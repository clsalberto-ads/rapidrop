import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.category import ProductCategory
from src.models.product import Product

logger = structlog.get_logger()


async def list_categories(
    db: AsyncSession,
    merchant_id: str,
    only_active: bool = False,
) -> tuple[list[ProductCategory], int]:
    """List categories for a merchant, ordered by sort_order."""
    query = select(ProductCategory).where(ProductCategory.merchant_id == merchant_id)

    if only_active:
        query = query.where(ProductCategory.is_active.is_(True))

    query = query.order_by(ProductCategory.sort_order, ProductCategory.name)

    result = await db.execute(query)
    categories = list(result.scalars().all())

    # Count products per category
    count_query = (
        select(ProductCategory.id, func.count(Product.id).label("count"))
        .select_from(ProductCategory)
        .outerjoin(Product, Product.category_id == ProductCategory.id)
        .where(ProductCategory.merchant_id == merchant_id)
        .group_by(ProductCategory.id)
    )
    count_result = await db.execute(count_query)
    counts = {row[0]: row[1] for row in count_result}

    total = len(categories)
    # Attach product counts
    for cat in categories:
        cat.product_count = counts.get(cat.id, 0)

    return categories, total


async def get_category(
    db: AsyncSession, category_id: str, merchant_id: str
) -> ProductCategory | None:
    """Get a single category by id, scoped to merchant."""
    result = await db.execute(
        select(ProductCategory).where(
            ProductCategory.id == category_id,
            ProductCategory.merchant_id == merchant_id,
        )
    )
    return result.scalar_one_or_none()


async def create_category(
    db: AsyncSession,
    merchant_id: str,
    data: dict,
) -> ProductCategory:
    """Create a new category for the merchant."""
    category = ProductCategory(merchant_id=merchant_id, **data)
    db.add(category)
    await db.commit()
    await db.refresh(category)
    logger.info("category_created", merchant_id=merchant_id, category_id=str(category.id))
    return category


async def update_category(
    db: AsyncSession,
    category_id: str,
    merchant_id: str,
    data: dict,
) -> ProductCategory | None:
    """Update a category, scoped to merchant."""
    category = await get_category(db, category_id, merchant_id)
    if not category:
        return None

    for field, value in data.items():
        if value is not None:
            setattr(category, field, value)

    await db.commit()
    await db.refresh(category)
    logger.info("category_updated", merchant_id=merchant_id, category_id=str(category.id))
    return category


async def delete_category(
    db: AsyncSession,
    category_id: str,
    merchant_id: str,
) -> bool:
    """Soft-delete a category (set is_active=False)."""
    category = await get_category(db, category_id, merchant_id)
    if not category:
        return False

    category.is_active = False
    await db.commit()
    logger.info("category_deactivated", merchant_id=merchant_id, category_id=str(category.id))
    return True
