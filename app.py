import json
import os
import streamlit as st


from openai import AzureOpenAI
from pdf_to_ppt import (
    pdf_to_ppt,
    detect_pdf_language,
    load_prompt,
    save_prompt,
)


CONFIG_FILE = "config.json"

LANGUAGE_OPTIONS = {
    "German": "de",
    "English": "en",
    "Spanish": "es",
    "Chinese": "zh",
}

LANGUAGE_NAMES = {v: k for k, v in LANGUAGE_OPTIONS.items()}


def load_config():
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
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)



CONFIG_FILE = "config.json"


def load_config():
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
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)


st.title("PDF to PowerPoint Summary")

config = load_config()


edit_prompt = st.sidebar.checkbox("Edit Prompt")


# Show configuration editor if no config is present or user requests it
edit_config = False
if not os.path.exists(CONFIG_FILE):
    st.info("Please enter your Azure OpenAI configuration.")
    edit_config = True
else:
    edit_config = st.sidebar.checkbox("Edit Configuration")

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
        st.experimental_rerun()
else:
    api_base = config.get("api_base", "")
    api_key = config.get("api_key", "")
    api_version = config.get("api_version", "2023-07-01-preview")
    deployment = config.get("deployment", "")


if edit_prompt:
    current_prompt = load_prompt()
    new_prompt = st.text_area("System Prompt", value=current_prompt, height=200)
    if st.button("Save Prompt"):
        save_prompt(new_prompt)
        st.success("Prompt saved.")


uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

language_code = ""
if uploaded_file:
    if (
        "pdf_lang" not in st.session_state
        or st.session_state.get("file_name") != uploaded_file.name
    ):
        with open("input.pdf", "wb") as f:
            f.write(uploaded_file.read())
        detected = detect_pdf_language("input.pdf")
        st.session_state["pdf_lang"] = detected
        st.session_state["file_name"] = uploaded_file.name
    detected_code = st.session_state.get("pdf_lang", "en")
    detected_name = LANGUAGE_NAMES.get(detected_code, detected_code)
    st.write(f"Detected language: {detected_name}")
    options = [f"PDF language ({detected_name})"] + list(LANGUAGE_OPTIONS.keys())
    choice = st.selectbox("Summarization language", options)
    if choice.startswith("PDF"):
        language_code = detected_code
    else:
        language_code = LANGUAGE_OPTIONS[choice]

if st.button("Generate PowerPoint") and uploaded_file:
    with open("input.pdf", "wb") as f:
        f.write(uploaded_file.read())


    client = AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=api_base,
    )

    output_path = "output.pptx"
    with st.spinner("Processing PDF..."):
        pdf_to_ppt("input.pdf", output_path, client, deployment, language=language_code)


    with open(output_path, "rb") as f:
        st.download_button(
            label="Download PowerPoint",
            data=f,
            file_name="summary.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        )
