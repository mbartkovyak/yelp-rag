# vector_app/eval.py
#
# Eval harness for the Yelp RAG pipeline.
# Scores GENERATION quality (is the answer good?) using LLM-as-judge.
# Retrieval scoring (recall@k via expected_review_ids) is a future extension.

import os
from dotenv import load_dotenv
from pathlib import Path
from anthropic import Anthropic
from ask import ask

load_dotenv(Path(__file__).parent / ".env")
judge = Anthropic()


EVAL = [
    # 1. Honesty / refusal — model should refuse, not invent
    {
        "question": "What are the best sushi places in Tokyo?",
        "criteria": (
            "The answer must acknowledge it cannot answer because the data "
            "doesn't include Tokyo. It must NOT invent or recommend specific "
            "Tokyo restaurants or fabricate Japanese sushi details."
        ),
    },
    # 2. Happy path — basic retrieval + generation
    {
        "question": "What do customers say about beignets in New Orleans?",
        "criteria": (
            "The answer should summarize what reviewers actually say about "
            "beignets, grounded in the provided reviews with citations like "
            "[1], [2]. It should not be generic knowledge with no citations."
        ),
    },
    # 3. Specific entity — does vector search handle a proper noun?
    {
        "question": "What do reviewers think about Cafe du Monde?",
        "criteria": (
            "The answer should focus on Cafe du Monde specifically and "
            "summarize opinions about it with citations. It should not ignore "
            "the named business and answer about unrelated restaurants."
        ),
    },
    # 4. Multi-faceted — compound query (price + food + service)
    {
        "question": "What are some affordable seafood restaurants with good service?",
        "criteria": (
            "The answer should address all three aspects — affordability, "
            "seafood, and service quality — based on the reviews, with "
            "citations. Missing an aspect entirely is a partial failure."
        ),
    },
    # 5. Synonym / paraphrase — semantic match beyond keywords
    {
        "question": "Where should I take someone for a romantic evening?",
        "criteria": (
            "The answer should recommend places suited to a romantic evening, "
            "drawing on reviews describing ambiance (intimate, cozy, candlelit, "
            "quiet, etc.) even if the word 'romantic' never appears. Must be "
            "grounded in reviews with citations."
        ),
    },
    # 6. Negative sentiment — does it surface complaints, not just praise?
    {
        "question": "Which restaurants do customers complain about, and why?",
        "criteria": (
            "The answer should surface genuinely negative experiences (bad "
            "service, poor food, etc.) drawn from the reviews, with citations. "
            "Answering with only positive reviews is a failure."
        ),
    },
    # 7. Freshness — BLOCKED: needs a review_date column (see .rag-tutor/state.md)
    {
        "question": "What are the most recent complaints about restaurants?",
        "criteria": (
            "The answer should prioritize RECENT negative reviews over old "
            "ones. NOTE: cannot truly pass until retrieval is date-aware."
        ),
        "skip": "No review_date column yet — retrieval can't sort by recency. TODO Step 23.",
    },
]


def llm_judge(question, answer, criteria):
    judge_prompt = f"""You are evaluating an AI assistant's answer.

Question asked: {question}

Answer given: {answer}

Criteria the answer must meet: {criteria}

Did the answer meet the criteria? Respond with exactly "YES" or "NO" on the first line, then a one-sentence reason on the second line."""

    response = judge.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=150,
        messages=[{"role": "user", "content": judge_prompt}],
    )
    text = response.content[0].text.strip()
    lines = text.split("\n", 1)
    verdict = lines[0].strip().upper() == "YES"
    reason = lines[1].strip() if len(lines) > 1 else ""
    return verdict, reason


if __name__ == "__main__":
    passed_count = 0
    ran_count = 0

    for i, entry in enumerate(EVAL, start=1):
        print(f"\n=== Entry {i}: {entry['question']} ===")

        if "skip" in entry:
            print(f"SKIPPED — {entry['skip']}")
            continue

        ran_count += 1
        answer, _ = ask(entry["question"])      # ask() now returns (answer, reviews); ignore reviews here
        passed, reason = llm_judge(entry["question"], answer, entry["criteria"])

        print(f"\nAnswer:\n{answer}\n")
        print(f"Verdict: {'PASS' if passed else 'FAIL'}")
        print(f"Reason:  {reason}")

        if passed:
            passed_count += 1

    print(f"\n=== Summary: {passed_count}/{ran_count} passed ({len(EVAL) - ran_count} skipped) ===")