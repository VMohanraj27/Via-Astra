from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="Company Fit Assessment Agent")

app.include_router(router)