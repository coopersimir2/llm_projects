# Story Maker App

`story_maker_app.py` is a Gradio app that uses the OpenAI API to generate a short story from a premise, genre, setting, tone, and three character descriptions.

## Features

- Creates a short story with three named characters
- Streams the story into the UI as it is generated
- Launches in your browser
- Creates a Gradio share link and displays it in the app

## Requirements

- Python environment managed with `uv`
- `OPENAI_API_KEY` set in your environment or `.env`

## Run

From the project root:

```bash
uv run week2/story_maker_app.py
```

## File

- App: `week2/story_maker_app.py`
