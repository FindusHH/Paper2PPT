# Paper2PPT

This application converts a PDF document into a summarized PowerPoint presentation.

## Features
- Extracts text and images from each page of the uploaded PDF.
- Summarizes the text using Azure OpenAI and creates bullet points.
- Generates a PowerPoint presentation with up to five bullet points per slide and relevant images.
- Simple web interface built with Streamlit.
- Runs inside Docker and can be orchestrated with Docker Compose.

## Usage

1. Set your Azure OpenAI credentials in `docker-compose.yml` or as environment variables:
   - `OPENAI_API_KEY`
   - `OPENAI_API_BASE`
   - `OPENAI_API_VERSION`
   - `OPENAI_DEPLOYMENT`

2. Build and start the service:

```bash
docker compose up --build
```

3. Open `http://localhost:8501` in your browser, upload a PDF and generate the presentation.

The resulting PowerPoint file can be downloaded directly from the interface.
