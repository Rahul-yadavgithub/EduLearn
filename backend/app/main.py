from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging

from app.core.cors import setup_cors
from app.core.database import connect_db, close_db

from app.routers import (
    auth,
    admin,
    papers,
    doubts,
    tests,
    notifications,
    ai,
    seed,
    progress,  
    generated_papers,
)

# -------------------------------------------------
# LOGGING
# -------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

# -------------------------------------------------
# LIFESPAN (DB INIT HERE)
# -------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    connect_db()          # ✅ runs before first request
    yield
    close_db()            # ✅ runs on shutdown

# -------------------------------------------------
# APP
# -------------------------------------------------
app = FastAPI(
    title="Education Platform API",
    lifespan=lifespan     # ✅ THIS IS IMPORTANT
)

# -------------------------------------------------
# CORS (BEFORE ROUTERS)
# -------------------------------------------------
setup_cors(app)

# -------------------------------------------------
# ROUTERS
# -------------------------------------------------
app.include_router(auth.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(papers.router, prefix="/api")
app.include_router(doubts.router, prefix="/api")
app.include_router(tests.router, prefix="/api")
app.include_router(notifications.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(seed.router, prefix="/api")
app.include_router(progress.router, prefix="/api")  # ✅ ADD THIS
app.include_router(generated_papers.router, prefix="/api") 



# -------------------------------------------------
# ROOT
# -------------------------------------------------
@app.get("/")
async def root():
    return {"message": "Education Platform API", "status": "running"}
