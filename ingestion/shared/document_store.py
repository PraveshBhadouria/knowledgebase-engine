from database.connection import get_connection


def create_document(
    filename,
    pdf_path,
    document_type,
    user_id=None,
):
    """
    Create a document record.

    Book Pipeline:
        user_id = None

    Policy Pipeline (Authenticated):
        user_id = Logged-in User ID
    """

    conn = get_connection()

    cur = conn.cursor()

    print("\n" + "=" * 120)
    print("CREATING DOCUMENT")
    print("=" * 120)

    print(f"FILE NAME     : {filename}")
    print(f"SOURCE PATH   : {pdf_path}")
    print(f"DOCUMENT TYPE : {document_type}")
    print(f"USER ID       : {user_id}")
    print(f"STATUS        : INDEXING")

    # =====================================================
    # INSERT WITHOUT USER
    # =====================================================

    if user_id is None:

        print("DOCUMENT OWNER : SYSTEM / LEGACY PIPELINE")

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
            ),
        )

    # =====================================================
    # INSERT WITH USER
    # =====================================================

    else:

        print(f"DOCUMENT OWNER : USER {user_id}")

        cur.execute(
            """
            INSERT INTO documents
            (
                document_name,
                source_path,
                document_type,
                user_id,
                status,
                created_by
            )
            VALUES
            (
                %s,
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
                user_id,
                "INDEXING",
                "SYSTEM",
            ),
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
    print(f"USER ID       : {user_id}")
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
        ),
    )

    conn.commit()

    print("\n" + "=" * 120)
    print("DOCUMENT STATUS UPDATED")
    print("=" * 120)

    print(f"DOCUMENT ID : {document_id}")
    print(f"NEW STATUS  : {status}")

    cur.close()
    conn.close()