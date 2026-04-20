import os
from textwrap import dedent

import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv(override=True)

MODEL = "gpt-4.1-nano"
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
    You are a SQL analyst inside a Gradio app.
    Explain SQL queries in plain English for learners and working professionals.
    Be accurate, concise, and practical.
    Assume the SQL is read-only unless it clearly modifies data.

    When you explain a query:
    - Start with a 1-2 sentence plain-English summary.
    - Then provide a short breakdown with these headings when relevant:
      - What it reads
      - How it filters
      - How it combines data
      - How it groups or aggregates
      - How it orders or limits results
      - Important notes
    - Mention joins, subqueries, CTEs, window functions, aggregates, and limits if present.
    - If the query could be risky or destructive, say so clearly.
    - If the SQL appears invalid or ambiguous, explain your best interpretation and note the uncertainty.
    - Return markdown without code fences.
    """
).strip()


def build_user_prompt(sql_query: str, schema_context: str) -> str:
    schema_section = schema_context.strip() or "No schema context provided."
    return dedent(
        f"""
        Explain the SQL query below in plain English.

        Schema context:
        {schema_section}

        SQL query:
        {sql_query}

        Requirements:
        - Keep the explanation easy to understand for someone who knows basic data concepts.
        - Be specific about what rows are returned and how the result set is shaped.
        - If aliases are used, map them back to the original table names or columns.
        - If there are calculations, describe them in plain language.
        - If the query updates, inserts, deletes, truncates, alters, or drops data, call that out prominently.
        """
    ).strip()


def explain_sql(sql_query: str, schema_context: str):
    if not sql_query.strip():
        yield "Please enter a SQL query to analyze."
        return

    try:
        client = build_client()
        stream = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": build_user_prompt(sql_query, schema_context),
                },
            ],
            temperature=0.2,
            stream=True,
        )
    except Exception as exc:
        yield f"Unable to start SQL analysis: {exc}"
        return

    response = ""
    try:
        for chunk in stream:
            response += chunk.choices[0].delta.content or ""
            yield response
    except Exception as exc:
        message = response or "No explanation was generated."
        yield f"{message}\n\nSQL analysis stopped because of an API error: {exc}"


def load_example(example_sql: str, example_schema: str) -> tuple[str, str]:
    return example_sql, example_schema


def get_share_link_markdown() -> str:
    if SHARE_URL:
        return f"**Link to SQL Analyzer:** [{SHARE_URL}]({SHARE_URL})"
    return "_Creating shareable link..._"


def refresh_share_link() -> tuple[str, gr.Timer]:
    if SHARE_URL:
        return get_share_link_markdown(), gr.Timer(active=False)
    return get_share_link_markdown(), gr.Timer(active=True)


def build_app() -> gr.Blocks:
    with gr.Blocks(title="SQL Analyzer") as app:
        gr.Markdown(
            """
            # SQL Analyzer
            """
        )
        share_link = gr.Markdown(get_share_link_markdown())
        gr.Markdown("Paste a SQL query and get a plain-English explanation powered by the OpenAI API.")
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
            with gr.Column(scale=3):
                sql_query = gr.Textbox(
                    label="SQL Query",
                    placeholder=(
                        "SELECT c.name, COUNT(o.id) AS order_count\n"
                        "FROM customers c\n"
                        "JOIN orders o ON c.id = o.customer_id\n"
                        "WHERE o.status = 'completed'\n"
                        "GROUP BY c.name\n"
                        "ORDER BY order_count DESC\n"
                        "LIMIT 10;"
                    ),
                    lines=14,
                )
            with gr.Column(scale=2):
                schema_context = gr.Textbox(
                    label="Optional Schema Context",
                    placeholder=(
                        "customers(id, name, email)\n"
                        "orders(id, customer_id, status, created_at)"
                    ),
                    lines=14,
                )

        with gr.Row():
            analyze_button = gr.Button("Explain Query", variant="primary")
            clear_button = gr.Button("Clear")

        explanation = gr.Markdown(label="Explanation")

        gr.Examples(
            examples=[
                [
                    dedent(
                        """
                        SELECT department, AVG(salary) AS avg_salary
                        FROM employees
                        WHERE active = true
                        GROUP BY department
                        ORDER BY avg_salary DESC;
                        """
                    ).strip(),
                    "employees(id, department, salary, active)",
                ],
                [
                    dedent(
                        """
                        WITH recent_orders AS (
                            SELECT customer_id, total_amount
                            FROM orders
                            WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
                        )
                        SELECT customer_id, SUM(total_amount) AS monthly_spend
                        FROM recent_orders
                        GROUP BY customer_id
                        HAVING SUM(total_amount) > 500;
                        """
                    ).strip(),
                    "orders(id, customer_id, total_amount, order_date)",
                ],
                [
                    dedent(
                        """
                        UPDATE products
                        SET price = price * 1.05
                        WHERE category = 'electronics';
                        """
                    ).strip(),
                    "products(id, name, category, price)",
                ],
            ],
            inputs=[sql_query, schema_context],
            outputs=[sql_query, schema_context],
            fn=load_example,
            cache_examples=False,
        )

        analyze_button.click(
            fn=explain_sql,
            inputs=[sql_query, schema_context],
            outputs=explanation,
        )
        sql_query.submit(
            fn=explain_sql,
            inputs=[sql_query, schema_context],
            outputs=explanation,
        )
        clear_button.click(
            fn=lambda: ("", "", ""),
            inputs=[],
            outputs=[sql_query, schema_context, explanation],
            queue=False,
        )

    return app


if __name__ == "__main__":
    app = build_app()
    app.queue()
    app.launch(share=True, inbrowser=True)
    if hasattr(app, "share_url"):
        SHARE_URL = app.share_url or ""
