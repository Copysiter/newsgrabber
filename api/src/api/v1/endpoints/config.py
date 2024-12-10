import os

from dotenv import set_key
from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Body

from core.config import Settings, settings
from api import deps

import models, schemas


router = APIRouter()


@router.get('/', response_model=settings)
async def read_config(
    _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Retrieve settings.
    """
    return settings.dict()


@router.put('/', response_model=settings)
async def update_config(
    key: str = Body(), value: str = Body(),
    _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Update an settings.
    """
    env_file = Settings.Config.env_file
    if not os.path.exists(env_file):
        raise HTTPException(status_code=400, detail="File .env not found")
    set_key(env_file, key.upper(), value.replace('\n', '\\n'), quote_mode='never')

    global settings
    settings = Settings()

    return settings.dict()
