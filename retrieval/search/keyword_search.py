import time

from database.connection import get_connection


def keyword_search(
    query_keywords,
    document_id,
):

    total_start = time.perf_counter()

    print("\n" + "=" * 80)
    print("KEYWORD SEARCH")
    print("=" * 80)

    print(f"DOCUMENT ID : {document_id}")

    print("\nQUERY KEYWORDS")

    for keyword in query_keywords:
        print(f"- {keyword}")

    query_text = " ".join(query_keywords)

    # ==========================================================
    # DATABASE CONNECTION
    # ==========================================================

    start = time.perf_counter()

    conn = get_connection()
    cur = conn.cursor()

    connection_time = time.perf_counter() - start

    print(
        f"\n⏱ Database Connection Time : {connection_time:.4f} sec"
    )

    # ==========================================================
    # SQL EXECUTION
    # ==========================================================

    start = time.perf_counter()

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

        WHERE
            dc.document_id = %s
            AND dc.is_active = TRUE
            AND cc.is_active = TRUE
            AND dc.keywords @@
                plainto_tsquery('english', %s)

        ORDER BY
            keyword_score DESC

        LIMIT 20
        """,
        (
            query_text,
            document_id,
            query_text,
        ),
    )

    sql_time = time.perf_counter() - start

    print(
        f"\n⏱ SQL Execution Time : {sql_time:.4f} sec"
    )

    # ==========================================================
    # FETCH RESULTS
    # ==========================================================

    start = time.perf_counter()

    rows = cur.fetchall()

    fetch_time = time.perf_counter() - start

    print(
        f"\n⏱ Fetch Time : {fetch_time:.4f} sec"
    )

    print(
        f"\nKEYWORD MATCHES : {len(rows)}"
    )

    for row in rows[:10]:

        print(f"\nChunk ID      : {row[0]}")
        print(f"Section       : {row[1]}")
        print(f"Keyword Score : {row[3]:.4f}")

    cur.close()
    conn.close()

    total_time = time.perf_counter() - total_start

    print("\n" + "=" * 80)
    print("KEYWORD SEARCH PERFORMANCE")
    print("=" * 80)
    print(
        f"Connection Time : {connection_time:.4f} sec"
    )
    print(
        f"SQL Time        : {sql_time:.4f} sec"
    )
    print(
        f"Fetch Time      : {fetch_time:.4f} sec"
    )
    print(
        f"Total Time      : {total_time:.4f} sec"
    )
    print("=" * 80)

    return rows