import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_connection():

    conn = psycopg2.connect(
        host=os.getenv("PGHOST"),
        database=os.getenv("PGDATABASE"),
        user=os.getenv("PGUSER"),
        password=os.getenv("PGPASSWORD"),
        port=os.getenv("PGPORT"),
    )

    # with conn.cursor() as cur:
    #     cur.execute(
    #         "SET search_path TO knowledge_base, public"
    #     )

    return conn