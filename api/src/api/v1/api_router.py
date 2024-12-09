from fastapi import APIRouter

from .endpoints import base, config, auth, users, sources, items, utils, scrapyd, telegraph  # noqa


api_router = APIRouter()

# api_router.include_router(base.router, prefix='', tags=['Info'])
# api_router.include_router(utils.router, prefix='/utils', tags=['Utils'])
api_router.include_router(config.router, prefix='/settings', tags=['Settings'])
api_router.include_router(auth.router, prefix='/auth', tags=['Auth'])
api_router.include_router(users.router, prefix='/users', tags=['Users'])
api_router.include_router(sources.router, prefix='/sources', tags=['Sources'])
api_router.include_router(items.router, prefix='/items', tags=['Items'])
api_router.include_router(scrapyd.router, prefix='/scrapyd', tags=['Scrapyd'])
api_router.include_router(telegraph.router, prefix='/telegraph', tags=['Telegraph'])
