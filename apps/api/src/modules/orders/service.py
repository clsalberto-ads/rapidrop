from datetime import UTC, datetime

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.models.order import Order, OrderItem, OrderStatus

logger = structlog.get_logger()


def _order_query():
    """Base order query that eagerly loads items."""
    return select(Order).options(joinedload(Order.items))


async def list_orders(
    db: AsyncSession,
    merchant_id: str,
    status: str | None = None,
    payment_status: str | None = None,
    search: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[Order], int]:
    """List orders for a merchant with optional filters."""
    query = _order_query().where(Order.merchant_id == merchant_id)

    if status:
        query = query.where(Order.status == status)

    if payment_status:
        query = query.where(Order.payment_status == payment_status)

    if search:
        query = query.where(
            Order.id.ilike(f"%{search}%")
            | Order.customer_id.ilike(f"%{search}%")
        )

    # Count total before pagination
    count_query = select(func.count()).select_from(Order).where(Order.merchant_id == merchant_id)
    if status:
        count_query = count_query.where(Order.status == status)
    if payment_status:
        count_query = count_query.where(Order.payment_status == payment_status)
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(Order.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(query)
    orders = list(result.unique().scalars().all())
    return orders, total


async def get_order(db: AsyncSession, order_id: str, merchant_id: str) -> Order | None:
    """Get a single order by id, scoped to merchant."""
    result = await db.execute(
        _order_query().where(
            Order.id == order_id,
            Order.merchant_id == merchant_id,
        )
    )
    return result.unique().scalar_one_or_none()


async def get_next_sequential_id(db: AsyncSession, merchant_id: str) -> int:
    """Get the next sequential order number for a merchant."""
    result = await db.execute(
        select(func.coalesce(func.max(Order.sequential_id), 0)).where(
            Order.merchant_id == merchant_id
        )
    )
    return (result.scalar() or 0) + 1


async def create_order(db: AsyncSession, merchant_id: str, data: dict) -> Order:
    """Create a new order with items."""
    sequential_id = await get_next_sequential_id(db, merchant_id)
    items_data = data.pop("items", [])

    order = Order(
        merchant_id=merchant_id,
        sequential_id=sequential_id,
        **data,
    )

    for item_data in items_data:
        item = OrderItem(**item_data)
        order.items.append(item)

    db.add(order)
    await db.commit()
    await db.refresh(order)
    logger.info(
        "order_created",
        merchant_id=merchant_id,
        order_id=str(order.id),
        sequential_id=sequential_id,
    )
    return order


async def update_order_status(
    db: AsyncSession, order_id: str, merchant_id: str, status: str
) -> Order | None:
    """Update order status with automatic timestamp tracking."""
    order = await get_order(db, order_id, merchant_id)
    if not order:
        return None

    now = datetime.now(UTC)
    order.status = status

    timestamp_map = {
        OrderStatus.confirmed.value: "confirmed_at",
        OrderStatus.preparing.value: "preparing_at",
        OrderStatus.ready.value: "ready_at",
        OrderStatus.out_for_delivery.value: "out_for_delivery_at",
        OrderStatus.delivered.value: "delivered_at",
        OrderStatus.cancelled.value: "cancelled_at",
    }

    timestamp_field = timestamp_map.get(status)
    if timestamp_field and not getattr(order, timestamp_field):
        setattr(order, timestamp_field, now)

    await db.commit()
    await db.refresh(order)
    logger.info(
        "order_status_updated",
        merchant_id=merchant_id,
        order_id=str(order_id),
        status=status,
    )
    return order


async def update_order(
    db: AsyncSession, order_id: str, merchant_id: str, data: dict
) -> Order | None:
    """Update an order."""
    order = await get_order(db, order_id, merchant_id)
    if not order:
        return None

    for field, value in data.items():
        if value is not None:
            setattr(order, field, value)

    await db.commit()
    await db.refresh(order)
    logger.info("order_updated", merchant_id=merchant_id, order_id=str(order_id))
    return order
