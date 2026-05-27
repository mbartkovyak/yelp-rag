import os
from dotenv import load_dotenv
from pathlib import Path
from openai import OpenAI
import psycopg2
from pgvector.psycopg2 import register_vector
from pull_reviews import pull_reviews



load_dotenv(Path(__file__).parent / ".env")
openai_client = OpenAI()



def retrieve(question, k=5):
    # 1. Embed the question
    response = openai_client.embeddings.create(
        model="text-embedding-3-small",
        input=question,
    )
    query_embedding = response.data[0].embedding

    # 2. Connect to pgvector
    conn = psycopg2.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        dbname=os.getenv("POSTGRES_DB"),
    )
    register_vector(conn)
    cur = conn.cursor()

    # 3. Similarity search
    cur.execute(
        """
        SELECT review_id, business_name, city, stars, text
        FROM review_embeddings
        ORDER BY embedding <=> %s::vector
        LIMIT %s
        """,
        (query_embedding, k),
    )
    results = cur.fetchall()

    cur.close()
    conn.close()
    return results

if __name__ == "__main__":  # only executed when retrieve.py executed. If the function is imported somewhere else - it's not executed
    question = "Best coffee place"
    results = retrieve(question, k=5)
    for r in results:
        print(f"{r[3]}⭐ {r[1]} ({r[2]})")
        print(f"   {r[4][:250]}...")
        print()
