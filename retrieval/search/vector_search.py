import time

from database.connection import get_connection

from ingestion.shared.embedder import (
    create_embedding,
)


def vector_search(
    query,
    document_id,
):

    total_start = time.perf_counter()

    # ==========================================================
    # EMBEDDING GENERATION
    # ==========================================================

    start = time.perf_counter()

    embedding = create_embedding(query)

    embedding_time = (
        time.perf_counter() - start
    )

    print(
        f"\n⏱ Embedding Generation Time : {embedding_time:.4f} sec"
    )

    print("\n" + "=" * 80)
    print("VECTOR SEARCH")
    print("=" * 80)

    print(f"QUERY       : {query}")
    print(f"DOCUMENT ID : {document_id}")

    # ==========================================================
    # DATABASE SEARCH
    # ==========================================================

    start = time.perf_counter()

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

        WHERE
            dc.document_id = %s
            AND dc.is_active = TRUE
            AND cc.is_active = TRUE
            AND cc.embedding <=> %s::vector < 0.7

        ORDER BY
            distance

        LIMIT 30
        """,
        (
            str(embedding),
            document_id,
            str(embedding),
        ),
    )

    rows = cur.fetchall()

    db_time = (
        time.perf_counter() - start
    )

    print(
        f"\n⏱ Database Vector Search Time : {db_time:.4f} sec"
    )

    print(f"\nVECTOR MATCHES : {len(rows)}")

    for row in rows[:10]:

        print(f"\nChunk ID : {row[0]}")
        print(f"Section  : {row[1]}")
        print(f"Distance : {row[3]:.6f}")

    cur.close()
    conn.close()

    total_time = (
        time.perf_counter() - total_start
    )

    print("\n" + "=" * 80)
    print("VECTOR SEARCH PERFORMANCE")
    print("=" * 80)
    print(
        f"Embedding Generation : {embedding_time:.4f} sec"
    )
    print(
        f"Database Search      : {db_time:.4f} sec"
    )
    print(
        f"Total Vector Search  : {total_time:.4f} sec"
    )
    print("=" * 80)

    return rows