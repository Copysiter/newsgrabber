import asyncio
import aiohttp
import logging

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


async def translate_item(item_id: int):
    """
    Background task to translate and update an item.
    """
    async with async_session() as db:
        item = await crud.item.get(db=db, id=item_id)
        if not item:
            return

        if not item.title_ru:
            item.title_ru = await asyncio.to_thread(
                google_translate, item.title
            )
        if not item.html_ru:
            item.html_ru = await asyncio.to_thread(
                google_translate, item.html
            )
        if not item.text_ru:
            item.text_ru = clean_html(item.html_ru)
        if not item.telegraph_url_ru:
            item.telegraph_url_ru = await asyncio.to_thread(
                publish_to_telegraph,
                item.title_ru, item.html_ru, item.url
            )
        db.add(item)
        await db.commit()

        TELEGRAM_BOT_TOKEN = '7867011321:AAFBqqhYRmb4ZE_H1hvIGiXPb_XTWYXOdFY'
        TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'

        text = (f'<b>{item.title_ru}</b>\n\n'
                f'{item.telegraph_url_ru}')
        payload = {
            'chat_id': item.chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(TELEGRAM_API_URL,
                                   json=payload) as response:
                if response.status == 200:
                    logging.info(response)
                else:
                    logging.wraning(response)


async def summarize_item(item_id: int):
    """
    Background task to translate and update an item.
    """
    async with async_session() as db:
        item = await crud.item.get(db=db, id=item_id)
        if not item:
            return

        # if item.text and not item.summary:
        #     item.summary = openai_summarize(item.title, item.text)
        source_name = item.source.name
        title = item.title_ru or item.title
        text = item.text_ru or item.text
        if text and not item.summary_ru:
            item.summary_ru = await openai_summarize(
                source_name, title, text
            )
        db.add(item)
        await db.commit()

        TELEGRAM_BOT_TOKEN = '7867011321:AAFBqqhYRmb4ZE_H1hvIGiXPb_XTWYXOdFY'
        TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'

        text = (f'<b>{item.title_ru or item.title}</b>\n\n'
                f'{item.summary_ru}')
        payload = {
            'chat_id': item.chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(TELEGRAM_API_URL,
                                   json=payload) as response:
                if response.status == 200:
                    logging.info(response)
                else:
                    logging.wraning(response)


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


@router.get('/{id}/get', response_model=schemas.Item)
async def get_item(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int
) -> Any:
    """
    Get item by ID.
    """
    item = await crud.item.get(db=db, id=id)
    return item


@router.get('/{id}/translate', response_model=schemas.Item)
async def translate(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    background_tasks: BackgroundTasks
) -> Any:
    """
    Translate an item.
    """
    item = await crud.item.get(db=db, id=id)
    if not item:
        raise HTTPException(
            status_code=404, detail='Item not found'
        )
    background_tasks.add_task(translate_item, item.id)
    return item


@router.get('/{id}/summarize', response_model=schemas.Item)
async def summarize(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    background_tasks: BackgroundTasks
) -> Any:
    """
    Summarize an item.
    """
    item = await crud.item.get(db=db, id=id)
    if not item:
        raise HTTPException(
            status_code=404, detail='Item not found'
        )
    background_tasks.add_task(summarize_item, item.id)
    return item