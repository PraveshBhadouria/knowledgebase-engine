import json

from database.connection import get_connection

from ingestion.shared.embedder import create_embedding

from ingestion.policy.store.embedding_formatter import (
    build_embedding_text,
)


def save_chunk(
    chunk,
    filename,
    metadata,
):
    """
    Save a policy chunk into the existing database schema.
    """

    print("\n" + "=" * 120)
    print("SAVING POLICY CHUNK")
    print("=" * 120)

    content = chunk.get(
        "content",
        "",
    ).strip()

    if not content:

        print("SKIPPING EMPTY CHUNK")

        print("=" * 120)

        return

    section_name = metadata.get(
        "section",
        "General",
    )

    page_start = metadata.get(
        "page_start",
        1,
    )

    page_end = metadata.get(
        "page_end",
        page_start,
    )

    print(f"DOCUMENT        : {filename}")

    print(
        f"DOCUMENT ID     : {metadata.get('document_id')}"
    )

    print(
        f"CHUNK ID        : {chunk.get('chunk_id')}"
    )

    print(
        f"CHUNK TYPE      : {chunk.get('chunk_type')}"
    )

    print(
        f"SECTION         : {section_name}"
    )

    print(
        f"CLAUSE ID       : {metadata.get('clause_id')}"
    )

    print(
        f"CLAUSE TITLE    : {metadata.get('clause_title')}"
    )

    print(
        f"PAGES           : {page_start} -> {page_end}"
    )

    print(
        f"WORD COUNT      : {len(content.split())}"
    )

    print(
        f"CHARACTERS      : {len(content)}"
    )

    print("\nCONTENT PREVIEW")
    print("-" * 100)

    print(content[:1000])

    if len(content) > 1000:

        print("\n...")

    print("-" * 100)

    # =====================================================
    # EMBEDDING
    # =====================================================

    print("\nBUILDING EMBEDDING TEXT")

    embedding_text = build_embedding_text(
        filename=filename,
        metadata=metadata,
        content=content,
    )

    print("\nGENERATING EMBEDDING...")

    embedding = create_embedding(
        embedding_text
    )

    if not embedding:

        print("FAILED TO GENERATE EMBEDDING")

        print("=" * 120)

        return

    print(
        f"EMBEDDING DIMENSION : {len(embedding)}"
    )

    print(
        f"FIRST 10 VALUES     : {embedding[:10]}"
    )

    # =====================================================
    # DATABASE
    # =====================================================

    print("\nCONNECTING TO DATABASE")

    conn = get_connection()

    cur = conn.cursor()

    try:

        print("\nINSERTING INTO document_chunks")

        cur.execute(
            """
            INSERT INTO document_chunks
            (
                document_id,
                section_name,
                chunk_type,
                keywords,
                page_start,
                page_end,
                metadata,
                created_by
            )
            VALUES
            (
                %s,
                %s,
                %s,
                to_tsvector('english',''),
                %s,
                %s,
                %s,
                %s
            )
            RETURNING id
            """,
            (
                metadata["document_id"],

                section_name,

                chunk.get(
                    "chunk_type",
                    "clause",
                ),

                page_start,

                page_end,

                json.dumps(metadata),

                "SYSTEM",
            ),
        )

        document_chunk_id = cur.fetchone()[0]

        print(
            f"document_chunks ID : {document_chunk_id}"
        )

        print("\nINSERTING INTO chunk_content")

        cur.execute(
            """
            INSERT INTO chunk_content
            (
                document_chunk_id,
                content,
                embedding,
                created_by
            )
            VALUES
            (
                %s,
                %s,
                %s::vector,
                %s
            )
            """,
            (
                document_chunk_id,

                content,

                str(embedding),

                "SYSTEM",
            ),
        )

        conn.commit()

        print("\nDATABASE COMMIT SUCCESSFUL")

        print(
            f"DOCUMENT CHUNK ID : {document_chunk_id}"
        )

        print(
            f"CONTENT LENGTH    : {len(content)}"
        )

        print(
            f"EMBEDDING SIZE    : {len(embedding)}"
        )

        print(
            f"SECTION           : {section_name}"
        )

        print(
            f"CLAUSE            : {metadata.get('clause_id')}"
        )

        print("\nPOLICY CHUNK SAVED SUCCESSFULLY")

    except Exception as e:

        conn.rollback()

        print("\n" + "=" * 120)

        print("DATABASE INSERT FAILED")

        print("=" * 120)

        print(f"ERROR TYPE : {type(e).__name__}")

        print(f"ERROR      : {e}")

        print("\nFAILED METADATA")

        print(
            json.dumps(
                metadata,
                indent=4,
                ensure_ascii=False,
            )
        )

        print("\nFAILED CONTENT")

        print(content[:1000])

        print("=" * 120)

        raise

    finally:

        cur.close()

        conn.close()

        print("\nDATABASE CONNECTION CLOSED")

        print("=" * 120)