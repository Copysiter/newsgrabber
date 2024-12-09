from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from telegraph import Telegraph

from api import deps

import models



router = APIRouter()


@router.get('/new_token')
async def read_config(
    short_name: str,
    _: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new Telegraph.
    """
    telegraph = Telegraph()
    token = telegraph.create_account(short_name=short_name)
    return token
