import json
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from app.config import (
    APP_NAME,
    APP_VERSION,
    DEFAULT_PANELS,
    MAX_PANELS,
    MIN_PANELS,
    TEMPLATES_DIR,
    DEMO_MODE,
)

from app.image_generator import generate_image
from app.gemini_flash import generate_outline
from app.gemini_pro import generate_story


# =========================================================
# ROUTER
# =========================================================

router = APIRouter()


# =========================================================
# TEMPLATES
# =========================================================

templates = Jinja2Templates(
    directory=str(TEMPLATES_DIR)
)


# =========================================================
# TEMPORARY STORAGE
# =========================================================

GENERATED_COMICS = {}


# =========================================================
# HELPERS
# =========================================================

def _clean_text(
    value: Any,
    default: str = ""
) -> str:
    if value is None:
        return default
    return str(value).strip()


def _safe_panel_count(value: Any) -> int:
    try:
        count = int(value)
    except (TypeError, ValueError):
        count = DEFAULT_PANELS

    return max(
        MIN_PANELS,
        min(MAX_PANELS, count)
    )


def _extract_json(text: str) -> dict:
    if not text:
        raise ValueError(
            "AI returned an empty response."
        )

    cleaned = text.strip()

    # Remove markdown code fences
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        cleaned = "\n".join(lines).strip()

    # Try direct JSON
    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass

    # Try extracting JSON object
    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start != -1 and end != -1 and end > start:
        possible_json = cleaned[start:end + 1]
        try:
            data = json.loads(possible_json)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass

    raise ValueError(
        "Could not parse the AI response as JSON."
    )


# =========================================================
# DEMO STORY
# =========================================================

def _demo_story(
    title: str,
    idea: str,
    character: str,
    setting: str,
    tone: str,
    style: str,
    panel_count: int,
) -> dict:

    if not character:
        character = "Maya"

    if not setting:
        setting = "an ancient magical library"

    if not tone:
        tone = "adventure"

    if not style:
        style = "cinematic comic book"

    if not title:
        title = "The Magical Book"

    if not idea:
        idea = (
            f"{character} discovers something mysterious "
            f"inside {setting}."
        )

    events = [
        (
            "The Discovery",
            f"{character} enters {setting} and notices "
            "a mysterious glowing book hidden on an old shelf.",
            f"{character}: What is that strange light?",
        ),
        (
            "The Awakening",
            f"{character} carefully opens the book. "
            "The pages begin to glow and strange symbols "
            "appear in the air.",
            f"{character}: This book is alive!",
        ),
        (
            "The Secret World",
            f"A magical doorway opens from the pages, "
            "revealing an incredible world beyond "
            f"{setting}.",
            f"{character}: I have never seen anything like this.",
        ),
        (
            "The Guardian",
            f"{character} meets a mysterious guardian who "
            "warns that the book has chosen its new keeper.",
            "Guardian: The real adventure begins now.",
        ),
        (
            "The Beginning",
            f"{character} steps toward the magical doorway, "
            "ready to discover the secret behind the book.",
            f"{character}: Then let's find out the truth.",
        ),
        (
            "The Hidden Path",
            f"{character} discovers a hidden path leading "
            "deeper into the magical world.",
            f"{character}: There must be something important ahead.",
        ),
        (
            "The Challenge",
            f"{character} faces the first mysterious challenge "
            "and realizes the journey will not be easy.",
            f"{character}: I won't turn back now.",
        ),
        (
            "The Mystery",
            f"{character} finds another clue connected to "
            "the strange book.",
            f"{character}: So this was the secret all along.",
        ),
        (
            "The Choice",
            f"{character} must decide whether to continue "
            "the dangerous magical journey.",
            f"{character}: I know what I have to do.",
        ),
        (
            "The New Adventure",
            f"{character} walks into the unknown as the "
            "magical world opens before them.",
            f"{character}: This is only the beginning.",
        ),
        (
            "The Final Clue",
            f"{character} discovers the final clue that may "
            "explain the origin of the magical book.",
            f"{character}: Everything finally makes sense.",
        ),
        (
            "The New Chapter",
            f"{character} closes the magical book for a moment, "
            "knowing that a new chapter is about to begin.",
            f"{character}: Tomorrow, the real journey starts.",
        ),
    ]

    panels = []

    for index in range(panel_count):
        event = events[index % len(events)]
        panel_title = event[0]
        scene = event[1]
        dialogue = event[2]

        image_prompt = (
            f"{style}, {tone}, professional comic book panel, "
            f"high quality cinematic illustration. "
            f"Main character: {character}. "
            f"Location: {setting}. "
            f"Story: {scene}. "
            f"Panel {index + 1} of {panel_count}. "
            "Strong composition, expressive character, "
            "dramatic lighting, detailed environment, "
            "consistent character appearance, "
            "no watermark, no logo, no readable text."
        )

        panels.append({
            "panel_number": index + 1,
            "title": panel_title,
            "scene": scene,
            "narration": scene,
            "dialogue": dialogue,
            "image_prompt": image_prompt,
            "image_url": None,
            "image_error": None,
        })

    return {
        "title": title,
        "logline": idea,
        "character": character,
        "setting": setting,
        "tone": tone,
        "style": style,
        "panels": panels,
    }


# =========================================================
# GEMINI PROMPT
# =========================================================

def _build_story_prompt(
    title: str,
    idea: str,
    character: str,
    setting: str,
    tone: str,
    style: str,
    panel_count: int,
) -> str:

    return f"""
You are the lead writer for a professional AI comic-book
generator called ComicCraft.

Create a complete original comic story.

USER INPUT
==========

Title: {title}
Story idea: {idea}
Main character: {character}
Setting: {setting}
Tone: {tone}
Art style: {style}
Number of panels: {panel_count}

IMPORTANT REQUIREMENTS

1. Create exactly {panel_count} panels.
2. Story must progress naturally.
3. Every panel must contain a different action.
4. Do not repeat the same scene.
5. Keep the same main character.
6. Maintain consistent character appearance.
7. Each panel must contain:
   - panel_number
   - title
   - scene
   - narration
   - dialogue
   - image_prompt
8. image_prompt must describe only the visual scene.
9. Do not put dialogue inside image_prompt.
10. Include character appearance, clothing,
    environment, action, emotion, camera angle,
    lighting and comic art style.
11. Keep the story suitable for a general audience.
12. Give the story a satisfying ending or cliffhanger.
13. Return ONLY valid JSON.

JSON FORMAT

{{
    "title": "Comic title",
    "logline": "One sentence summary",
    "character": "Detailed character description",
    "setting": "Detailed setting description",
    "tone": "Story tone",
    "style": "Visual style",
    "panels": [
        {{
            "panel_number": 1,
            "title": "Panel title",
            "scene": "What happens",
            "narration": "Narration",
            "dialogue": "Dialogue",
            "image_prompt": "Detailed visual prompt"
        }}
    ]
}}
""".strip()


# =========================================================
# GEMINI STORY GENERATION
# =========================================================

def _generate_story_with_gemini(
    title: str,
    idea: str,
    character: str,
    setting: str,
    tone: str,
    style: str,
    panel_count: int,
) -> dict:

    outline = generate_outline(
        prompt=idea,
        character=character,
        setting=setting,
        tone=tone,
        art_style=style,
        panels=panel_count,
    )

    panels = generate_story(
        outline=outline,
        character=character,
        tone=tone,
    )

    return {
        "title": title,
        "logline": idea,
        "character": character,
        "setting": setting,
        "tone": tone,
        "style": style,
        "panels": [
            {
                "panel_number": panel.panel_number,
                "title": panel.title,
                "scene": panel.scene_description,
                "narration": panel.narration,
                "dialogue": panel.dialogue,
                "image_prompt": panel.image_prompt,
            }
            for panel in panels
        ],
    }


# =========================================================
# NORMALIZE STORY
# =========================================================

def _normalize_story(
    story: dict,
    panel_count: int,
    title: str,
    idea: str,
    character: str,
    setting: str,
    tone: str,
    style: str,
) -> dict:

    if not isinstance(story, dict):
        raise ValueError(
            "Story result is not a JSON object."
        )

    panels = story.get("panels", [])

    if not isinstance(panels, list):
        panels = []

    normalized = []

    for index, panel in enumerate(panels):
        if not isinstance(panel, dict):
            continue

        number = index + 1

        normalized.append({
            "panel_number": number,
            "title": _clean_text(
                panel.get("title"),
                f"Panel {number}",
            ),
            "scene": _clean_text(
                panel.get("scene"),
                "The story continues.",
            ),
            "narration": _clean_text(
                panel.get("narration") or panel.get("scene"),
                "The story continues.",
            ),
            "dialogue": _clean_text(
                panel.get("dialogue"),
                "",
            ),
            "image_prompt": _clean_text(
                panel.get("image_prompt"),
                panel.get("scene"),
            ),
            "image_url": None,
            "image_error": None,
        })

    # Fill missing panels
    if len(normalized) < panel_count:
        fallback = _demo_story(
            title=title,
            idea=idea,
            character=character,
            setting=setting,
            tone=tone,
            style=style,
            panel_count=panel_count,
        )

        existing = len(normalized)
        normalized.extend(
            fallback["panels"][existing:panel_count]
        )

    normalized = normalized[:panel_count]

    return {
        "title": _clean_text(
            story.get("title"),
            title,
        ),
        "logline": _clean_text(
            story.get("logline"),
            idea,
        ),
        "character": _clean_text(
            story.get("character"),
            character,
        ),
        "setting": _clean_text(
            story.get("setting"),
            setting,
        ),
        "tone": _clean_text(
            story.get("tone"),
            tone,
        ),
        "style": _clean_text(
            story.get("style"),
            style,
        ),
        "panels": normalized,
    }


# =========================================================
# IMAGE GENERATION
# =========================================================

def _generate_panel_images(
    story: dict
) -> dict:

    panels = story.get("panels", [])

    for panel in panels:
        panel_number = panel["panel_number"]

        prompt = panel.get(
            "image_prompt",
            panel.get("scene", "")
        )

        character = story.get("character", "")
        setting = story.get("setting", "")
        style = story.get("style", "comic book")

        final_prompt = (
            f"{style}. "
            f"Main character consistency: {character}. "
            f"Setting: {setting}. "
            f"Scene: {prompt}. "
            "Professional comic illustration, "
            "cinematic composition, expressive face, "
            "detailed environment, dynamic lighting, "
            "high quality, clean line art, "
            "no watermark, no logo, no text."
        )

        try:
            image_url = generate_image(
                prompt=final_prompt,
                panel_number=panel_number,
            )
            panel["image_url"] = image_url
            panel["image_error"] = None
        except Exception as exc:
            panel["image_url"] = None
            panel["image_error"] = str(exc)

    return story


# =========================================================
# HOME PAGE
# =========================================================

@router.get(
    "/",
    response_class=HTMLResponse,
)
async def home(
    request: Request,
):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": APP_NAME,
            "app_version": APP_VERSION,
            "default_panels": DEFAULT_PANELS,
            "min_panels": MIN_PANELS,
            "max_panels": MAX_PANELS,
        },
    )


# =========================================================
# HEALTH
# =========================================================

@router.get("/health")
async def health():
    return {
        "status": "ok",
        "app": APP_NAME,
        "version": APP_VERSION,
        "demo_mode": DEMO_MODE,
        "image_generation": not DEMO_MODE,
    }


# =========================================================
# TEST IMAGE
# =========================================================

@router.get("/test-image")
async def test_image():
    try:
        image_url = generate_image(
            prompt=(
                "A cinematic comic book illustration "
                "of a young adventurer standing inside "
                "a mysterious ancient library, magical "
                "blue light, dramatic atmosphere, "
                "detailed environment."
            ),
            panel_number=1,
        )

        return {
            "success": True,
            "image_url": image_url,
        }
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(exc),
            },
        )


# =========================================================
# GENERATE COMIC
# =========================================================

@router.post(
    "/generate",
    response_class=HTMLResponse,
)
async def generate_comic(
    request: Request,
):
    try:
        content_type = (
            request.headers
            .get("content-type", "")
            .lower()
        )

        if "application/json" in content_type:
            data = await request.json()
        else:
            form = await request.form()
            data = dict(form)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=(
                "Could not read the request: "
                f"{exc}"
            ),
        )

    # INPUTS
    title = _clean_text(data.get("title"), "The Magical Book")
    idea = _clean_text(
        data.get("story") or data.get("story_idea") or data.get("prompt"),
        "A mysterious adventure begins.",
    )
    character = _clean_text(data.get("character"), "Maya")
    setting = _clean_text(data.get("setting"), "an ancient magical library")
    tone = _clean_text(data.get("tone"), "adventure")
    style = _clean_text(
        data.get("style") or data.get("art_style"),
        "cinematic comic book",
    )
    panel_count = _safe_panel_count(
        data.get("panels", data.get("panel_count", DEFAULT_PANELS))
    )

    # STORY
    if DEMO_MODE:
        story = _demo_story(
            title=title,
            idea=idea,
            character=character,
            setting=setting,
            tone=tone,
            style=style,
            panel_count=panel_count,
        )
    else:
        try:
            raw_story = _generate_story_with_gemini(
                title=title,
                idea=idea,
                character=character,
                setting=setting,
                tone=tone,
                style=style,
                panel_count=panel_count,
            )
            story = _normalize_story(
                story=raw_story,
                panel_count=panel_count,
                title=title,
                idea=idea,
                character=character,
                setting=setting,
                tone=tone,
                style=style,
            )
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Story generation failed: {exc}",
            )

    # IMAGES
    story = _generate_panel_images(story)

    # GENERATION ID
    generation_id = uuid.uuid4().hex[:12]
    story["generation_id"] = generation_id
    story["image_count"] = sum(1 for panel in story["panels"] if panel.get("image_url"))
    story["failed_images"] = sum(1 for panel in story["panels"] if panel.get("image_error"))

    # SAVE IN MEMORY
    GENERATED_COMICS[generation_id] = story

    return templates.TemplateResponse(
        request=request,
        name="comic_preview.html",
        context={
            "comic": story,
            "app_name": APP_NAME,
            "app_version": APP_VERSION,
        },
    )


# =========================================================
# COMIC PREVIEW
# =========================================================

@router.get(
    "/preview/{generation_id}",
    response_class=HTMLResponse,
)
async def comic_preview(
    request: Request,
    generation_id: str,
):
    comic = GENERATED_COMICS.get(generation_id)

    if comic is None:
        raise HTTPException(
            status_code=404,
            detail="Comic generation not found."
        )

    return templates.TemplateResponse(
        request=request,
        name="comic_preview.html",
        context={
            "comic": comic,
            "app_name": APP_NAME,
            "app_version": APP_VERSION,
        },
    )


# =========================================================
# JSON API
# =========================================================

@router.get(
    "/api/comic/{generation_id}"
)
async def get_comic(
    generation_id: str,
):
    comic = GENERATED_COMICS.get(generation_id)

    if comic is None:
        raise HTTPException(
            status_code=404,
            detail="Comic generation not found."
        )

    return {
        "success": True,
        "comic": comic,
    }


# =========================================================
# ABOUT
# =========================================================

@router.get(
    "/api/about"
)
async def about():
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "description": "AI-powered comic story and panel generator.",
    }


# =========================================================
# EXPORT PAGE
# =========================================================

@router.get(
    "/export",
    response_class=HTMLResponse,
)
async def export_page(
    request: Request,
    generation_id: str = None,
):
    comic = GENERATED_COMICS.get(generation_id) if generation_id else None

    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "comic": comic,
            "app_name": APP_NAME,
            "app_version": APP_VERSION,
        },
    )