# Paper2PPT

This application converts a PDF document into a summarized PowerPoint presentation.

## Features
- Extracts text and images from each page of the uploaded PDF.
- Summarizes the text using Azure OpenAI and creates bullet points.
- Uses a language model to decide if extracted images are relevant to the page text before adding them to slides.
- Generates a PowerPoint presentation with up to five bullet points per slide and relevant images.
- Chooses at most one relevant image per slide based on an LLM score.

- Multiple PDF pages can be combined into a single slide.

- User interface language can be switched (English, German, Spanish or Chinese by default).
- Simple web interface built with Streamlit.
- Runs inside Docker and can be orchestrated with Docker Compose.
- All prompts are stored in text files inside `prompts/` and loaded at application start. The default summarization prompt lives in `prompts/summarize.txt` and can be edited from the sidebar.
- The relevance check prompt for images resides in `prompts/image_eval.txt` and is also editable.

- The title creation prompt is stored in `prompts/title.txt`.
- API credentials are persisted in `config.json` after the first run.
- The summarization language can be chosen (detected from the PDF or the languages listed in `settings.json`).
- Both the system prompt and API configuration can be edited from the sidebar.
- Formatting options like font size and maximum words per bullet are defined in `settings.json`.
- Settings such as font size, image relevance threshold and pages per slide can be edited from the sidebar and persist in `settings.json`.
- A scrollable log displays the current processing step and progress while creating the PowerPoint file.


- The title creation prompt is stored in `prompts/title.txt`.
- API credentials are persisted in `config.json` after the first run.
- The summarization language can be chosen (detected from the PDF or the languages listed in `settings.json`).
- Both the system prompt and API configuration can be edited from the sidebar.
- Formatting options like font size and maximum words per bullet are defined in `settings.json`.

- Settings can be edited from the sidebar and persist in `settings.json`.
- A scrollable log displays the current processing step and progress while creating the PowerPoint file.

- The title creation prompt is stored in `prompts/title.txt`.
- API credentials are persisted in `config.json` after the first run.
- The summarization language can be chosen (detected from the PDF or the languages listed in `settings.json`).
- Both the system prompt and API configuration can be edited from the sidebar.
- Formatting options like font size and maximum words per bullet are defined in `settings.json`.



## Usage

1. Build and start the service:

```bash
docker compose up --build
```

2. Open `http://localhost:8501` in your browser. On the first launch you will be asked for your Azure OpenAI API key. Endpoint, deployment and version are pre-filled from the Docker compose file and stored in `config.json` for reuse. You can adjust them later via "Edit Configuration" in the sidebar.

3. Upload a PDF and generate the presentation. The resulting PowerPoint file can be downloaded directly from the interface.


To add more summarization or UI languages, edit the `languages` section in `settings.json`.

