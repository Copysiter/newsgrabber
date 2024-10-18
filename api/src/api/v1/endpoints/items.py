from typing import Any, List  # noqa

from fastapi import APIRouter, Depends, HTTPException, status  # noqa
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from api import deps  # noqa

import crud, models, schemas  # noqa

router = APIRouter()


@router.get('/', response_model=schemas.ItemRows)
async def read_items(
    db: AsyncSession = Depends(deps.get_db),
    filters: List[schemas.Filter] = Depends(deps.request_filters),
    orders: List[schemas.Order] = Depends(deps.request_orders),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve items.
    """
    if crud.user.is_superuser(current_user):
        items = await crud.item.get_rows(db, skip=skip, limit=limit)
        count = await crud.item.get_count(db)
    else:
        items = await crud.item.get_rows_by_user(
            db, filters=filters, orders=orders,
            user_id=current_user.id, skip=skip, limit=limit
        )
        count = await crud.item.get_count_by_user(
            db, filters=filters, user_id=current_user.id
        )
    return {'data': jsonable_encoder(items), 'total': count}


@router.post(
    '/',
    response_model=schemas.Item,
    status_code=status.HTTP_201_CREATED
)
async def create_item(
    *,
    db: AsyncSession = Depends(deps.get_db),
    item_in: schemas.ItemCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new item.
    """
    item = await crud.item.create_with_user(
        db=db, obj_in=item_in, user_id=current_user.id
    )
    return item


@router.put('/{id}', response_model=schemas.Item)
async def update_item(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    item_in: schemas.ItemUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an item.
    """
    item = await crud.item.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail='Item not found')
    if not crud.user.is_superuser(current_user) and \
            (item.user_id != current_user.id):
        raise HTTPException(status_code=400, detail='Not enough permissions')
    item = await crud.item.update(db=db, db_obj=item, obj_in=item_in)
    return item


@router.get('/{id}', response_model=schemas.Item)
async def read_item(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get item by ID.
    """
    item = await crud.item.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail='Item not found')
    if not crud.user.is_superuser(current_user) and \
            (item.user_id != current_user.id):
        raise HTTPException(
            status_code=item.user_id, detail='Not enough permissions'
        )
    return item


@router.delete('/{id}', response_model=schemas.Item)
async def delete_item(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an item.
    """
    item = await crud.item.get(db=db, id=id)
    if not item:
        raise HTTPException(status_code=404, detail='Item not found')
    if not crud.user.is_superuser(current_user) and \
            (item.user_id != current_user.id):
        raise HTTPException(status_code=400, detail='Not enough permissions')
    item = await crud.item.delete(db=db, id=id)
    return item
