from typing import List, Dict
from fastapi import Request, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings  # noqa
from db.session import async_session  # noqa

import crud, models, schemas  # noqa

from utils.query_string import parse  # noqa

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f'{settings.API_VERSION_PREFIX}/auth/access-token'
)


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session


async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> models.User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (jwt.JWTError, ValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Could not validate credentials',
        )
    user = await crud.user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    return user


async def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not crud.user.is_active(current_user):
        raise HTTPException(status_code=400, detail='Inactive user')
    return current_user


async def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not crud.user.is_superuser(current_user):
        raise HTTPException(
            status_code=400, detail='The user doesn\'t have enough privileges'
        )
    return current_user


def query_params(
    request: Request
) -> Dict:
    params = parse(str(request.query_params), normalized=True)
    return params


def request_filters(
    params: Dict = Depends(query_params)
) -> List | Dict:
    return params.get('filters', [])


def request_orders(
    params: Dict = Depends(query_params)
) -> List:
    return params.get('orders', [])
