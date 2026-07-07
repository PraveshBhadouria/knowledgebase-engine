from database.connection import get_connection

def create_document(
    filename,
    pdf_path,
    document_type,
):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO documents
        (
            document_name,
            source_path,
            document_type,
            status,
            created_by
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s
        )
        RETURNING id
        """,
        (
            filename,
            pdf_path,
            document_type,
            "INDEXING",
            "SYSTEM",
        )
    )

    document_id = cur.fetchone()[0]

    conn.commit()

    print("\n" + "=" * 120)
    print("DOCUMENT CREATED")
    print("=" * 120)

    print(f"DOCUMENT ID   : {document_id}")
    print(f"FILE NAME     : {filename}")
    print(f"SOURCE PATH   : {pdf_path}")
    print(f"DOCUMENT TYPE : {document_type}")
    print(f"STATUS        : INDEXING")

    cur.close()
    conn.close()

    return document_id


def update_document_status(
    document_id,
    status,
):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE documents
        SET
            status = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
        """,
        (
            status,
            document_id,
        )
    )

    conn.commit()

    print(f"\nDOCUMENT {document_id} STATUS UPDATED TO: {status}")

    cur.close()
    conn.close()