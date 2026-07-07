from database.connection import get_connection

from ingestion.shared.embedder import (
    create_embedding,
)


def vector_search(query):

    embedding = create_embedding(query)

    print("\nVECTOR SEARCH")

    print(
        "Query:",
        query,
    )

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            dc.id,
            dc.section_name,
            cc.content,

            cc.embedding <=> %s::vector
            AS distance

        FROM document_chunks dc

        JOIN chunk_content cc
            ON dc.id = cc.document_chunk_id

        WHERE cc.embedding <=> %s::vector
              < 0.7

        ORDER BY distance

        LIMIT 30
        """,
        (
            str(embedding),
            str(embedding),
        ),
    )

    rows = cur.fetchall()

    print(
        "Retrieved:",
        len(rows),
    )

    cur.close()
    conn.close()

    return rows