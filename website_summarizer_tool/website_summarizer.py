"""
Day 2 homework solution: summarize a webpage with a local Ollama model.

Run from the repo root:
    uv run week1/simir_solution.py

Or from inside the week1 folder:
    uv run simir_solution.py
"""

import argparse

from openai import OpenAI

from scraper import fetch_website_contents

OLLAMA_BASE_URL = "http://localhost:11434/v1"
DEFAULT_MODEL = "deepseek-r1:1.5b"

SYSTEM_PROMPT = """
You are an information retrieval assistant. Please provide a summary of the contents of the website.
"""

USER_PROMPT_PREFIX = """
Here are the contents of a website.
Provide a short summary of this website.
If it includes news or announcements, then summarize these too.

"""


def messages_for(website: str) -> list[dict[str, str]]:
    """Build the chat completion payload."""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT_PREFIX + website},
    ]


def summarize(url: str, model: str = DEFAULT_MODEL) -> str:
    """Fetch a webpage and summarize it with a local Ollama model."""
    website = fetch_website_contents(url)
    ollama = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
    response = ollama.chat.completions.create(
        model=model,
        messages=messages_for(website),
    )
    return response.choices[0].message.content or ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarize a webpage using a locally running Ollama model."
    )
    parser.add_argument(
        "url",
        nargs="?",
        help="URL to summarize. If omitted, you will be prompted for one.",
    )
    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f'Ollama model to use. Defaults to "{DEFAULT_MODEL}".',
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    url = args.url or input("Enter a website URL to summarize: ").strip()
    if not url:
        raise SystemExit("No URL provided.")

    try:
        summary = summarize(url, model=args.model)
    except Exception as exc:
        raise SystemExit(
            "Failed to generate a summary. Make sure Ollama is running at "
            f"{OLLAMA_BASE_URL} and the model '{args.model}' is installed.\n"
            f"Original error: {exc}"
        ) from exc

    print(summary)


if __name__ == "__main__":
    main()
