from typing import List

from pydantic import BaseModel, Field


# =========================================================
# PANEL OUTLINE
# =========================================================

class PanelOutline(BaseModel):
    panel_number: int = Field(
        ...,
        ge=1,
    )

    title: str

    scene_description: str

    image_prompt: str


# =========================================================
# COMPLETE COMIC PANEL
# =========================================================

class ComicPanel(BaseModel):
    panel_number: int = Field(
        ...,
        ge=1,
    )

    title: str

    narration: str = ""

    dialogue: str = ""

    scene_description: str

    image_prompt: str

    image_url: str = ""


class StoryPanel(BaseModel):
    panel_number: int = Field(
        ...,
        ge=1,
    )

    title: str

    scene_description: str

    image_prompt: str

    caption: str = ""

    narration: str = ""

    dialogue: str = ""


# =========================================================
# COMIC GENERATION REQUEST
# =========================================================

class ComicGenerationRequest(BaseModel):

    prompt: str

    character: str = (
        "A young adventurous protagonist"
    )

    setting: str = (
        "A mysterious fantasy world"
    )

    tone: str = (
        "Adventurous and emotional"
    )

    art_style: str = (
        "Cinematic graphic novel"
    )

    panels: int = Field(
        default=5,
        ge=1,
        le=12,
    )

    title: str = "My AI Comic"


# =========================================================
# COMIC GENERATION RESPONSE
# =========================================================

class ComicGenerationResponse(BaseModel):

    success: bool

    message: str

    title: str

    panels: List[ComicPanel]


# =========================================================
# EXPORT RESPONSE
# =========================================================

class ExportResponse(BaseModel):

    success: bool

    message: str

    pdf_url: str = ""

