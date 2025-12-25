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
# APP
# -------------------------------------------------
app = FastAPI(title="Education Platform API")

# -------------------------------------------------
# CORS (MUST BE BEFORE ROUTERS)
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

# -------------------------------------------------
# ROOT
# -------------------------------------------------
@app.get("/")
async def root():
    return {"message": "Education Platform API", "status": "running"}

# -------------------------------------------------
# STARTUP / SHUTDOWN
# -------------------------------------------------
@app.on_event("startup")
async def startup():
    connect_db()   # ✅ correct


@app.on_event("shutdown")
async def shutdown():
    close_db()
