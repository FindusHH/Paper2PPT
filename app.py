import json
import os
import streamlit as st


from openai import AzureOpenAI
from pdf_to_ppt import pdf_to_ppt


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

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

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
        pdf_to_ppt("input.pdf", output_path, client, deployment)


    with open(output_path, "rb") as f:
        st.download_button(
            label="Download PowerPoint",
            data=f,
            file_name="summary.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        )
