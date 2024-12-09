from typing import Any, List  # noqa

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status  # noqa
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from api import deps
from services.translate import google_translate
from services.publish import publish_to_telegraph
from services.summarize import openai_summarize

from db.session import async_session

from utils.html_cleaner import clean_html

import crud, models, schemas  # noqa


router = APIRouter()


@router.get('/', response_model=schemas.SourceRows)
async def read_sources(
    db: AsyncSession = Depends(deps.get_db),
    filters: List[schemas.Filter] = Depends(deps.request_filters),
    orders: List[schemas.Order] = Depends(deps.request_orders),
    skip: int = 0,
    limit: int = 100,
    _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve sources.
    """
    sources = await crud.source.get_rows_by_user(
        db, filters=filters, orders=orders, skip=skip, limit=limit
    )
    count = await crud.source.get_count_by_user(db, filters=filters)
    return {'data': jsonable_encoder(sources), 'total': count}


@router.post(
    '/',
    response_model=schemas.Source,
    status_code=status.HTTP_201_CREATED
)
async def create_source(
    *,
    db: AsyncSession = Depends(deps.get_db),
    source_in: schemas.SourceCreate,
    _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new source.
    """
    source = await crud.source.create(db=db, obj_in=source_in)
    return source


@router.put('/{id}', response_model=schemas.Source)
async def update_source(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    source_in: schemas.SourceUpdate,
    _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an source.
    """
    source = await crud.source.get(db=db, id=id)
    if not source:
        raise HTTPException(status_code=404, detail='Source not found')
    source = await crud.source.update(db=db, db_obj=source, obj_in=source_in)
    return source


@router.get('/{id}', response_model=schemas.Source)
async def read_source(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get source by ID.
    """
    source = await crud.source.get(db=db, id=id)
    if not source:
        raise HTTPException(status_code=404, detail='Source not found')
    return source


@router.delete('/{id}', response_model=schemas.Source)
async def delete_source(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Delete an source.
    """
    source = await crud.source.get(db=db, id=id)
    if not source:
        raise HTTPException(status_code=404, detail='Source not found')
    source = await crud.source.delete(db=db, id=id)
    return source
