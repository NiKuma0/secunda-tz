import fastapi

from . import organizations

root_router = fastapi.APIRouter(prefix='/api/v1')

root_router.include_router(organizations.router, prefix='/organizations')
