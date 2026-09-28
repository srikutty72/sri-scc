import os
from pathlib import Path

from dotenv import load_dotenv


# =========================================================
# PROJECT ROOT
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# =========================================================
# PROJECT DIRECTORIES
# =========================================================

APP_DIR = BASE_DIR / "app"

TEMPLATES_DIR = BASE_DIR / "templates"

STATIC_DIR = BASE_DIR / "static"

PANELS_DIR = STATIC_DIR / "panels"

EXPORTS_DIR = STATIC_DIR / "exports"


# =========================================================
# LOAD .ENV FILE
# =========================================================

ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)


# =========================================================
# APPLICATION SETTINGS
# =========================================================

APP_NAME = os.getenv(
    "APP_NAME",
    "ComicCraft AI"
)

APP_VERSION = os.getenv(
    "APP_VERSION",
    "1.0.0"
)

DEBUG = os.getenv(
    "DEBUG",
    "true"
).lower() == "true"


# =========================================================
# GEMINI API
# =========================================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY",
    ""
).strip()


GEMINI_FLASH_MODEL = os.getenv(
    "GEMINI_FLASH_MODEL",
    "gemini-3.8-flash"
).strip()


GEMINI_PRO_MODEL = os.getenv(
    "GEMINI_PRO_MODEL",
    "gemini-3.1-pro-preview"
).strip()


# =========================================================
# HUGGING FACE API
# =========================================================

HF_API_KEY = os.getenv(
    "HF_API_KEY",
    ""
).strip()


HF_IMAGE_MODEL = os.getenv(
    "HF_IMAGE_MODEL",
    "stabilityai/stable-diffusion-xl-base-1.0"
).strip()


# =========================================================
# DEMO MODE
# =========================================================

DEMO_MODE = os.getenv(
    "DEMO_MODE",
    "true"
).strip().lower() in {
    "true",
    "1",
    "yes",
    "y",
    "on",
}


# =========================================================
# SERVER SETTINGS
# =========================================================

HOST = os.getenv(
    "HOST",
    "127.0.0.1"
)


PORT = int(
    os.getenv(
        "PORT",
        "8000"
    )
)


# =========================================================
# COMIC SETTINGS
# =========================================================

DEFAULT_PANELS = int(
    os.getenv(
        "DEFAULT_PANELS",
        "5"
    )
)


MIN_PANELS = int(
    os.getenv(
        "MIN_PANELS",
        "1"
    )
)


MAX_PANELS = int(
    os.getenv(
        "MAX_PANELS",
        "12"
    )
)


# =========================================================
# IMAGE SETTINGS
# =========================================================

IMAGE_WIDTH = int(
    os.getenv(
        "IMAGE_WIDTH",
        "1024"
    )
)


IMAGE_HEIGHT = int(
    os.getenv(
        "IMAGE_HEIGHT",
        "1024"
    )
)


# =========================================================
# API TIMEOUT
# =========================================================

API_TIMEOUT = int(
    os.getenv(
        "API_TIMEOUT",
        "180"
    )
)


# =========================================================
# CREATE REQUIRED DIRECTORIES
# =========================================================

TEMPLATES_DIR.mkdir(
    parents=True,
    exist_ok=True
)


STATIC_DIR.mkdir(
    parents=True,
    exist_ok=True
)


PANELS_DIR.mkdir(
    parents=True,
    exist_ok=True
)


EXPORTS_DIR.mkdir(
    parents=True,
    exist_ok=True
)

