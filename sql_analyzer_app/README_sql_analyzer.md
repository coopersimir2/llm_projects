# SQL Analyzer App

`sql_analyzer_app.py` is a Gradio prototype that lets a user paste in a SQL query and receive a plain-English explanation generated with the OpenAI API.

## Features

- Explains SQL queries in clear, plain English
- Streams the explanation into the UI as it is generated
- Accepts optional schema context for more accurate explanations
- Calls out joins, grouping, filtering, sorting, limits, and potentially destructive statements
- Launches in your browser and creates a Gradio share link

## Requirements

- Python environment managed with `uv`
- `OPENAI_API_KEY` set in your environment or `.env`

## Run

From the project root:

```bash
uv run week2/sql_analyzer_app.py
```

## File

- App: `week2/sql_analyzer_app.py`
