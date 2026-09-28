from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import (
    APP_NAME,
    STATIC_DIR,
    TEMPLATES_DIR,
)

from app.routes import router


# =========================================================
# CREATE DIRECTORIES
# =========================================================

Path(STATIC_DIR).mkdir(
    parents=True,
    exist_ok=True,
)

Path(TEMPLATES_DIR).mkdir(
    parents=True,
    exist_ok=True,
)


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title=APP_NAME,
    description="AI-powered comic generation application.",
)


# =========================================================
# STATIC FILES
# =========================================================

app.mount(
    "/static",
    StaticFiles(
        directory=str(STATIC_DIR)
    ),
    name="static",
)


# =========================================================
# REGISTER ROUTES
# =========================================================

app.include_router(router)


# =========================================================
# APP INFO
# =========================================================

@app.get("/app-info")
async def app_info():
    return {
        "name": APP_NAME,
        "status": "running",
    }


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )