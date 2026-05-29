# RAG project — where we left off

## Where the code actually lives

`/Users/myro/Public/snowflake_project1/yelp_1/`
The dbt project root. Conductor workspace is just where Claude runs — the project survived the abuja workspace deletion.

The RAG app: `yelp_1/vector_app/`

## Stack

- **Source data:** Yelp reviews → Snowflake → dbt → `fct_reviews` mart
- **Embeddings:** OpenAI `text-embedding-3-small` (1536 dims)
- **Vector store:** Postgres + pgvector (running locally in Docker)
- **Generator:** Claude (`claude-sonnet-4-6`)

## Files in `vector_app/`

| File | Status | What it does |
|------|--------|--------------|
| `pull_reviews.py` | ✅ done | Pulls reviews from Snowflake `fct_reviews`, filtered to New Orleans, text > 500 chars. Function: `pull_reviews(limit=1000)` returns a pandas DataFrame. |
| `embed_reviews.py` | ✅ done | Script (not a function). Pulls 10k reviews, embeds in batches of 100, inserts into pgvector table `review_embeddings` with `ON CONFLICT DO NOTHING`. |
| `retrieve.py` | ✅ done | Function `retrieve(question, k=5)` → embeds the question, runs `ORDER BY embedding <=> %s::vector LIMIT %s`, returns list of tuples `(review_id, business_name, city, stars, text)`. |
| `ask.py` | ✅ done + tested | Function `ask(question, k=5)` → calls `retrieve()`, formats reviews as `[i] (5⭐ Name, City) "text"`, builds RAG prompt, calls Claude, returns answer text. |

## Postgres table schema

```sql
CREATE TABLE review_embeddings (
  review_id TEXT PRIMARY KEY,
  business_id TEXT,
  business_name TEXT,
  city TEXT,
  stars INT,
  text TEXT,
  embedding VECTOR(1536)
);
```

## `.env` keys (in vector_app/.env)

```
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD, SNOWFLAKE_WAREHOUSE, SNOWFLAKE_DATABASE, SNOWFLAKE_SCHEMA
```

## Tutorial step tracker

**Completed:** Steps 1–22.
- 1–20: Snowflake load → dbt → pgvector → embed → retrieve → ask.
- 21: Eval harness (`eval.py`) — LLM-as-judge over 6 failure-mode questions + 1 skipped (freshness, blocked on date column). Ran green.
- 22: Streamlit UI (`app.py`) + repo polish (`requirements.txt`, `.env.example`, rewritten root `README.md`). `ask()` refactored to return `(answer, reviews)`; callers in `eval.py` + `ask.py` updated. Streamlit boots clean (health ok), end-to-end verified.

**Not yet committed/pushed to GitHub** as of 2026-05-29. `.env` confirmed gitignored. Open decision: whether to commit `.rag-tutor/` (tutor metadata) or gitignore it.

**Step 21 (historical note) — Eval harness.** Order was: eval first (B), then Streamlit (A).

Eval set design — 7 questions, each probing a specific RAG failure mode:
1. Happy path → beignets
2. Specific entity → Café du Monde (or similar known NOLA spot in data)
3. Honesty/refusal → Tokyo sushi (data only has NOLA — model should refuse, not invent)
4. Multi-faceted → affordable seafood with good service
5. Synonym/paraphrase → romantic date (vector should catch candlelit/intimate/cozy)
6. Negative sentiment → restaurants people complain about
7. **Freshness (BLOCKED on date column)** → tests whether retrieval surfaces stale 5-star reviews when newer 1-star reviews exist. Requires `review_date` column not yet in `review_embeddings`. To unblock: pull date from Snowflake `fct_reviews`, ALTER TABLE, backfill. Eval entry to be written with `# TODO` comment.

Storage: eval entries as a Python list of dicts inside `vector_app/eval.py`.

**Planned after eval harness:**
- Step 22 — Streamlit UI on top of `ask()`
- Step 23 — Add date column + run freshness eval (unblocks #7)
- Step 24 — Hybrid retrieval (vector + BM25) or metadata filters
- Step 25 — Streaming responses
- Step 26 — Citation parser (link [1], [2] back to displayed reviews)

## Teaching mode for this user

From auto-memory:
- **Coach mode** — explain shapes/concepts, don't paste full code blocks for him to copy. He writes the code.
- **AI-first for repeated patterns** — if Claude is writing the 4th near-identical staging model or copy-paste boilerplate, Claude writes, Myro reviews. First instances are still concept-teaching.
- **Simpler prose** — define jargon inline, one concept per response, match question's scope.
- **No projecting Amazon BIE experience** onto modern-stack patterns (dbt, RAG, etc.) — ask first.
- Pace: he interrupts with "next piece" or "not that slow, I can process more" — let him drive cadence.

## Where the original chat history lives

The deleted abuja workspace's `.jsonl` chat files are still on disk:
`~/.claude/projects/-Users-myro-conductor-workspaces-llm-playground-abuja/`

Main RAG thread: `c1fadbc9-daa2-4df6-b9b9-ee8547c0f30f.jsonl` (5.6 MB, 582 substantive messages, May 6 → May 27)
Earlier RAG concepts intro: `e76250ab-7461-44f0-baf1-282a9bc034c5.jsonl` (61 KB, May 6 morning)
