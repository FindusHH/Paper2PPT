# Paper2PPT

This application converts a PDF document into a summarized PowerPoint presentation.

## Features
- Extracts text and images from each page of the uploaded PDF.
- Summarizes the text using Azure OpenAI and creates bullet points.
- Uses a language model to decide if extracted images are relevant to the page text before adding them to slides.
- Generates a PowerPoint presentation with up to five bullet points per slide and relevant images.
- Simple web interface built with Streamlit.
- Runs inside Docker and can be orchestrated with Docker Compose.
- All prompts are stored in text files inside `prompts/` and loaded at application start. The default summarization prompt lives in `prompts/summarize.txt` and can be edited from the sidebar.
- The relevance check prompt for images resides in `prompts/image_eval.txt` and is also editable.
- API credentials are persisted in `config.json` after the first run.
- The summarization language can be chosen (detected from the PDF, German, English, Spanish or Chinese by default).
- Both the system prompt and API configuration can be edited from the sidebar.

- All prompts are stored in text files inside `prompts/` and loaded at application start.
- API credentials are persisted in `config.json` after the first run.

- The summarization language can be chosen (detected from the PDF, German,
  English, Spanish or Chinese by default).
- Both the system prompt and API configuration can be edited from the sidebar.


=======

## Usage

1. Build and start the service:

```bash
docker compose up --build
```

2. Open `http://localhost:8501` in your browser. On the first launch you will be asked for your Azure OpenAI API key. Endpoint, deployment and version are pre-filled from the Docker compose file and stored in `config.json` for reuse. You can adjust them later via "Edit Configuration" in the sidebar.

3. Upload a PDF and generate the presentation. The resulting PowerPoint file can be downloaded directly from the interface.

To add more summarization languages, edit the `LANGUAGE_OPTIONS` dictionary in `app.py`.

