import json
import time
from typing import List

from google import genai
from google.genai import types

from app.config import (
    GEMINI_API_KEY,
    GEMINI_FLASH_MODEL,
    GEMINI_PRO_MODEL,
    DEMO_MODE,
)

from app.schemas import PanelOutline


# =========================================================
# DEMO OUTLINE
# =========================================================

def _demo_outline(
    prompt: str,
    character: str,
    setting: str,
    tone: str,
    art_style: str,
    panels: int,
) -> List[PanelOutline]:

    result = []

    story_beats = [
        (
            "The Beginning",
            f"{character} arrives at {setting} and discovers "
            f"something unexpected related to: {prompt}."
        ),
        (
            "The Mystery",
            f"{character} investigates the strange situation "
            f"and discovers an important clue."
        ),
        (
            "The Conflict",
            f"{character} faces the main challenge and must "
            f"make an important decision."
        ),
        (
            "The Turning Point",
            f"{character} takes action and begins to overcome "
            f"the conflict."
        ),
        (
            "The Resolution",
            f"{character} successfully resolves the situation "
            f"and begins a new chapter."
        ),
    ]

    for i in range(1, panels + 1):

        if panels <= len(story_beats):
            title, scene = story_beats[i - 1]

        else:

            if i == 1:
                title, scene = story_beats[0]

            elif i == panels:
                title, scene = story_beats[-1]

            else:
                title = f"Turning Point {i}"

                scene = (
                    f"{character} continues the journey through "
                    f"{setting}. The situation becomes increasingly "
                    f"{tone.lower()}."
                )

        image_prompt = _build_image_prompt(
            character=character,
            setting=setting,
            scene=scene,
            art_style=art_style,
            panel_number=i,
        )

        result.append(
            PanelOutline(
                panel_number=i,
                title=title,
                scene_description=scene,
                image_prompt=image_prompt,
            )
        )

    return result


# =========================================================
# IMAGE PROMPT BUILDER
# =========================================================

def _build_image_prompt(
    character: str,
    setting: str,
    scene: str,
    art_style: str,
    panel_number: int,
) -> str:

    return (
        f"Professional {art_style} comic illustration. "
        f"Comic panel {panel_number}. "
        f"Main character: {character}. "
        f"Location: {setting}. "
        f"Scene: {scene}. "
        "Keep the character's appearance consistent with previous panels. "
        "Clear facial expression and body pose. "
        "Strong foreground, middle ground and background separation. "
        "Detailed environment. "
        "Dynamic cinematic composition. "
        "Professional comic-book lighting. "
        "Expressive storytelling. "
        "Clean line art. "
        "Rich visual details. "
        "High-quality digital illustration. "
        "No text, no captions, no speech bubbles, no watermark, no logo."
    )


# =========================================================
# CREATE GEMINI CLIENT
# =========================================================

def _create_client():

    if not GEMINI_API_KEY:

        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Add your Gemini API key to the .env file."
        )

    return genai.Client(
        api_key=GEMINI_API_KEY
    )


# =========================================================
# BUILD STORY INSTRUCTION
# =========================================================

def _build_instruction(
    prompt: str,
    character: str,
    setting: str,
    tone: str,
    art_style: str,
    panels: int,
) -> str:

    return f"""
You are a professional comic-book story director and
visual storytelling planner.

Create a complete {panels}-panel comic outline.

USER STORY IDEA:
{prompt}

MAIN CHARACTER:
{character}

SETTING:
{setting}

TONE:
{tone}

VISUAL STYLE:
{art_style}

Your job is to transform the simple story idea into a
coherent visual comic.

STORY STRUCTURE:

Panel 1:
Introduce the main character, environment and situation.

Middle panels:
Develop the story naturally.
Introduce a problem, discovery, conflict or obstacle.

Second-to-last panel:
Create the major turning point or climax.

Final panel:
Resolve the main story and provide a satisfying ending.

CHARACTER CONSISTENCY:

- The same main character must appear in every relevant panel.
- Do not randomly change the character.
- Do not change the character's age.
- Do not change the character's role.
- Keep clothing and visual identity consistent.
- Keep the environment logically consistent.

VISUAL STORYTELLING:

Every panel must show a clearly different moment.
Avoid repeating the same composition.
Use different camera angles where appropriate.
Show emotions through facial expressions and body language.
Describe important objects that should appear in the scene.

IMAGE PROMPTS:

Each image_prompt must be detailed enough for an
AI image-generation model to create the panel.

Image prompts must include:

- character
- location
- action
- emotion
- important objects
- composition
- lighting
- art style

Do NOT put dialogue or written text inside image_prompt.

OUTPUT FORMAT:

Return ONLY valid JSON.

Return an array containing exactly {panels} objects.

Each object MUST contain:

panel_number
title
scene_description
image_prompt

The panel_number must start at 1 and increase sequentially.

Do not use Markdown.
Do not use ```json.
Do not add explanations.
"""


# =========================================================
# CALL GEMINI
# =========================================================

def _call_gemini(
    client,
    model: str,
    instruction: str,
):

    response = client.models.generate_content(

        model=model,

        contents=instruction,

        config=types.GenerateContentConfig(

            temperature=0.75,

            response_mime_type="application/json",

        ),
    )

    return response


# =========================================================
# PARSE RESPONSE
# =========================================================

def _parse_response(
    response,
    panels: int,
) -> List[PanelOutline]:

    if response is None:

        raise RuntimeError(
            "Gemini returned an empty response."
        )

    response_text = getattr(
        response,
        "text",
        None,
    )

    if not response_text:

        raise RuntimeError(
            "Gemini returned no text response."
        )

    response_text = response_text.strip()

    # Remove accidental Markdown fences
    if response_text.startswith("```"):

        response_text = (
            response_text
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

    # Parse JSON
    try:

        data = json.loads(
            response_text
        )

    except json.JSONDecodeError as exc:

        raise RuntimeError(
            "Gemini returned invalid JSON.\n\n"
            f"Response:\n{response_text[:1000]}"
        ) from exc

    if isinstance(data, dict):

        data = data.get(
            "panels",
            data.get(
                "outline",
                [],
            ),
        )

    if not isinstance(data, list):

        raise RuntimeError(
            "Gemini response does not contain "
            "a valid panel list."
        )

    if len(data) != panels:

        raise RuntimeError(
            f"Gemini returned {len(data)} panels, "
            f"but {panels} panels were requested."
        )

    result = []

    for index, item in enumerate(data, start=1):

        if not isinstance(item, dict):

            raise RuntimeError(
                f"Panel {index} is not a valid object."
            )

        item["panel_number"] = index

        item.setdefault(
            "title",
            f"Panel {index}",
        )

        item.setdefault(
            "scene_description",
            "Comic scene.",
        )

        item.setdefault(
            "image_prompt",
            "Professional comic illustration.",
        )

        try:

            panel = PanelOutline.model_validate(
                item
            )

        except Exception as exc:

            raise RuntimeError(
                f"Panel {index} has an invalid structure: "
                f"{exc}"
            ) from exc

        result.append(panel)

    return result


# =========================================================
# MAIN OUTLINE GENERATOR
# =========================================================

def generate_outline(
    prompt: str,
    character: str,
    setting: str,
    tone: str,
    art_style: str,
    panels: int = 5,
) -> List[PanelOutline]:

    # DEMO MODE
    if DEMO_MODE:

        print("ComicCraft: DEMO_MODE is enabled.")

        return _demo_outline(
            prompt=prompt,
            character=character,
            setting=setting,
            tone=tone,
            art_style=art_style,
            panels=panels,
        )

    # VALIDATION
    if not prompt.strip():

        raise ValueError(
            "Story prompt cannot be empty."
        )

    if panels < 1 or panels > 12:

        raise ValueError(
            "Panels must be between 1 and 12."
        )

    # Gemini Call முயற்சிக்கப்படுகிறது
    try:

        client = _create_client()

        instruction = _build_instruction(
            prompt=prompt,
            character=character,
            setting=setting,
            tone=tone,
            art_style=art_style,
            panels=panels,
        )

        max_retries = 2
        response = None

        for attempt in range(1, max_retries + 1):
            try:
                print(f"Gemini Flash request {attempt}/{max_retries}")
                response = _call_gemini(
                    client=client,
                    model=GEMINI_FLASH_MODEL or "gemini-1.5-flash",
                    instruction=instruction,
                )
                break
            except Exception as exc:
                print(f"Gemini Attempt {attempt} failed: {exc}")
                if attempt < max_retries:
                    time.sleep(2)

        if response is not None:
            return _parse_response(response=response, panels=panels)

    except Exception as exc:
        print(f"Gemini API Error: {exc}. Switching to local Fallback Outline...")

    # =====================================================
    # FALLBACK: Gemini எர்ரர் வந்தால் தானாகக் கதை உருவாக்கப்படும்
    # =====================================================

    print("Generating local fallback outline...")
    return _demo_outline(
        prompt=prompt,
        character=character,
        setting=setting,
        tone=tone,
        art_style=art_style,
        panels=panels,
    )