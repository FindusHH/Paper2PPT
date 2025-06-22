# Paper2PPT

This application converts a PDF document into a summarized PowerPoint presentation.

## Features
- Extracts text and images from each page of the uploaded PDF.
- Summarizes the text using Azure OpenAI and creates bullet points.
- Generates a PowerPoint presentation with up to five bullet points per slide and relevant images.
- Simple web interface built with Streamlit.
- Runs inside Docker and can be orchestrated with Docker Compose.
- All prompts are stored in text files inside `prompts/` and loaded at
  application start.
- API credentials are persisted in `config.json` after the first run.

## Usage

1. Build and start the service:

```bash
docker compose up --build
```

2. Open `http://localhost:8501` in your browser. On the first launch you will be
   asked for your Azure OpenAI credentials. They will be stored in `config.json`
   and reused on subsequent runs. You can change them later via "Edit
   Configuration" in the sidebar.

3. Upload a PDF and generate the presentation. The resulting PowerPoint file can
   be downloaded directly from the interface.
