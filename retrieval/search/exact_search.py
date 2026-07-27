import time

from database.connection import get_connection


def exact_search(
    query,
    document_id,
):

    total_start = time.perf_counter()

    print("\n" + "=" * 80)
    print("EXACT SEARCH")
    print("=" * 80)

    print(f"QUERY       : {query}")
    print(f"DOCUMENT ID : {document_id}")

    # ==========================================================
    # DATABASE CONNECTION
    # ==========================================================

    start = time.perf_counter()

    conn = get_connection()
    cur = conn.cursor()

    connection_time = (
        time.perf_counter() - start
    )

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
            cc.content

        FROM document_chunks dc

        JOIN chunk_content cc
            ON dc.id = cc.document_chunk_id

        WHERE
            dc.document_id = %s
            AND dc.is_active = TRUE
            AND cc.is_active = TRUE
            AND LOWER(cc.content) LIKE LOWER(%s)

        LIMIT 5
        """,
        (
            document_id,
            f"%{query}%",
        ),
    )

    sql_time = (
        time.perf_counter() - start
    )

    print(
        f"\n⏱ SQL Execution Time : {sql_time:.4f} sec"
    )

    # ==========================================================
    # FETCH RESULTS
    # ==========================================================

    start = time.perf_counter()

    rows = cur.fetchall()

    fetch_time = (
        time.perf_counter() - start
    )

    print(
        f"\n⏱ Fetch Time : {fetch_time:.4f} sec"
    )

    print(
        f"\nEXACT MATCHES : {len(rows)}"
    )

    cur.close()
    conn.close()

    total_time = (
        time.perf_counter() - total_start
    )

    print("\n" + "=" * 80)
    print("EXACT SEARCH PERFORMANCE")
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