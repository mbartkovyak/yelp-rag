import os
from dotenv import load_dotenv
import snowflake.connector
import pandas as pd

load_dotenv()


def pull_reviews(limit = 1000):
    conn = snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
    )

    query = f"""
            select review_id, business_id, name, city, stars, text
            from fct_reviews
            where city like '%New Orleans%'
            and length(text) > 500
            limit {limit}
        """
    
    df = pd.read_sql(query, conn)

    conn.close()

    return df

if __name__ == "__main__":
    df = pull_reviews(limit=100)
    print(df.head(5))
    print(df.shape)


    




