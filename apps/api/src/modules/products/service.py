import uuid

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.integrations.storage import upload_fileobj
from src.models.product import Product, ProductVariation

logger = structlog.get_logger()


def _product_query():
    """Base product query that eagerly loads category and variations."""
    return (
        select(Product)
        .options(joinedload(Product.category))
        .options(selectinload(Product.variations))
    )


# --- Products ---


async def list_products(
    db: AsyncSession,
    merchant_id: str,
    category_id: str | None = None,
    only_available: bool = False,
    search: str | None = None,
) -> tuple[list[Product], int]:
    """List products for a merchant with optional filters."""
    query = _product_query().where(Product.merchant_id == merchant_id)

    if category_id:
        query = query.where(Product.category_id == category_id)

    if only_available:
        query = query.where(Product.is_available.is_(True))

    if search:
        query = query.where(Product.name.ilike(f"%{search}%"))

    query = query.order_by(Product.name)

    result = await db.execute(query)
    products = list(result.unique().scalars().all())

    total = len(products)
    return products, total


async def get_product(db: AsyncSession, product_id: str, merchant_id: str) -> Product | None:
    """Get a single product by id, scoped to merchant."""
    result = await db.execute(
        _product_query().where(
            Product.id == product_id,
            Product.merchant_id == merchant_id,
        )
    )
    return result.unique().scalar_one_or_none()


async def create_product(db: AsyncSession, merchant_id: str, data: dict) -> Product:
    """Create a new product."""
    product = Product(merchant_id=merchant_id, **data)
    db.add(product)
    await db.commit()
    await db.refresh(product)
    logger.info("product_created", merchant_id=merchant_id, product_id=str(product.id))
    return product


async def update_product(
    db: AsyncSession, product_id: str, merchant_id: str, data: dict
) -> Product | None:
    """Update a product."""
    product = await get_product(db, product_id, merchant_id)
    if not product:
        return None

    for field, value in data.items():
        if value is not None:
            setattr(product, field, value)

    await db.commit()
    await db.refresh(product)
    logger.info("product_updated", merchant_id=merchant_id, product_id=str(product.id))
    return product


async def delete_product(db: AsyncSession, product_id: str, merchant_id: str) -> bool:
    """Soft-delete a product (set is_available=False)."""
    product = await get_product(db, product_id, merchant_id)
    if not product:
        return False

    product.is_available = False
    await db.commit()
    logger.info("product_deactivated", merchant_id=merchant_id, product_id=str(product_id))
    return True


async def set_product_availability(
    db: AsyncSession, product_id: str, merchant_id: str, is_available: bool
) -> Product | None:
    """Set a product's availability (is_available)."""
    product = await get_product(db, product_id, merchant_id)
    if not product:
        return None

    product.is_available = is_available
    await db.commit()
    await db.refresh(product)
    logger.info(
        "product_availability_updated",
        merchant_id=merchant_id,
        product_id=product_id,
        is_available=is_available,
    )
    return product


async def upload_product_photo(
    db: AsyncSession,
    product_id: str,
    merchant_id: str,
    file_contents: bytes,
    content_type: str,
    filename: str,
) -> str | None:
    """Upload a photo for a product and update its image_url.

    Returns the new image URL, or None if the product was not found.
    """
    product = await get_product(db, product_id, merchant_id)
    if not product:
        return None

    # Generate a unique S3 key
    ext = filename.rsplit(".", 1)[-1] if "." in filename else "jpg"
    s3_key = f"products/{product_id}/{uuid.uuid4().hex}.{ext}"

    import io

    fileobj = io.BytesIO(file_contents)
    url = upload_fileobj(fileobj, key=s3_key, content_type=content_type)

    if url is None:
        logger.error("product_photo_upload_failed", product_id=product_id)
        return None

    product.image_url = url
    await db.commit()
    await db.refresh(product)
    logger.info("product_photo_uploaded", product_id=product_id, url=url)
    return url


# --- Variations ---


async def create_variation(
    db: AsyncSession, product_id: str, merchant_id: str, data: dict
) -> ProductVariation | None:
    """Create a new variation for a product. Validates product ownership."""
    product = await get_product(db, product_id, merchant_id)
    if not product:
        return None

    variation = ProductVariation(product_id=product_id, **data)

    if variation.is_default:
        # Clear other defaults
        await db.execute(
            select(ProductVariation).where(
                ProductVariation.product_id == product_id,
                ProductVariation.is_default.is_(True),
            )
        )

    db.add(variation)
    product.has_variations = True
    await db.commit()
    await db.refresh(variation)
    logger.info(
        "variation_created",
        product_id=str(product_id),
        variation_id=str(variation.id),
    )
    return variation


async def update_variation(
    db: AsyncSession,
    variation_id: str,
    product_id: str,
    merchant_id: str,
    data: dict,
) -> ProductVariation | None:
    """Update a variation. Validates product ownership."""
    product = await get_product(db, product_id, merchant_id)
    if not product:
        return None

    result = await db.execute(
        select(ProductVariation).where(
            ProductVariation.id == variation_id,
            ProductVariation.product_id == product_id,
        )
    )
    variation = result.scalar_one_or_none()
    if not variation:
        return None

    for field, value in data.items():
        if value is not None:
            setattr(variation, field, value)

    await db.commit()
    await db.refresh(variation)
    logger.info(
        "variation_updated",
        product_id=str(product_id),
        variation_id=str(variation_id),
    )
    return variation


async def delete_variation(
    db: AsyncSession, variation_id: str, product_id: str, merchant_id: str
) -> bool:
    """Delete a variation. Validates product ownership."""
    product = await get_product(db, product_id, merchant_id)
    if not product:
        return False

    result = await db.execute(
        select(ProductVariation).where(
            ProductVariation.id == variation_id,
            ProductVariation.product_id == product_id,
        )
    )
    variation = result.scalar_one_or_none()
    if not variation:
        return False

    await db.delete(variation)
    await db.commit()
    logger.info(
        "variation_deleted",
        product_id=str(product_id),
        variation_id=str(variation_id),
    )
    return True
