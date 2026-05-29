# Yelp Review RAG

A retrieval-augmented generation (RAG) app that answers natural-language questions about
New Orleans restaurants, grounded in real Yelp reviews. Built as an end-to-end data project:
raw JSON → Snowflake → dbt → pgvector embeddings → retrieval → Claude → a Streamlit UI.

## Architecture

```
Yelp JSON (businesses, reviews, users, tips, checkins)
   │
   ▼  load into Snowflake (stage + COPY INTO)
RAW tables (VARIANT)
   │
   ▼  dbt staging  (views: stg_businesses, stg_reviews, stg_users, stg_tips, stg_checkins)
typed, cleaned, tested
   │
   ▼  dbt marts    (tables: dim_businesses, fct_reviews)
business-ready
   │
   ▼  pull_reviews.py  →  embed_reviews.py   (OpenAI text-embedding-3-small, 1536-dim)
pgvector store (review_embeddings)
   │
   ├──  retrieve.py   nearest-neighbour search (cosine distance)
   ├──  ask.py        retrieved reviews + question → Claude → grounded answer w/ citations
   ├──  eval.py       LLM-as-judge eval harness across failure-mode questions
   └──  app.py        Streamlit UI (answer + source reviews + k slider)
```

## The `vector_app/` files

| File | What it does |
|------|--------------|
| `pull_reviews.py` | Pulls reviews from the Snowflake `fct_reviews` mart (New Orleans, text > 500 chars) into a DataFrame. |
| `embed_reviews.py` | Embeds review text in batches via OpenAI, inserts into the `review_embeddings` pgvector table. |
| `retrieve.py` | `retrieve(question, k)` — embeds the question, returns the `k` nearest reviews by cosine distance. |
| `ask.py` | `ask(question, k)` — retrieves reviews, prompts Claude to answer using only those reviews, returns `(answer, reviews)`. |
| `eval.py` | Eval harness. Runs questions that probe specific RAG failure modes (hallucination, proper nouns, sentiment, etc.) and grades answers with an LLM judge. |
| `app.py` | Streamlit web UI on top of `ask()`. |

## Running it

**Prerequisites:** Python 3.9+, Docker, a Snowflake account with the dbt models built, and OpenAI + Anthropic API keys.

1. **Start pgvector** (Postgres with the vector extension):
   ```bash
   docker run -d --name yelp_pgvector \
     -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=yelp_rag \
     -p 5432:5432 pgvector/pgvector:pg16
   ```

2. **Create the table** (once), via `docker exec -it yelp_pgvector psql -U postgres -d yelp_rag`:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   CREATE TABLE review_embeddings (
     review_id     TEXT PRIMARY KEY,
     business_id   TEXT,
     business_name TEXT,
     city          TEXT,
     stars         INT,
     text          TEXT,
     embedding     VECTOR(1536)
   );
   ```

3. **Install deps and configure secrets:**
   ```bash
   pip install -r vector_app/requirements.txt
   cp vector_app/.env.example vector_app/.env   # then fill in real values
   ```

4. **Embed the reviews** (pulls from Snowflake, writes to pgvector):
   ```bash
   cd vector_app && python embed_reviews.py
   ```

5. **Launch the app:**
   ```bash
   cd vector_app && streamlit run app.py
   ```
   Opens at `http://localhost:8501`. Ask something like *"What do customers say about beignets?"*

## Evaluation

`eval.py` is a small eval harness. Instead of checking answers against a fixed string
(impossible — answers are generated text), each question carries a natural-language
`criteria`, and a Claude judge decides PASS/FAIL with a reason. The questions are chosen
to probe distinct RAG failure modes:

- **Honesty** — refuses on data it doesn't have (Tokyo sushi) instead of hallucinating
- **Happy path** — basic retrieval + generation (beignets)
- **Specific entity** — proper-noun retrieval (Café du Monde)
- **Multi-faceted** — compound query (affordable + seafood + service)
- **Synonym/paraphrase** — semantic match beyond keywords (romantic evening → intimate/cozy)
- **Negative sentiment** — surfaces complaints, not just praise

```bash
cd vector_app && python eval.py
```

## The dbt layer

The `models/` directory holds the dbt project (`yelp_1`): staging views one-per-source,
marts (`dim_businesses`, `fct_reviews`) as tables, with schema + data tests. Run with
`dbt run` and `dbt test`.
