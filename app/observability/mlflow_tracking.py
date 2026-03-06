import mlflow
from app.config import MLFLOW_TRACKING_URI


mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
mlflow.set_experiment("company-fit-agent")