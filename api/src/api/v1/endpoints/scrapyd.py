import logging

import aiohttp

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status  # noqa
from sqlalchemy.ext.asyncio import AsyncSession
from scrapyd_api import ScrapydAPI

from api import deps  # noqa

import schemas, crud


SCRAPYD_URL = "http://scrapyd:6800"
scrapyd = ScrapydAPI(SCRAPYD_URL)

router = APIRouter()


@router.post("/schedule/")
async def schedule_task(
    *,
    db: AsyncSession = Depends(deps.get_db),
    chat_id: int = None,
    url: str,
    domain: str = Depends(deps.get_domain),
    source:schemas.source = Depends(deps.get_source)
) -> Any:
    import logging
    logging.info(source)
    if not source:
        allowed_domains = [
            source.domain for source in \
            await crud.source.get_rows(db, limit=None)
        ]
        detail = \
            f'⚠️ Домен {domain} не поддерживается.\n\n' \
            f'Введите ссылку на статью с одного из сайтов: ' \
            f'{", ".join(allowed_domains)}.'
        raise HTTPException(status_code=422, detail=detail)
    item = await crud.item.get_by_url(db=db, url=url)
    if item:
        # raise HTTPException(status_code=400, detail="URL already exists")
        return {'job_id': item.job_id}

    _ = await crud.item.create(
        db=db, obj_in={
            'chat_id': chat_id,
            'source_id': source.id,
            'url': url,
            'status': schemas.Status.NEW
        }
    )

    result = scrapyd.schedule(
        'default', source.spider_name, url=url
    )
    status = result.get('status')

    if status == 'ok':
        return {'job_id': result.get('jobid')}

    raise HTTPException(
        status_code=422,
        detail=f'Scrapy spider with name \'{source.spider_name}\' not found'
    )


@router.get("/status/{job_id}")
async def get_status(
    *,
    db: AsyncSession = Depends(deps.get_db),
    job_id: str
) -> schemas.Item:
    item = await crud.item.get_by_job_id(db=db, job_id=job_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return item


@router.get("/webhook/{item_id}")
async def webhook(
    *,
    db: AsyncSession = Depends(deps.get_db),
    item_id: int
) -> schemas.Item:
    item = await crud.item.get(db=db, id=item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    TELEGRAM_BOT_TOKEN = '7867011321:AAFBqqhYRmb4ZE_H1hvIGiXPb_XTWYXOdFY'
    TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    text = (f'<b>{item.title}</b>\n\n'
            f'<a href="{item.telegraph_url}">'
            f'{item.telegraph_url}'
            '</a>')
    keyboard = {
        'inline_keyboard': [
            [
                {'text': '🇷🇺 Перевод статьи', 'callback_data': f'get_translate:{item.id}'},
                {'text': '📝️ Саммари статьи', 'callback_data': f'get_summary:{item.id}'}
            ]
        ]
    }
    payload = {
        'chat_id': item.chat_id,
        'text': text,
        'parse_mode': 'HTML',
        'reply_markup': keyboard
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(TELEGRAM_API_URL, json=payload) as response:
            if response.status == 200:
                logging.info(response)
            else:
                logging.wraning(response)
    return item
