from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from app.core.config import CORS_ORIGINS

def setup_cors(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
