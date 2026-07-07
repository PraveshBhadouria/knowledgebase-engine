from database.connection import get_connection
from ingestion.shared.embedder import create_embedding

import json


def save_chunk(
    chunk,
    filename,
    metadata,
):

    content = chunk.get(
        "content",
        "",
    ).strip()

    if not content:
        return

    word_count = len(content.split())

    if word_count < 10:

        print(
            f"SKIPPING SMALL CHUNK ({word_count} words)"
        )

        return

    section_name = (
        chunk.get("subsubsection")
        or chunk.get("subsection")
        or chunk.get("section")
        or "General"
    )

    if (
        section_name
        and section_name.upper() == "REFERENCES"
    ):
        return

    chunk_type = chunk.get(
        "chunk_type",
        "content",
    )

    page_start = chunk.get(
        "page_start",
        1,
    )

    page_end = chunk.get(
        "page_end",
        page_start,
    )

    if "node_id" not in metadata:
        raise ValueError(
            "node_id missing from metadata"
        )

    node_id = metadata["node_id"]

    embedding_text = f"""
Document: {filename}

Chapter:
{metadata.get('chapter', '')}

Section:
{metadata.get('section', '')}

Subsection:
{metadata.get('subsection', '')}

SubSubSection:
{metadata.get('subsubsection', '')}

Chunk Type:
{chunk_type}

Content:
{content}
"""

    print("\nGENERATING EMBEDDING")

    embedding = create_embedding(
        embedding_text
    )

    print(
        "Embedding Size:",
        len(embedding),
    )

    keywords_text = ""

    conn = get_connection()
    cur = conn.cursor()

    print("\nSAVING CHUNK")

    print(
        f"Document ID : {metadata['document_id']}"
    )

    print(
        f"Node ID     : {node_id}"
    )

    print(
        f"Chunk Type  : {chunk_type}"
    )

    print(
        f"Pages       : {page_start} -> {page_end}"
    )

    print(
        f"Section     : {section_name}"
    )

    # ======================================================
    # INSERT INTO document_chunks FIRST
    # ======================================================

    cur.execute(
        """
        INSERT INTO document_chunks
        (
            document_id,
            node_id,
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
            %s,
            to_tsvector('english', %s),
            %s,
            %s,
            %s,
            %s
        )
        RETURNING id
        """,
        (
            metadata["document_id"],
            node_id,
            section_name,
            chunk_type,
            keywords_text,
            page_start,
            page_end,
            json.dumps(metadata),
            "SYSTEM",
        ),
    )

    document_chunk_id = cur.fetchone()[0]

    print(
        f"DOCUMENT_CHUNKS INSERTED -> {document_chunk_id}"
    )

    # ======================================================
    # INSERT INTO chunk_content
    # ======================================================

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
        RETURNING id
        """,
        (
            document_chunk_id,
            content,
            str(embedding),
            "SYSTEM",
        ),
    )

    content_id = cur.fetchone()[0]

    print(
        f"CHUNK_CONTENT INSERTED -> {content_id}"
    )

    conn.commit()

    print(
        "DATABASE INSERT SUCCESS"
    )

    cur.close()
    conn.close()