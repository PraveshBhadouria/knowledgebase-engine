import json


def build_metadata(
    chunk,
    document_id,
):
    """
    Build metadata for policy chunks.

    This metadata is stored in document_chunks.metadata.
    """

    print("\n" + "=" * 120)
    print("BUILDING CHUNK METADATA")
    print("=" * 120)

    print(
        f"DOCUMENT ID   : {document_id}"
    )

    print(
        f"CHUNK ID      : {chunk.get('chunk_id')}"
    )

    print(
        f"CHUNK TYPE    : {chunk.get('chunk_type')}"
    )

    print(
        f"SECTION       : {chunk.get('section')}"
    )

    print(
        f"CLAUSE ID     : {chunk.get('clause_id')}"
    )

    print(
        f"CLAUSE TITLE  : {chunk.get('clause_title')}"
    )

    print(
        f"PAGES         : {chunk.get('page_start')} -> {chunk.get('page_end')}"
    )

    content = chunk.get(
        "content",
        "",
    )

    print(
        f"WORD COUNT    : {len(content.split())}"
    )

    semantic = chunk.get(
        "metadata",
        {},
    )

    print(
        f"SEMANTIC KEYS : {list(semantic.keys())}"
    )

    metadata = {

        # =====================================================
        # Generic Information
        # =====================================================

        "document_id": document_id,

        "document_type": "POLICY",

        "chunk_id": chunk.get(
            "chunk_id",
        ),

        "chunk_type": chunk.get(
            "chunk_type",
            "clause",
        ),

        # =====================================================
        # Policy Structure
        # =====================================================

        "section": chunk.get(
            "section",
            "General",
        ),

        "clause_id": chunk.get(
            "clause_id",
            "",
        ),

        "clause_title": chunk.get(
            "clause_title",
            "",
        ),

        # =====================================================
        # Page Information
        # =====================================================

        "page_start": chunk.get(
            "page_start",
            1,
        ),

        "page_end": chunk.get(
            "page_end",
            chunk.get(
                "page_start",
                1,
            ),
        ),

        # =====================================================
        # Chunk Statistics
        # =====================================================

        "word_count": len(
            content.split()
        ),

        "character_count": len(
            content
        ),

        # =====================================================
        # Semantic Metadata
        # =====================================================

        "semantic": semantic,

    }

    print("\nFINAL METADATA")

    print("-" * 120)

    print(
        json.dumps(
            metadata,
            indent=4,
            ensure_ascii=False,
        )
    )

    print("-" * 120)

    print("METADATA BUILD COMPLETE")

    print("=" * 120)

    return metadata