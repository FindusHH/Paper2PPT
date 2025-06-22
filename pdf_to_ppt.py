import io
import os
from typing import List


from langdetect import detect

# Path to the system prompt used for summarization
PROMPT_FILE = os.path.join(os.path.dirname(__file__), "prompts", "summarize.txt")


def load_prompt() -> str:

    """Load the system prompt from the prompts directory."""
    try:
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        # Fallback prompt if the file does not exist
        return (
            "Summarize the following text into at most 5 concise bullet points."


            " Respond in {language}."
        )


def save_prompt(content: str) -> None:
    """Persist the system prompt to disk."""
    with open(PROMPT_FILE, "w", encoding="utf-8") as f:
        f.write(content)


SYSTEM_PROMPT = load_prompt()

import fitz  # PyMuPDF
from pptx import Presentation
from pptx.util import Inches, Pt


def extract_pages(pdf_path: str):
    """Extract text and images from each page of a PDF."""
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        images = []
        for img in page.get_images(full=True):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            ext = base_image["ext"]
            images.append((image_bytes, ext))
        yield page_num + 1, text, images
    doc.close()


def detect_pdf_language(pdf_path: str) -> str:
    """Detect predominant language of the PDF text."""
    text_snippets = []
    for _, text, _ in extract_pages(pdf_path):
        text_snippets.append(text)
        if len(" ".join(text_snippets)) > 1000:
            break
    try:
        return detect(" ".join(text_snippets))
    except Exception:
        return "en"


def create_slide(prs: Presentation, title: str, bullets: List[str], images: List[bytes]):
    """Add a slide with a title, bullet points and images."""
    slide_layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(slide_layout)
    slide.shapes.title.text = title

    body = slide.shapes.placeholders[1].text_frame
    body.text = ""
    for point in bullets:
        p = body.add_paragraph()
        p.text = point
        p.level = 0
        p.font.size = Pt(32)

    for img_bytes, ext in images:
        image_stream = io.BytesIO(img_bytes)
        slide.shapes.add_picture(image_stream, Inches(1), Inches(3), height=Inches(3))


def _add_bullet_slides(prs: Presentation, title: str, bullets: List[str], images: List[bytes]):
    """Create one or more slides ensuring bullet lists fit."""
    MAX_BULLETS = 5
    for idx in range(0, len(bullets), MAX_BULLETS):
        group = bullets[idx : idx + MAX_BULLETS]
        slide_title = title if idx == 0 else f"{title} (cont.)"
        create_slide(prs, slide_title, group, images if idx == 0 else [])


def save_presentation(sections, output_path: str):
    prs = Presentation()
    for title, bullets, images in sections:
        _add_bullet_slides(prs, title, bullets, images)
    prs.save(output_path)


from openai import AzureOpenAI


def summarize_text(
    text: str,
    client: AzureOpenAI,
    deployment: str,
    *,
    language: str = "",
    max_tokens: int = 256,
) -> List[str]:

    """Use Azure OpenAI to summarize text into bullet points."""
    system_prompt = SYSTEM_PROMPT

    if "{language}" in system_prompt:
        system_prompt = system_prompt.format(language=language or "the original language")
    elif language:
        system_prompt = f"{system_prompt}\nRespond in {language}."

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text},
    ]

    response = client.chat.completions.create(
        model=deployment,
        messages=messages,
        max_tokens=max_tokens,
    )
    content = response.choices[0].message.content

    bullets = [line.lstrip("- ").strip() for line in content.splitlines() if line]
    return bullets


def pdf_to_ppt(
    pdf_path: str,
    output_path: str,
    client: AzureOpenAI,
    deployment: str,
    *,
    language: str = "",
) -> None:
    sections = []
    for page_num, text, images in extract_pages(pdf_path):
        title = f"Page {page_num}"
        bullets = summarize_text(text, client, deployment, language=language)

        sections.append((title, bullets, images))
    save_presentation(sections, output_path)

