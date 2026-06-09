import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.modules.auth.deps import extract_merchant_id, get_current_merchant
from src.modules.categories.schemas import (
    CategoryCreate,
    CategoryListResponse,
    CategoryResponse,
    CategoryUpdate,
)
from src.modules.categories.service import (
    create_category,
    delete_category,
    get_category,
    list_categories,
    update_category,
)

logger = structlog.get_logger()
router = APIRouter(prefix="/api/v1/categories", tags=["categories"])


def _category_to_response(cat, product_count: int = 0) -> CategoryResponse:
    return CategoryResponse(
        id=str(cat.id),
        name=cat.name,
        sort_order=cat.sort_order,
        is_active=cat.is_active,
        product_count=product_count,
        created_at=cat.created_at,
    )


@router.get("", response_model=CategoryListResponse)
async def list_categories_endpoint(
    only_active: bool = Query(default=False),
    current_merchant: dict = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    """List all categories for the authenticated merchant."""
    merchant_id = extract_merchant_id(current_merchant)
    categories, total = await list_categories(db, merchant_id, only_active=only_active)

    return CategoryListResponse(
        categories=[_category_to_response(c, getattr(c, "product_count", 0)) for c in categories],
        total=total,
    )


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category_endpoint(
    category_id: str,
    current_merchant: dict = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    """Get a single category by ID."""
    merchant_id = extract_merchant_id(current_merchant)
    category = await get_category(db, category_id, merchant_id)

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    return _category_to_response(category)


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category_endpoint(
    body: CategoryCreate,
    current_merchant: dict = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    """Create a new category."""
    merchant_id = extract_merchant_id(current_merchant)
    category = await create_category(db, merchant_id, body.model_dump())
    return _category_to_response(category)


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category_endpoint(
    category_id: str,
    body: CategoryUpdate,
    current_merchant: dict = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    """Update a category."""
    merchant_id = extract_merchant_id(current_merchant)
    data = body.model_dump(exclude_none=True)
    category = await update_category(db, category_id, merchant_id, data)

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    return _category_to_response(category)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category_endpoint(
    category_id: str,
    current_merchant: dict = Depends(get_current_merchant),
    db: AsyncSession = Depends(get_db),
):
    """Soft-delete a category (deactivate it)."""
    merchant_id = extract_merchant_id(current_merchant)
    deleted = await delete_category(db, category_id, merchant_id)

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
