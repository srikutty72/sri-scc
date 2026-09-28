from pathlib import Path
from datetime import datetime

from fpdf import FPDF
from PIL import Image

from app.config import EXPORTS_DIR, STATIC_DIR


def _get_local_image_path(image_url: str) -> Path:
    """
    Convert a browser URL such as:

        /static/panels/panel_1.png

    into the actual local file path.
    """

    if image_url.startswith("/static/"):
        relative_path = image_url[len("/static/"):]
    else:
        relative_path = image_url

    return STATIC_DIR / relative_path


def save_pdf(
    layout,
    title: str = "ComicCraft Comic"
) -> str:
    """
    Create a PDF containing all generated comic panels.

    Parameters
    ----------
    layout:
        List of comic panel dictionaries.

    title:
        Title of the comic.

    Returns
    -------
    str
        Browser-accessible URL of the generated PDF.
    """

    # Create a unique filename
    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    filename = (
        f"comiccraft_{timestamp}.pdf"
    )

    output_path = EXPORTS_DIR / filename

    # Create PDF
    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4"
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=15
    )

    # --------------------------------------------------
    # TITLE PAGE
    # --------------------------------------------------

    pdf.add_page()

    pdf.set_font(
        "Helvetica",
        "B",
        24
    )

    pdf.multi_cell(
        pdf.epw,
        12,
        title,
        align="C"
    )

    pdf.ln(10)

    pdf.set_font(
        "Helvetica",
        "",
        12
    )

    pdf.multi_cell(
        pdf.epw,
        8,
        "Created with ComicCraft AI",
        align="C"
    )

    # --------------------------------------------------
    # COMIC PANELS
    # --------------------------------------------------

    for panel in layout:

        pdf.add_page()

        # Panel number and title
        panel_number = panel.get(
            "panel_number",
            ""
        )

        panel_title = panel.get(
            "title",
            "Untitled Panel"
        )

        pdf.set_font(
            "Helvetica",
            "B",
            18
        )

        pdf.multi_cell(
            pdf.epw,
            10,
            f"Panel {panel_number}: {panel_title}"
        )

        pdf.ln(3)

        # --------------------------------------------------
        # IMAGE
        # --------------------------------------------------

        image_url = panel.get(
            "image_path",
            ""
        )

        image_path = _get_local_image_path(
            image_url
        )

        if image_path.exists():

            try:

                with Image.open(
                    image_path
                ) as image:

                    image_width, image_height = (
                        image.size
                    )

                # A4 printable area
                max_width = 180
                max_height = 105

                width_ratio = (
                    max_width / image_width
                )

                height_ratio = (
                    max_height / image_height
                )

                scale = min(
                    width_ratio,
                    height_ratio
                )

                display_width = (
                    image_width * scale
                )

                display_height = (
                    image_height * scale
                )

                # Center image
                page_width = 210

                x_position = (
                    page_width -
                    display_width
                ) / 2

                pdf.image(
                    str(image_path),
                    x=x_position,
                    w=display_width,
                    h=display_height
                )

            except Exception:

                pdf.set_font(
                    "Helvetica",
                    "I",
                    11
                )

                pdf.multi_cell(
                    pdf.epw,
                    7,
                    "Unable to load panel image."
                )

        else:

            pdf.set_font(
                "Helvetica",
                "I",
                11
            )

            pdf.multi_cell(
                pdf.epw,
                7,
                "Panel image is not available."
            )

        # Reset the text cursor after a centered image.
        pdf.set_xy(
            pdf.l_margin,
            pdf.get_y() + 6
        )

        # --------------------------------------------------
        # SCENE DESCRIPTION
        # --------------------------------------------------

        scene_description = panel.get(
            "scene_description",
            ""
        )

        if scene_description:

            pdf.set_font(
                "Helvetica",
                "B",
                11
            )

            pdf.multi_cell(
                pdf.epw,
                7,
                "Scene"
            )

            pdf.set_font(
                "Helvetica",
                "",
                11
            )

            pdf.multi_cell(
                pdf.epw,
                7,
                scene_description
            )

            pdf.ln(3)

        # --------------------------------------------------
        # CAPTION
        # --------------------------------------------------

        caption = panel.get(
            "caption",
            ""
        )

        if caption:

            pdf.set_font(
                "Helvetica",
                "B",
                11
            )

            pdf.multi_cell(
                pdf.epw,
                7,
                "Caption"
            )

            pdf.set_font(
                "Helvetica",
                "",
                11
            )

            pdf.multi_cell(
                pdf.epw,
                7,
                caption
            )

            pdf.ln(3)

        # --------------------------------------------------
        # NARRATION
        # --------------------------------------------------

        narration = panel.get(
            "narration",
            ""
        )

        if narration:

            pdf.set_font(
                "Helvetica",
                "B",
                11
            )

            pdf.multi_cell(
                pdf.epw,
                7,
                "Narration"
            )

            pdf.set_font(
                "Helvetica",
                "",
                11
            )

            pdf.multi_cell(
                pdf.epw,
                7,
                narration
            )

            pdf.ln(3)

        # --------------------------------------------------
        # DIALOGUE
        # --------------------------------------------------

        dialogue = panel.get(
            "dialogue",
            ""
        )

        if dialogue:

            pdf.set_font(
                "Helvetica",
                "B",
                11
            )

            pdf.multi_cell(
                pdf.epw,
                7,
                "Dialogue"
            )

            pdf.set_font(
                "Helvetica",
                "",
                11
            )

            pdf.multi_cell(
                pdf.epw,
                7,
                dialogue

            )

    # --------------------------------------------------
    # SAVE PDF
    # --------------------------------------------------

    pdf.output(
        str(output_path)
    )

    # Return URL that FastAPI can serve
    return (
        f"/static/exports/{filename}"
    )
    