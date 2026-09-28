# ComicCraft AI

ComicCraft AI is a Generative AI application that transforms a story idea into a multi-panel comic.

The application uses AI to generate:

* Story outline
* Comic panel descriptions
* Character dialogue
* Narration
* Image prompts
* Comic panel artwork
* PDF export

---

## 1. Project Structure

```text
ComicCraft/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── routes.py
│   ├── config.py
│   ├── schemas.py
│   ├── gemini_flash.py
│   ├── gemini_pro.py
│   ├── image_generator.py
│   ├── layout_builder.py
│   └── exporters.py
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── comic_preview.html
│   └── export_success.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   ├── panels/
│   └── exports/
│
├── tests/
│   └── test_app.py
│
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
└── README.md
```

---

# 2. Requirements

Before running the project, install:

* Python 3.10 or newer
* VS Code
* Internet connection
* Google Gemini API key

---

# 3. Create Virtual Environment

Open the VS Code terminal inside the `ComicCraft` folder.

Run:

```bash
python -m venv venv
```

---

# 4. Activate Virtual Environment

## Windows

```bash
venv\Scripts\activate
```

After activation, the terminal should show something similar to:

```text
(venv)
```

---

# 5. Install Dependencies

Run:

```bash
pip install -r requirements.txt
```

Wait until all packages are installed successfully.

---

# 6. Configure Environment Variables

Create a file named:

```text
.env
```

in the main `ComicCraft` folder.

Add:

```env
APP_NAME=ComicCraft AI
APP_VERSION=1.0.0

GEMINI_API_KEY=YOUR_GEMINI_API_KEY

GEMINI_FLASH_MODEL=gemini-2.5-flash
GEMINI_PRO_MODEL=gemini-2.5-pro

HF_API_KEY=

HF_IMAGE_MODEL=stabilityai/stable-diffusion-xl-base-1.0

DEMO_MODE=true

HOST=127.0.0.1
PORT=8000
DEBUG=true

DEFAULT_PANELS=5
MIN_PANELS=1
MAX_PANELS=12

IMAGE_WIDTH=1024
IMAGE_HEIGHT=1024

API_TIMEOUT=180
```

Replace:

```text
YOUR_GEMINI_API_KEY
```

with your actual Gemini API key.

Do not upload `.env` to GitHub.

---

# 7. Run the Application

From the main `ComicCraft` folder, run:

```bash
uvicorn app.main:app --reload
```

If everything is configured correctly, you should see something similar to:

```text
Uvicorn running on http://127.0.0.1:8000
```

---

# 8. Open the Application

Open your browser and visit:

```text
http://127.0.0.1:8000
```

You should see the ComicCraft AI home page.

---

# 9. Create a Comic

Enter:

### Comic Title

Example:

```text
The Mysterious Robot
```

### Story Idea

Example:

```text
A college student discovers a mysterious robot
hidden inside an old laboratory.
```

### Main Character

```text
A young college student
```

### Setting

```text
A futuristic college campus
```

### Story Tone

```text
Adventurous
```

### Art Style

```text
Cinematic Comic Book
```

Select the number of panels and click:

```text
Generate My Comic
```

---

# 10. Comic Generation Flow

The application follows this general workflow:

```text
User Story
     ↓
Gemini Flash
     ↓
Panel Outline
     ↓
Gemini Pro
     ↓
Complete Comic Story
     ↓
Image Generation
     ↓
Comic Layout
     ↓
PDF Export
```

---

# 11. Run Tests

Open another VS Code terminal.

Activate the virtual environment if necessary:

```bash
venv\Scripts\activate
```

Then run:

```bash
pytest -v
```

This runs the automated application tests.

---

# 12. API Documentation

When the FastAPI application is running, open:

```text
http://127.0.0.1:8000/docs
```

This opens the interactive Swagger API documentation.

You can use it to inspect and test the available API endpoints.

---

# 13. Health Check

The application provides a health check endpoint:

```text
GET /health
```

Open:

```text
http://127.0.0.1:8000/health
```

A successful response should indicate that the application is running.

---

# 14. Demo Mode

The project supports demo mode.

In `.env`:

```env
DEMO_MODE=true
```

Demo mode is useful for testing the application without making unnecessary real AI requests.

When you are ready to use the actual AI services, configure the required API keys and set:

```env
DEMO_MODE=false
```

---

# 15. Generated Files

Generated comic images are stored in:

```text
static/panels/
```

Generated PDF files are stored in:

```text
static/exports/
```

These generated files are excluded from Git using `.gitignore`.

---

# 16. Troubleshooting

## Python command not found

Try:

```bash
py --version
```

If `py` works, create the virtual environment with:

```bash
py -m venv venv
```

---

## Virtual environment is not activated

Windows:

```bash
venv\Scripts\activate
```

PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

---

## Missing package error

Run:

```bash
pip install -r requirements.txt
```

again.

---

## Port 8000 is already in use

Run the application on another port:

```bash
uvicorn app.main:app --reload --port 8001
```

Then open:

```text
http://127.0.0.1:8001
```

---

## API key error

Check that `.env` contains:

```env
GEMINI_API_KEY=your_actual_key
```

Make sure there are no unnecessary quotation marks or spaces around the key.

---

# 17. Development Commands

Start the application:

```bash
uvicorn app.main:app --reload
```

Run tests:

```bash
pytest -v
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Check Python version:

```bash
python --version
```

---

# 18. Important Security Notes

Never commit your `.env` file.

Never publish your Gemini API key in:

* GitHub
* Public repositories
* Screenshots
* Frontend JavaScript
* HTML files
* Chat messages

Keep secret API keys inside `.env`.

---

# 19. Application Summary

ComicCraft AI combines:

* FastAPI backend
* Jinja2 templates
* Gemini AI
* AI image generation
* Comic layout generation
* PDF export
* Automated tests

The application is designed to convert a simple story idea into a complete AI-generated comic.

---

## 20. Quick Start

For future runs:

```bash
cd ComicCraft
```

Activate the environment:

```bash
venv\Scripts\activate
```

Start the server:

```bash
uvicorn app.main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

For API documentation:

```text
http://127.0.0.1:8000/docs
```

For tests:

```bash
pytest -v
```
