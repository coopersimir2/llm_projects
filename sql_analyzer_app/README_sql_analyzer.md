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


<img width="1875" height="935" alt="Screenshot 2026-04-19 at 9 04 53 PM" src="https://github.com/user-attachments/assets/9635c2df-c2a4-4530-b313-7e262e700c9c" />
