from database.connection import get_connection

from ingestion.shared.keyword_extractor import (
    extract_keywords,
)


def generate_keywords(document_ids):

    if not document_ids:

        return {
            "status": "failed",
            "message": "No document ids provided",
        }

    conn = get_connection()
    cur = conn.cursor()

    total_documents = 0
    total_chunks = 0

    print("\n" + "=" * 120)
    print("KEYWORD GENERATION STARTED")
    print("=" * 120)

    try:

        for document_id in document_ids:

            print("\n" + "-" * 120)
            print(
                f"PROCESSING DOCUMENT ID: {document_id}"
            )
            print("-" * 120)

            cur.execute(
                """
                SELECT
                    dc.id,
                    cc.content
                FROM document_chunks dc
                JOIN chunk_content cc
                    ON cc.document_chunk_id = dc.id
                WHERE
                    dc.document_id = %s
                    AND dc.is_active = TRUE
                    AND cc.is_active = TRUE
                ORDER BY dc.id
                """,
                (document_id,),
            )

            rows = cur.fetchall()

            if not rows:

                print(
                    f"NO CHUNKS FOUND FOR DOCUMENT {document_id}"
                )

                continue

            processed_chunks = 0

            for chunk_id, content in rows:

                try:

                    print("\n" + "." * 80)

                    print(
                        f"CHUNK ID : {chunk_id}"
                    )

                    # ==================================================
                    # GENERATE KEYWORDS
                    # ==================================================

                    keywords = extract_keywords(
                        content
                    )

                    keywords_text = " ".join(
                        keywords
                    )

                    print(
                        f"KEYWORDS : {keywords}"
                    )

                    # ==================================================
                    # UPDATE KEYWORDS
                    # ==================================================

                    cur.execute(
                        """
                        UPDATE document_chunks
                        SET
                            keywords =
                                to_tsvector(
                                    'english',
                                    %s
                                ),
                            updated_at =
                                CURRENT_TIMESTAMP,
                            updated_by = %s
                        WHERE id = %s
                        """,
                        (
                            keywords_text,
                            "SYSTEM",
                            chunk_id,
                        ),
                    )

                    # ==================================================
                    # SAVE IMMEDIATELY
                    # ==================================================

                    conn.commit()

                    print(
                        f"CHUNK {chunk_id} SAVED SUCCESSFULLY"
                    )

                    processed_chunks += 1
                    total_chunks += 1

                except Exception as e:

                    conn.rollback()

                    print(
                        f"\nFAILED TO PROCESS CHUNK {chunk_id}"
                    )

                    print(
                        f"ERROR : {e}"
                    )

                    continue

            total_documents += 1

            print("\n" + "✓" * 80)

            print(
                f"DOCUMENT {document_id} COMPLETED"
            )

            print(
                f"CHUNKS PROCESSED : {processed_chunks}"
            )

            print("✓" * 80)

        print("\n" + "=" * 120)

        print(
            "KEYWORD GENERATION COMPLETED"
        )

        print(
            f"DOCUMENTS PROCESSED : {total_documents}"
        )

        print(
            f"TOTAL CHUNKS PROCESSED : {total_chunks}"
        )

        print("=" * 120)

        return {
            "status": "success",
            "documents_processed": total_documents,
            "chunks_processed": total_chunks,
        }

    except Exception as e:

        conn.rollback()

        print(
            f"\nKEYWORD GENERATION FAILED : {e}"
        )

        return {
            "status": "failed",
            "message": str(e),
        }

    finally:

        cur.close()
        conn.close()