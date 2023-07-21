from fastapi import FastAPI

from .routers.payments import router

app = FastAPI(
    title="Personal Finance API - PFA",
    version="0.0.1",
)
app.include_router(router)
