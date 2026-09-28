import re
import uuid
import urllib.parse
from pathlib import Path

from PIL import Image, ImageDraw
from huggingface_hub import InferenceClient

from app.config import (
    HF_API_KEY,
    HF_IMAGE_MODEL,
    PANELS_DIR,
)


# =========================================================
# SAFE FILE NAME
# =========================================================

def _safe_name(text: str) -> str:
    cleaned = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        text,
    )

    cleaned = cleaned.strip("_")

    return cleaned[:60] or "panel"


# =========================================================
# DEMO IMAGE
# =========================================================

def _demo_image(
    prompt: str,
    output_path: Path,
    panel_number: int,
) -> None:

    width = 1024
    height = 1024

    image = Image.new(
        "RGB",
        (width, height),
        "white",
    )

    draw = ImageDraw.Draw(image)

    draw.rectangle(
        (20, 20, width - 20, height - 20),
        outline="black",
        width=8,
    )

    draw.text(
        (60, 70),
        f"COMICCRAFT - PANEL {panel_number}",
        fill="black",
    )

    draw.text(
        (60, 140),
        "DEMO IMAGE",
        fill="black",
    )

    words = prompt.split()

    lines = []
    current_line = ""

    for word in words:

        test_line = (
            f"{current_line} {word}"
        ).strip()

        if len(test_line) > 70:

            if current_line:
                lines.append(current_line)

            current_line = word

        else:
            current_line = test_line

    if current_line:
        lines.append(current_line)

    y = 220

    for line in lines[:25]:

        draw.text(
            (60, y),
            line,
            fill="black",
        )

        y += 30

    image.save(
        output_path,
        format="PNG",
    )


# =========================================================
# HUGGING FACE IMAGE GENERATION
# =========================================================

def _generate_huggingface_image(
    prompt: str,
    output_path: Path,
):

    if not HF_API_KEY:
        raise RuntimeError(
            "HF_API_KEY is missing."
        )

    if not HF_IMAGE_MODEL:
        raise RuntimeError(
            "HF_IMAGE_MODEL is missing."
        )

    print("Generating image with Hugging Face...")
    print(f"Model: {HF_IMAGE_MODEL}")

    client = InferenceClient(
        provider="auto",
        api_key=HF_API_KEY,
    )

    negative_prompt = (
        "blurry, low quality, distorted face, "
        "deformed body, extra fingers, bad anatomy, "
        "duplicate character, cropped, watermark, "
        "logo, unreadable text"
    )

    image = client.text_to_image(
        prompt=prompt,
        model=HF_IMAGE_MODEL,
        negative_prompt=negative_prompt,
    )

    if image is None:
        raise RuntimeError(
            "Hugging Face returned an empty image."
        )

    image = image.convert("RGB")

    image.save(
        output_path,
        format="PNG",
    )

    print(
        f"Hugging Face image saved: {output_path}"
    )


# =========================================================
# POLLINATIONS FALLBACK
# =========================================================

def _pollinations_url(
    prompt: str,
    panel_number: int,
) -> str:

    encoded_prompt = urllib.parse.quote(
        prompt,
        safe="",
    )

    seed = panel_number * 42

    return (
        "https://image.pollinations.ai/prompt/"
        f"{encoded_prompt}"
        f"?width=1024"
        f"&height=1024"
        f"&nologo=true"
        f"&seed={seed}"
    )


# =========================================================
# MAIN IMAGE GENERATOR
# =========================================================

def generate_image(
    prompt: str,
    panel_number: int,
) -> str:

    # -----------------------------------------------------
    # CREATE OUTPUT DIRECTORY
    # -----------------------------------------------------

    PANELS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # -----------------------------------------------------
    # FILE NAME
    # -----------------------------------------------------

    unique_id = uuid.uuid4().hex[:8]

    filename = (
        f"panel_{panel_number}_{unique_id}.png"
    )

    output_path = PANELS_DIR / filename

    # -----------------------------------------------------
    # IMPORTANT
    #
    # DEMO_MODE IS NOT USED HERE.
    #
    # DEMO_MODE=true only means:
    # "Don't use Gemini for story generation."
    #
    # Images will STILL try Hugging Face.
    # -----------------------------------------------------

    # =====================================================
    # 1. HUGGING FACE REAL IMAGE
    # =====================================================

    try:

        _generate_huggingface_image(
            prompt=prompt,
            output_path=output_path,
        )

        return (
            f"/static/panels/{filename}"
        )

    except Exception as exc:

        print(
            "Hugging Face image generation failed:"
        )

        print(exc)

        print(
            "Trying Pollinations fallback..."
        )

    # =====================================================
    # 2. POLLINATIONS FALLBACK
    # =====================================================

    try:

        fallback_url = _pollinations_url(
            prompt=prompt,
            panel_number=panel_number,
        )

        print(
            "Using Pollinations fallback image."
        )

        return fallback_url

    except Exception as exc:

        print(
            "Pollinations fallback failed:"
        )

        print(exc)

    # =====================================================
    # 3. LAST RESORT DEMO IMAGE
    # =====================================================

    print(
        "Creating local demo image as final fallback."
    )

    _demo_image(
        prompt=prompt,
        output_path=output_path,
        panel_number=panel_number,
    )

    return (
        f"/static/panels/{filename}"
    )
    