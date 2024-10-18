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
    request: schemas.ScrapydRequest
) -> Any:
    item = await crud.item.get_by_url(db=db, url=request.url)
    if item:
        # raise HTTPException(status_code=400, detail="URL already exists")
        return {'job_id': item.job_id}

    _ = await crud.item.create(
        db=db, obj_in={
            'url': request.url,
            'status': schemas.Status.NEW
        }
    )

    result = scrapyd.schedule(
        'default', request.spider_name, url=request.url
    )
    status = result.get('status')

    if status == 'ok':
        return {'job_id': result.get('jobid')}

    raise HTTPException(
        status_code=422,
        detail=f'Scrapy spider with name \'{request.spider_name}\' not found'
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
