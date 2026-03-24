from __future__ import annotations
import json
import os
from openai import OpenAI
from .bot_prompts import SYSTEM_PROMPT


def answer_with_snapp_bot(user_question: str, dashboard_context: dict) -> str:
    """
    Generate a grounded answer using only the supplied dashboard context.
    Requires OPENAI_API_KEY in environment variables.
    """

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return (
            "Snapp Bot is not connected yet. The OpenAI API key is missing. "
            "Please set OPENAI_API_KEY in your environment."
        )

    try:
        client = OpenAI(api_key=api_key)

        context_json = json.dumps(dashboard_context, default=str, ensure_ascii=False)

        user_input = f"""
Dashboard context:
{context_json}

User question:
{user_question}

Answer only from the dashboard context above.
"""

        response = client.responses.create(
            model="gpt-5.4",
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input},
            ],
        )

        text = getattr(response, "output_text", None)
        if text and text.strip():
            return text.strip()

        return "I could not generate a response from the dashboard context."

    except Exception as e:
        return f"Snapp Bot could not respond because of an API/runtime error: {e}"