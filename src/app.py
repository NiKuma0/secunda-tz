import fastapi

from src.routers import root_router

app = fastapi.FastAPI()

app.include_router(root_router)
