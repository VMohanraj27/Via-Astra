import mlflow
import os

# Use local file-based MLflow backend (no server needed)
MLFLOW_TRACKING_URI = "http://127.0.0.1:5000"


def configure_mlflow():
    """Initialize MLflow tracking configuration."""
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    mlflow.set_experiment("company-fit-agent")
    print(f"✅ MLflow initialized")
    print(f"   Tracking URI: {MLFLOW_TRACKING_URI}")
    print(f"   Experiment: company-fit-agent")