import os
from dotenv import load_dotenv
from pathlib import Path
from anthropic import Anthropic
from retrieve import retrieve

load_dotenv(Path(__file__).parent / ".env")
claude = Anthropic()


def ask(question, k=5):
    results = retrieve(question, k=k)

    reviews_text = ""
    for i, r in enumerate(results, start=1):
        reviews_text += f"[{i}] ({r[3]}⭐ {r[1]}, {r[2]}) \"{r[4]}\"\n\n"


    prompt = f"""You are a helpful assistant answering questions about Yelp businesses.
    Use ONLY the reviews below. If they don't answer the question, say so.

    Reviews:
    {reviews_text}
    Question: {question}

    Answer with citations like [1], [2]."""

    response = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.content[0].text