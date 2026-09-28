import json
from typing import List

from google import genai
from google.genai import types

from app.config import (
    GEMINI_API_KEY,
    GEMINI_PRO_MODEL,
    DEMO_MODE
)

from app.schemas import (
    PanelOutline,
    StoryPanel
)


# =========================================================
# DEMO STORY GENERATOR
# =========================================================

def _demo_story(
    outline: List[PanelOutline],
    character: str,
    tone: str
) -> List[StoryPanel]:
    """
    Creates a sample comic story when DEMO_MODE is enabled.

    This allows the complete ComicCraft application
    to be tested without a Gemini API key.
    """

    result = []

    for panel in outline:

        # -------------------------------------------------
        # CAPTION
        # -------------------------------------------------

        caption = (
            f"{character} looks around carefully."
        )

        # -------------------------------------------------
        # NARRATION
        # -------------------------------------------------

        narration = (
            f"The moment feels {tone}. "
            f"{character} moves forward, "
            "determined to discover what happens next."
        )

        # -------------------------------------------------
        # DIALOGUE
        # -------------------------------------------------

        dialogue = (
            f'{character}: '
            '"I have a feeling this is only the beginning!"'
        )

        result.append(

            StoryPanel(

                panel_number=panel.panel_number,

                title=panel.title,

                scene_description=(
                    panel.scene_description
                ),

                image_prompt=(
                    panel.image_prompt
                ),

                caption=caption,

                narration=narration,

                dialogue=dialogue

            )
        )

    return result


# =========================================================
# GEMINI PRO STORY GENERATOR
# =========================================================

def generate_story(
    outline: List[PanelOutline],
    character: str,
    tone: str
) -> List[StoryPanel]:
    """
    Expand the comic outline into a complete story
    using Gemini Pro.

    Each panel contains:

    - panel_number
    - title
    - scene_description
    - image_prompt
    - caption
    - narration
    - dialogue
    """

    # =====================================================
    # DEMO MODE
    # =====================================================

    if DEMO_MODE:

        return _demo_story(

            outline=outline,

            character=character,

            tone=tone

        )

    # =====================================================
    # CHECK API KEY
    # =====================================================

    if not GEMINI_API_KEY:

        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Please add your Gemini API key "
            "inside the .env file or set "
            "DEMO_MODE=true."
        )

    # =====================================================
    # CREATE GEMINI CLIENT
    # =====================================================

    client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    # =====================================================
    # CONVERT OUTLINE TO JSON
    # =====================================================

    outline_data = [

        panel.model_dump()

        for panel in outline

    ]

    outline_json = json.dumps(

        outline_data,

        ensure_ascii=False,

        indent=2

    )

    # =====================================================
    # CREATE STORY PROMPT
    # =====================================================

    instruction = f"""
You are an expert comic book writer.

Expand the following comic outline into a
complete and engaging panel-by-panel comic story.

MAIN CHARACTER:
{character}

STORY TONE:
{tone}

COMIC OUTLINE:

{outline_json}

Return ONLY valid JSON.

The JSON must be an array.

Each item must contain exactly these fields:

panel_number
title
scene_description
image_prompt
caption
narration
dialogue

IMPORTANT REQUIREMENTS:

1. Keep the same main character throughout the story.

2. Do not change the main character's identity.

3. Keep the story consistent with the supplied outline.

4. Keep the setting and events consistent.

5. Each panel must continue naturally from the previous panel.

6. Caption should be short and suitable for a comic panel.

7. Narration should explain the important story action.

8. Dialogue should sound natural.

9. Dialogue should be short enough to fit inside a comic speech bubble.

10. Keep the requested tone.

11. Do not add unnecessary characters.

12. Do not rewrite the entire story in one panel.

13. Make the final panel feel like a proper ending.

14. Keep image_prompt visually detailed.

15. Image prompts should be suitable for an AI image generator.

16. Do not include Markdown.

17. Do not include explanations outside the JSON.

Example structure:

[
    {{
        "panel_number": 1,
        "title": "The Beginning",
        "scene_description": "Description of the scene",
        "image_prompt": "Detailed visual prompt",
        "caption": "Short caption",
        "narration": "Story narration",
        "dialogue": "Character: Short dialogue"
    }}
]
"""

    # =====================================================
    # CALL GEMINI PRO
    # =====================================================

    try:

        response = client.models.generate_content(

            model=GEMINI_PRO_MODEL,

            contents=instruction,

            config=types.GenerateContentConfig(

                temperature=0.85,

                response_mime_type="application/json"

            )

        )

    except Exception as exc:

        raise RuntimeError(
            "Gemini Pro API request failed: "
            f"{exc}"
        ) from exc

    # =====================================================
    # CHECK RESPONSE
    # =====================================================

    if not response:

        raise RuntimeError(
            "Gemini Pro returned an empty response."
        )

    response_text = getattr(
        response,
        "text",
        None
    )

    if not response_text:

        raise RuntimeError(
            "Gemini Pro returned no text response."
        )

    # =====================================================
    # PARSE JSON
    # =====================================================

    try:

        data = json.loads(
            response_text
        )

    except json.JSONDecodeError as exc:

        raise RuntimeError(
            "Gemini Pro returned invalid JSON. "
            f"Response received: {response_text[:500]}"
        ) from exc

    # =====================================================
    # HANDLE OBJECT RESPONSE
    # =====================================================

    if isinstance(data, dict):

        data = data.get(

            "panels",

            data.get(
                "story",
                []
            )

        )

    # =====================================================
    # VALIDATE RESPONSE TYPE
    # =====================================================

    if not isinstance(data, list):

        raise RuntimeError(
            "Gemini Pro response must contain "
            "a list of comic panels."
        )

    # =====================================================
    # VALIDATE EACH PANEL
    # =====================================================

    try:

        result = [

            StoryPanel.model_validate(
                item
            )

            for item in data

        ]

    except Exception as exc:

        raise RuntimeError(
            "Gemini Pro returned panels "
            "with an unexpected structure: "
            f"{exc}"
        ) from exc

    # =====================================================
    # CHECK PANEL COUNT
    # =====================================================

    if len(result) != len(outline):

        raise RuntimeError(
            f"Gemini Pro returned "
            f"{len(result)} panels, "
            f"but the outline contains "
            f"{len(outline)} panels."
        )

    # =====================================================
    # RETURN STORY
    # =====================================================

    return result