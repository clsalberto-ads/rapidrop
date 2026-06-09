import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.models.product import UnitType
from src.modules.auth.deps import extract_merchant_id, get_current_merchant
from src.modules.products.schemas import (
    ProductCreate,
    ProductListResponse,
    ProductResponse,
    ProductUpdate,
    VariationCreate,
    VariationResponse,
    VariationUpdate,
)
from src.modules.products.service import (
    create_product,
    create_variation,
    delete_product,
    delete_variation,
    get_product,
    list_products,
    update_product,
    update_variation,
)

logger = structlog.get_logger()
router = APIRouter(prefix="/api/v1/products", tags=["products"])


def _fmt_price(cents: int) -> str:
    return f"R$ {cents / 100:.2f}"


def _product_to_response(product) -> ProductResponse:
    cat = product.category if hasattr(product, "category") else None
    category_name = cat.name if cat else None
    variations = getattr(product, "variations_list", []) or []

    return ProductResponse(
        id=str(product.id),
        category_id=str(product.category_id) if product.category_id else None,
        category_name=category_name,
        name=product.name,
        description=product.description,
        price_cents=product.price_cents,
        price_formatted=_fmt_price(product.price_cents),
        image_url=product.image_url,
        barcode=product.barcode,
        unit_type=(
            product.unit_type.value
            if isinstance(product.unit_type, UnitType)
            else str(product.unit_type)
        ),
        is_available=product.is_available,
        has_variations=product.has_variations,
        stock_quantity=product.stock_quantity,
        stock_alert_at=product.stock_alert_at,
        variations=[
            {
                "id": str(v.id),
                "name": v.name,
                "price_cents_adjustment": v.price_cents_adjustment,
                "is_default": v.is_default,
            }
            for v in variations
        ],
        created_at=product.created_at,
        updated_at=product.updated_at,
    )


def _variation_to_response(variation) -> VariationResponse:
    return VariationResponse(
        id=str(variation.id),
        product_id=str(variation.product_id),
        name=variation.name,
        price_cents_adjustment=variation.price_cents_adjustment,
        is_default=variation.is_default,
        created_at=variation.created_at,
    )


# --- Product Endpoints ---


@router.get("", response_model=ProductListResponse)
async def list_products_endpoint(
    category_id: str | None = Query(default=None),
    only_available: bool = Query(default=False),
    search: str | None = Query(default=None),
    current_merchant: dict = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    """List products for the authenticated merchant."""
    merchant_id = extract_merchant_id(current_merchant)
    products, total = await list_products(
        db, merchant_id, category_id=category_id, only_available=only_available, search=search
    )

    return ProductListResponse(
        products=[_product_to_response(p) for p in products],
        total=total,
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product_endpoint(
    product_id: str,
    current_merchant: dict = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    """Get a single product by ID."""
    merchant_id = extract_merchant_id(current_merchant)
    product = await get_product(db, product_id, merchant_id)

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    return _product_to_response(product)


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product_endpoint(
    body: ProductCreate,
    current_merchant: dict = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    """Create a new product."""
    merchant_id = extract_merchant_id(current_merchant)
    product = await create_product(db, merchant_id, body.model_dump())
    return _product_to_response(product)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product_endpoint(
    product_id: str,
    body: ProductUpdate,
    current_merchant: dict = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    """Update a product."""
    merchant_id = extract_merchant_id(current_merchant)
    product = await update_product(db, product_id, merchant_id, body.model_dump(exclude_none=True))

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    return _product_to_response(product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_endpoint(
    product_id: str,
    current_merchant: dict = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete a product (set is_available=False)."""
    merchant_id = extract_merchant_id(current_merchant)
    deleted = await delete_product(db, product_id, merchant_id)

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")


# --- Variation Endpoints ---


@router.get("/{product_id}/variations", response_model=list[VariationResponse])
async def list_variations_endpoint(
    product_id: str,
    current_merchant: dict = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    """List all variations for a product."""
    merchant_id = extract_merchant_id(current_merchant)
    product = await get_product(db, product_id, merchant_id)

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    variations = getattr(product, "variations_list", [])
    return [_variation_to_response(v) for v in variations]


@router.post(
    "/{product_id}/variations",
    response_model=VariationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_variation_endpoint(
    product_id: str,
    body: VariationCreate,
    current_merchant: dict = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    """Create a new variation for a product."""
    merchant_id = extract_merchant_id(current_merchant)
    variation = await create_variation(db, product_id, merchant_id, body.model_dump())

    if not variation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    return _variation_to_response(variation)


@router.put(
    "/{product_id}/variations/{variation_id}",
    response_model=VariationResponse,
)
async def update_variation_endpoint(
    product_id: str,
    variation_id: str,
    body: VariationUpdate,
    current_merchant: dict = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    """Update a variation."""
    merchant_id = extract_merchant_id(current_merchant)
    variation = await update_variation(
        db, variation_id, product_id, merchant_id, body.model_dump(exclude_none=True)
    )

    if not variation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variation not found")

    return _variation_to_response(variation)


@router.delete("/{product_id}/variations/{variation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_variation_endpoint(
    product_id: str,
    variation_id: str,
    current_merchant: dict = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    """Delete a variation."""
    merchant_id = extract_merchant_id(current_merchant)
    deleted = await delete_variation(db, variation_id, product_id, merchant_id)

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variation not found")
