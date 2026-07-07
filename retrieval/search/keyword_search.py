from database.connection import get_connection


def keyword_search(query_keywords):

    print("\nQUERY KEYWORDS")

    for keyword in query_keywords:

        print(f"- {keyword}")

    query_text = " ".join(query_keywords)

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            dc.id,
            dc.section_name,
            cc.content,

            ts_rank(
                dc.keywords,
                plainto_tsquery('english', %s)
            ) AS keyword_score

        FROM document_chunks dc

        JOIN chunk_content cc
            ON dc.id = cc.document_chunk_id

        WHERE dc.keywords @@
              plainto_tsquery('english', %s)

        ORDER BY keyword_score DESC

        LIMIT 20
        """,
        (
            query_text,
            query_text,
        ),
    )

    rows = cur.fetchall()

    print(
        "\nKEYWORD MATCHES:",
        len(rows)
    )

    for row in rows[:10]:

        print(f"\nChunk={row[0]}")

        print(
            f"Keyword Score={row[3]:.4f}"
        )

    cur.close()
    conn.close()

    return rows