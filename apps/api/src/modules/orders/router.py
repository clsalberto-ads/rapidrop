import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.modules.auth.deps import extract_merchant_id, get_current_merchant
from src.modules.orders.schemas import (
    OrderCreate,
    OrderItemResponse,
    OrderListResponse,
    OrderResponse,
    OrderUpdate,
)
from src.modules.orders.service import (
    create_order,
    get_order,
    list_orders,
    update_order,
    update_order_status,
)

logger = structlog.get_logger()
router = APIRouter(prefix="/api/v1/orders", tags=["orders"])


def _order_to_response(order) -> OrderResponse:
    return OrderResponse(
        id=str(order.id),
        sequential_id=order.sequential_id,
        customer_id=str(order.customer_id),
        rider_id=str(order.rider_id) if order.rider_id else None,
        channel=order.channel.value if hasattr(order.channel, "value") else str(order.channel),
        status=order.status.value if hasattr(order.status, "value") else str(order.status),
        items=[
            OrderItemResponse(
                id=str(item.id),
                product_id=str(item.product_id),
                product_name=item.product_name,
                product_variation=item.product_variation,
                quantity=item.quantity,
                unit_price_cents=item.unit_price_cents,
                total_cents=item.total_cents,
                special_notes=item.special_notes,
            )
            for item in (order.items or [])
        ],
        subtotal_cents=order.subtotal_cents,
        delivery_fee_cents=order.delivery_fee_cents,
        discount_cents=order.discount_cents,
        total_cents=order.total_cents,
        payment_method=order.payment_method,
        payment_status=order.payment_status.value if hasattr(order.payment_status, "value") else str(order.payment_status),
        customer_address=order.customer_address or {},
        customer_notes=order.customer_notes,
        confirmed_at=order.confirmed_at,
        preparing_at=order.preparing_at,
        ready_at=order.ready_at,
        out_for_delivery_at=order.out_for_delivery_at,
        delivered_at=order.delivered_at,
        cancelled_at=order.cancelled_at,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


@router.get("", response_model=OrderListResponse)
async def list_orders_endpoint(
    status: str | None = Query(default=None),
    payment_status: str | None = Query(default=None),
    search: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    current_merchant: dict = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    """List orders for the authenticated merchant."""
    merchant_id = extract_merchant_id(current_merchant)
    orders, total = await list_orders(
        db, merchant_id, status=status, payment_status=payment_status,
        search=search, limit=limit, offset=offset,
    )
    return OrderListResponse(
        orders=[_order_to_response(o) for o in orders],
        total=total,
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_endpoint(
    order_id: str,
    current_merchant: dict = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    """Get a single order by ID."""
    merchant_id = extract_merchant_id(current_merchant)
    order = await get_order(db, order_id, merchant_id)

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    return _order_to_response(order)


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order_endpoint(
    body: OrderCreate,
    current_merchant: dict = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    """Create a new order."""
    merchant_id = extract_merchant_id(current_merchant)
    order = await create_order(db, merchant_id, body.model_dump())
    return _order_to_response(order)


@router.patch("/{order_id}/status", response_model=OrderResponse)
async def update_order_status_endpoint(
    order_id: str,
    status_update: OrderUpdate,
    current_merchant: dict = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    """Update order status (auto-timestamps: confirmed_at, preparing_at, etc.)."""
    merchant_id = extract_merchant_id(current_merchant)

    if status_update.status:
        order = await update_order_status(db, order_id, merchant_id, status_update.status)
    else:
        order = await update_order(
            db, order_id, merchant_id, status_update.model_dump(exclude_none=True)
        )

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    return _order_to_response(order)
