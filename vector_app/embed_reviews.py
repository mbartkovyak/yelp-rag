import os
from dotenv import load_dotenv
from pathlib import Path
from openai import OpenAI
import psycopg2
from pgvector.psycopg2 import register_vector
from pull_reviews import pull_reviews


load_dotenv(Path(__file__).parent / ".env")

openai_client = OpenAI()   # reads OPENAI_API_KEY automatically

conn = psycopg2.connect(
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    dbname=os.getenv("POSTGRES_DB"),
)
register_vector(conn)   # tells psycopg2 to handle VECTOR types


df = pull_reviews(limit=100) # pulls 100 reviews from snowflake
print(f"pulled {len(df)} reviews")

texts = df["TEXT"].tolist() # grabs the TEXT column from the query and transforms it to the list of strings (python)

response = openai_client.embeddings.create(
    model="text-embedding-3-small",
    input=texts,
) # throws the text to open ai and defines the model used


embeddings = [item.embedding for item in response.data] # you only care about embedding itself, however response holds other attributes as well

print(len(embeddings), len(embeddings[0]))


cur = conn.cursor() # to connect to SQL that is running on the Docker

for i, row in df.iterrows():
    cur.execute(
        """
        INSERT INTO public.review_embeddings 
        (review_id, business_id, business_name, city, stars, text, embedding)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
                (
            row["REVIEW_ID"],
            row["BUSINESS_ID"],
            row["NAME"],
            row["CITY"],
            row["STARS"],
            row["TEXT"],
            embeddings[i],
        ),
        )
conn.commit()
cur.close()
conn.close()




