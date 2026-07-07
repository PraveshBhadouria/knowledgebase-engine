from database.connection import get_connection


def exact_search(query):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            dc.id,
            dc.section_name,
            cc.content

        FROM document_chunks dc

        JOIN chunk_content cc
            ON dc.id = cc.document_chunk_id

        WHERE LOWER(cc.content)
        LIKE LOWER(%s)

        LIMIT 5
        """,
        (f"%{query}%",),
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return rows