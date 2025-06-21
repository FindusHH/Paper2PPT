import os
import streamlit as st

import openai
from pdf_to_ppt import pdf_to_ppt

st.title("PDF to PowerPoint Summary")

api_base = st.text_input("Azure OpenAI API Base", value=os.getenv("OPENAI_API_BASE", ""))
api_key = st.text_input("Azure OpenAI API Key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
api_version = st.text_input("Azure OpenAI API Version", value=os.getenv("OPENAI_API_VERSION", "2023-07-01-preview"))
deployment = st.text_input("Deployment Name", value=os.getenv("OPENAI_DEPLOYMENT", ""))

uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

if st.button("Generate PowerPoint") and uploaded_file:
    with open("input.pdf", "wb") as f:
        f.write(uploaded_file.read())

    openai.api_type = "azure"
    openai.api_base = api_base
    openai.api_version = api_version
    openai.api_key = api_key

    output_path = "output.pptx"
    with st.spinner("Processing PDF..."):
        pdf_to_ppt("input.pdf", output_path, deployment)

    with open(output_path, "rb") as f:
        st.download_button(
            label="Download PowerPoint",
            data=f,
            file_name="summary.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        )
