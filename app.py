
"""Streamlit UI for converting PDF files to PowerPoint
with Azure OpenAI summarization.

The app loads prompts and settings from disk and allows
users to edit them via the sidebar."""


import json
import os
import streamlit as st


def rerun() -> None:
    """Compatibility wrapper for Streamlit rerun."""
    try:
        st.experimental_rerun()
    except AttributeError:
        st.rerun()


from openai import AzureOpenAI
from pdf_to_ppt import (
    pdf_to_ppt,
    detect_pdf_language,
    load_prompt,
    save_prompt,

    IMAGE_PROMPT_PATH,
    TITLE_PROMPT_PATH,
    load_settings,
)


CONFIG_FILE = "config.json"

SETTINGS = load_settings()
LANGUAGE_OPTIONS = SETTINGS.get("languages", {})
LANGUAGE_NAMES = {v: k for k, v in LANGUAGE_OPTIONS.items()}

# Text labels for the UI in different languages
TRANSLATIONS = {
    "en": {
        "title": "PDF to PowerPoint Summary",
        "upload": "Upload PDF",
        "generate": "Generate PowerPoint",
        "detected": "Detected language",
        "summarization": "Summarization language",
    },
    "de": {
        "title": "PDF zu PowerPoint Zusammenfassung",
        "upload": "PDF hochladen",
        "generate": "PowerPoint erstellen",
        "detected": "Erkannte Sprache",
        "summarization": "Sprache der Zusammenfassung",
    },
    "es": {
        "title": "Resumen PDF a PowerPoint",
        "upload": "Subir PDF",
        "generate": "Generar PowerPoint",
        "detected": "Idioma detectado",
        "summarization": "Idioma del resumen",
    },
    "zh": {

        "title": "PDF\u8f6cPowerPoint\u6458\u8981",
        "upload": "\u4e0a\u4f20PDF",
        "generate": "\u751f\u6210PPT",
        "detected": "\u68c0\u6d4b\u8bed\u8a00",
        "summarization": "\u6458\u8981\u8bed\u8a00",
    },
}



def load_config():
    """Return saved API settings or defaults from env vars."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "api_base": os.getenv("OPENAI_API_BASE", ""),
        "api_key": os.getenv("OPENAI_API_KEY", ""),
        "api_version": os.getenv("OPENAI_API_VERSION", "2023-07-01-preview"),
        "deployment": os.getenv("OPENAI_DEPLOYMENT", ""),
    }


def save_config(data: dict):
    """Persist API settings to disk."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)


processing = st.session_state.get("processing", False)

ui_choice = st.sidebar.selectbox(
    "UI Language", list(LANGUAGE_OPTIONS.keys()), disabled=processing
)
ui_code = LANGUAGE_OPTIONS[ui_choice]
TR = TRANSLATIONS.get(ui_code, TRANSLATIONS["en"])

st.title(TR["title"])

config = load_config()

# Sidebar switch to allow editing of the LLM prompts
edit_prompt = st.sidebar.checkbox("Edit Prompt", disabled=processing)
edit_settings = st.sidebar.checkbox("Edit Settings", disabled=processing)

# Show configuration editor on first run or when the user selects "Edit Configuration"
edit_config = False
if not os.path.exists(CONFIG_FILE):
    st.info("Please enter your Azure OpenAI configuration.")
    edit_config = True
else:
    edit_config = st.sidebar.checkbox("Edit Configuration", disabled=processing)

# When editing is enabled show input fields for all settings
if edit_config:
    api_base = st.text_input("Azure OpenAI API Base", value=config.get("api_base", ""))
    api_key = st.text_input("Azure OpenAI API Key", type="password", value=config.get("api_key", ""))
    api_version = st.text_input(
        "Azure OpenAI API Version",
        value=config.get("api_version", "2023-07-01-preview"),
    )
    deployment = st.text_input("Deployment Name", value=config.get("deployment", ""))
    if st.button("Save Configuration"):
        config = {
            "api_base": api_base,
            "api_key": api_key,
            "api_version": api_version,
            "deployment": deployment,
        }
        save_config(config)
        st.success("Configuration saved. You can now generate a presentation.")
        rerun()
else:
    # Use the previously saved configuration values
    api_base = config.get("api_base", "")
    api_key = config.get("api_key", "")
    api_version = config.get("api_version", "2023-07-01-preview")
    deployment = config.get("deployment", "")

if edit_prompt:
    # Load current prompt texts so they can be edited in the sidebar
    current_summary = load_prompt()
    current_image = load_prompt(IMAGE_PROMPT_PATH)
    current_title = load_prompt(TITLE_PROMPT_PATH)
    new_summary = st.text_area(
        "Summarization Prompt", value=current_summary, height=200
    )
    new_image = st.text_area(
        "Image Relevance Prompt", value=current_image, height=200
    )
    new_title = st.text_area(
        "Title Prompt", value=current_title, height=150
    )
    if st.button("Save Prompts"):
        save_prompt(new_summary)
        save_prompt(new_image, IMAGE_PROMPT_PATH)
        save_prompt(new_title, TITLE_PROMPT_PATH)
        st.success("Prompts saved.")

if edit_settings:
    SETTINGS = load_settings()
    font_size = st.number_input(
        "Font Size", value=SETTINGS.get("font_size", 24), min_value=12, max_value=32
    )
    max_words = st.number_input(
        "Max words per bullet", value=SETTINGS.get("max_words_per_bullet", 10), min_value=1
    )
    max_title = st.number_input(
        "Max words per title", value=SETTINGS.get("max_words_title", 4), min_value=1
    )
    min_score = st.number_input(
        "Min image relevance score", value=SETTINGS.get("min_image_score", 5), min_value=0, max_value=10
    )
    if st.button("Save Settings"):
        SETTINGS.update(
            {
                "font_size": int(font_size),
                "max_words_per_bullet": int(max_words),
                "max_words_title": int(max_title),
                "min_image_score": float(min_score),
            }
        )
        with open("settings.json", "w", encoding="utf-8") as f:
            json.dump(SETTINGS, f, indent=2)
        st.success("Settings saved.")

uploaded_file = st.file_uploader(TR["upload"], type=["pdf"], disabled=processing)

language_code = ""
# When a PDF is uploaded we detect its main language
if uploaded_file:
    if (
        # Detect language once per uploaded file
        "pdf_lang" not in st.session_state
        or st.session_state.get("file_name") != uploaded_file.name
    ):
        # Save the file so PyMuPDF can read it
        with open("input.pdf", "wb") as f:
            f.write(uploaded_file.read())
        # Use a helper to detect the main language of the PDF
        detected = detect_pdf_language("input.pdf")
        st.session_state["pdf_lang"] = detected
        st.session_state["file_name"] = uploaded_file.name
    detected_code = st.session_state.get("pdf_lang", "en")
    detected_name = LANGUAGE_NAMES.get(detected_code, detected_code)
    st.write(f"{TR['detected']}: {detected_name}")
    # Allow the user to override the detected language for summarization
    options = [f"PDF language ({detected_name})"] + list(LANGUAGE_OPTIONS.keys())
    choice = st.selectbox(TR["summarization"], options)
    if choice.startswith("PDF"):
        language_code = detected_code
    else:
        language_code = LANGUAGE_OPTIONS[choice]

generate = st.button(TR["generate"], disabled=processing)

log_box = st.empty()
progress_bar = st.progress(0)
log_messages = []

if generate and uploaded_file:
    st.session_state["processing"] = True
    with open("input.pdf", "wb") as f:
        f.write(uploaded_file.read())

    client = AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=api_base,
    )


    pdf_name = os.path.splitext(uploaded_file.name)[0]
    output_path = f"{pdf_name}_summary.pptx"

    def update_progress(done, total, message):
        percent = int(done / total * 100)
        log_messages.append(f"{message} ({percent}%)")
        log_box.text_area("Progress", "\n".join(log_messages), height=200)
        progress_bar.progress(percent)

    with st.spinner("Processing PDF..."):
        pdf_to_ppt(
            "input.pdf",
            output_path,
            client,
            deployment,
            language=language_code,
            progress_callback=update_progress,
        )


    st.session_state["processing"] = False
    progress_bar.progress(100)
    log_messages.append("Done")
    log_box.text_area("Progress", "\n".join(log_messages), height=200)

    with open(output_path, "rb") as f:
        # Offer the resulting file for download
        st.download_button(
            label="Download PowerPoint",
            data=f,
            file_name=output_path,
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            type="primary",
        )
