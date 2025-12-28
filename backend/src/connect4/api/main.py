import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import mlflow
import torch

from connect4.ml.agent.dqn_agent import DQNAgent
from connect4.game.engine_wrapper import Connect4Env
from connect4.api.endpoints import game


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    # Load the trained DQN agent model from MLflow on application startup.
    # The model is stored in app.state to be accessible across the application.
    
    run_id = os.environ.get("MLFLOW_RUN_ID")

    loaded_state_dict = None
    if run_id:
        print(f"Loading model from MLflow run: {run_id}")
        try:
            model_uri = f"runs:/{run_id}/model"
            # MLflow loads the entire model object, we need its state_dict
            loaded_model_object = mlflow.pytorch.load_model(model_uri)
            loaded_state_dict = loaded_model_object.state_dict()
        except mlflow.exceptions.MlflowException as e:
            print(f"Warning: Could not load model from MLflow: {e}")
    
    if not loaded_state_dict:
        model_path = "models/dqn_agent.pth"
        print(f"Attempting to load model from local path: {model_path}")
        if os.path.exists(model_path):
            # torch.load with a state_dict file already returns the dictionary
            loaded_state_dict = torch.load(model_path, map_location="cpu")
        else:
            print("Warning: No MLFLOW_RUN_ID set and no local model found.")
            print("API will start with a new, untrained agent (dev mode).")

    # We still need an agent structure
    env = Connect4Env()
    agent = DQNAgent(
        state_shape=env.state_shape,
        actions_num=env.actions_num,
        device="cpu", # Assume CPU for inference server
    )
    
    if loaded_state_dict:
        agent.model.load_state_dict(loaded_state_dict)
        print("Successfully loaded model weights into agent.")
    
    agent.model.eval()
    app.state.agent = agent
    
    yield
    # --- Shutdown ---
    print("Application is shutting down.")


app = FastAPI(
    title="Connect4 AI API",
    description="An API to play Connect4 against a trained DQN agent.",
    version="1.0.0",
    lifespan=lifespan,
)

# --- Middleware ---
# Configure CORS to allow frontend to communicate with this backend.
# Origins are read from an environment variable for flexibility.
CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Routers ---
app.include_router(game.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "Welcome to the Connect4 API. Visit /docs for documentation."}

