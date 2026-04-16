import os
import time
from textwrap import dedent

import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv(override=True)

MODEL = "gpt-4.1-mini"
SHARE_URL = ""


def build_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is not set. Add it to your environment or .env file before launching the app."
        )
    return OpenAI(api_key=api_key)


SYSTEM_PROMPT = dedent(
    """
    You are a creative story writer inside a Gradio app.
    Write vivid, polished short stories with strong character voices.
    Always include all three named characters in meaningful ways.
    Keep the story concise, satisfying, and appropriate for a broad audience unless the user explicitly asks otherwise.
    Return markdown without code fences.
    """
).strip()


def build_user_prompt(
    premise: str,
    genre: str,
    setting: str,
    tone: str,
    character_one_name: str,
    character_one_description: str,
    character_two_name: str,
    character_two_description: str,
    character_three_name: str,
    character_three_description: str,
) -> str:
    return dedent(
        f"""
        Write a short story based on the details below.

        Premise: {premise}
        Genre: {genre}
        Setting: {setting}
        Tone: {tone}

        Character 1: {character_one_name}
        Description: {character_one_description}

        Character 2: {character_two_name}
        Description: {character_two_description}

        Character 3: {character_three_name}
        Description: {character_three_description}

        Requirements:
        - Give each character a clear role in the story.
        - Make the story feel complete, with a beginning, middle, and ending.
        - Keep it roughly 500 to 800 words.
        - Add a short title at the top.
        """
    ).strip()


def create_story(
    premise: str,
    genre: str,
    setting: str,
    tone: str,
    character_one_name: str,
    character_one_description: str,
    character_two_name: str,
    character_two_description: str,
    character_three_name: str,
    character_three_description: str,
):
    fields = {
        "Premise": premise,
        "Character 1 name": character_one_name,
        "Character 1 description": character_one_description,
        "Character 2 name": character_two_name,
        "Character 2 description": character_two_description,
        "Character 3 name": character_three_name,
        "Character 3 description": character_three_description,
    }

    missing_fields = [label for label, value in fields.items() if not value.strip()]
    if missing_fields:
        yield "Please fill in all required fields before generating a story."
        return

    try:
        client = build_client()
        stream = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": build_user_prompt(
                        premise,
                        genre,
                        setting,
                        tone,
                        character_one_name,
                        character_one_description,
                        character_two_name,
                        character_two_description,
                        character_three_name,
                        character_three_description,
                    ),
                },
            ],
            stream=True,
        )
    except Exception as exc:
        yield f"Unable to start story generation: {exc}"
        return

    response = ""
    try:
        for chunk in stream:
            response += chunk.choices[0].delta.content or ""
            yield response
    except Exception as exc:
        message = response or "No story content was generated."
        yield f"{message}\n\nStory generation stopped because of an API error: {exc}"


def get_share_link_markdown() -> str:
    if SHARE_URL:
        return f"**Link to Story Maker:** [{SHARE_URL}]({SHARE_URL})"
    return "_Creating shareable link..._"


def refresh_share_link() -> tuple[str, gr.Timer]:
    if SHARE_URL:
        return get_share_link_markdown(), gr.Timer(active=False)
    return get_share_link_markdown(), gr.Timer(active=True)


def build_app() -> gr.Blocks:
    with gr.Blocks(title="Story Maker") as app:
        gr.Markdown(
            """
            # Story Maker
            """
        )
        share_link = gr.Markdown(get_share_link_markdown())
        gr.Markdown("Build a short story with three characters using the OpenAI API.")
        share_link_timer = gr.Timer(value=1, active=True)

        app.load(
            fn=refresh_share_link,
            outputs=[share_link, share_link_timer],
            queue=False,
            show_progress="hidden",
        )
        share_link_timer.tick(
            fn=refresh_share_link,
            outputs=[share_link, share_link_timer],
            queue=False,
            show_progress="hidden",
        )

        with gr.Row():
            premise = gr.Textbox(
                label="Story Premise",
                placeholder="A mysterious lighthouse starts speaking to the people who visit it.",
                lines=3,
            )

        with gr.Row():
            genre = gr.Dropdown(
                choices=["Fantasy", "Science Fiction", "Mystery", "Adventure", "Romance", "Comedy"],
                value="Fantasy",
                label="Genre",
            )
            setting = gr.Textbox(
                label="Setting",
                value="A windswept island on the edge of the known world",
            )
            tone = gr.Dropdown(
                choices=["Whimsical", "Suspenseful", "Heartwarming", "Epic", "Funny", "Bittersweet"],
                value="Heartwarming",
                label="Tone",
            )

        with gr.Row():
            with gr.Column():
                character_one_name = gr.Textbox(label="Character 1 Name", placeholder="Mara")
                character_one_description = gr.Textbox(
                    label="Character 1 Description",
                    placeholder="A brave apprentice mapmaker who never admits she is afraid.",
                    lines=4,
                )
            with gr.Column():
                character_two_name = gr.Textbox(label="Character 2 Name", placeholder="Ivo")
                character_two_description = gr.Textbox(
                    label="Character 2 Description",
                    placeholder="An aging lighthouse keeper with a dry sense of humor and a secret past.",
                    lines=4,
                )
            with gr.Column():
                character_three_name = gr.Textbox(label="Character 3 Name", placeholder="Fen")
                character_three_description = gr.Textbox(
                    label="Character 3 Description",
                    placeholder="A clever seabird who seems to understand more than it should.",
                    lines=4,
                )

        generate_button = gr.Button("Create Story", variant="primary")
        output = gr.Markdown(label="Story")

        generate_button.click(
            fn=create_story,
            inputs=[
                premise,
                genre,
                setting,
                tone,
                character_one_name,
                character_one_description,
                character_two_name,
                character_two_description,
                character_three_name,
                character_three_description,
            ],
            outputs=output,
        )

    return app


def main() -> None:
    global SHARE_URL

    app = build_app()
    _, _, share_url = app.launch(
        inbrowser=True,
        share=True,
        prevent_thread_lock=True,
        show_error=True,
    )
    SHARE_URL = share_url or ""

    try:
        app.block_thread()
    except KeyboardInterrupt:
        app.close()
        time.sleep(0.2)


if __name__ == "__main__":
    main()
