from fastapi import FastAPI
from app.api.routes import router
from app.observability.mlflow_tracking import configure_mlflow

# Initialize MLflow configuration on startup
configure_mlflow()

app = FastAPI(title="Company Fit Assessment Agent")

app.include_router(router)