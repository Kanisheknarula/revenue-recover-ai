from fastapi import FastAPI

from backend.config import APP_NAME, APP_VERSION
from backend.routes import router

app = FastAPI(title=APP_NAME, version=APP_VERSION)

app.include_router(router)