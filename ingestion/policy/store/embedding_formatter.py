import json


def _format_list(title, values):
    """
    Convert a list into readable text.
    """

    if not values:
        return ""

    if isinstance(values, str):
        values = [values]

    values = [
        str(v).strip()
        for v in values
        if str(v).strip()
    ]

    if not values:
        return ""

    return f"{title}: {', '.join(values)}"


def build_embedding_text(
    filename,
    metadata,
    content,
):
    """
    Convert policy metadata into natural language
    before generating embeddings.
    """

    print("\n" + "=" * 120)
    print("BUILDING EMBEDDING TEXT")
    print("=" * 120)

    print(f"DOCUMENT      : {filename}")
    print(f"SECTION       : {metadata.get('section')}")
    print(f"CLAUSE ID     : {metadata.get('clause_id')}")
    print(f"CLAUSE TITLE  : {metadata.get('clause_title')}")
    print(f"CHUNK TYPE    : {metadata.get('chunk_type')}")
    print(
        f"PAGES         : {metadata.get('page_start')} -> {metadata.get('page_end')}"
    )

    semantic = metadata.get(
        "semantic",
        {},
    )

    print("\nSEMANTIC METADATA")
    print("-" * 100)

    print(
        json.dumps(
            semantic,
            indent=4,
            ensure_ascii=False,
        )
    )

    print("-" * 100)

    lines = []

    # =====================================================
    # Document Information
    # =====================================================

    lines.append(
        f"Document Name: {filename}"
    )

    lines.append(
        "Document Type: Insurance Policy"
    )

    lines.append("")

    # =====================================================
    # Structure
    # =====================================================

    section = metadata.get(
        "section",
        "",
    )

    if section:

        lines.append(
            f"Section: {section}"
        )

    clause = metadata.get(
        "clause_id",
        "",
    )

    if clause:

        lines.append(
            f"Clause: {clause}"
        )

    clause_title = metadata.get(
        "clause_title",
        "",
    )

    if clause_title:

        lines.append(
            f"Clause Title: {clause_title}"
        )

    page_start = metadata.get(
        "page_start",
        1,
    )

    page_end = metadata.get(
        "page_end",
        page_start,
    )

    lines.append(
        f"Pages: {page_start}-{page_end}"
    )

    lines.append("")

    # =====================================================
    # Semantic Metadata
    # =====================================================

    semantic_lines = []

    semantic_lines.append(
        _format_list(
            "Benefits",
            semantic.get(
                "benefits",
                [],
            ),
        )
    )

    semantic_lines.append(
        _format_list(
            "Exclusions",
            semantic.get(
                "exclusions",
                [],
            ),
        )
    )

    semantic_lines.append(
        _format_list(
            "Coverage Amounts",
            semantic.get(
                "money",
                [],
            ),
        )
    )

    semantic_lines.append(
        _format_list(
            "Waiting Period",
            semantic.get(
                "waiting_period",
                [],
            ),
        )
    )

    semantic_lines.append(
        _format_list(
            "Age",
            semantic.get(
                "age",
                [],
            ),
        )
    )

    semantic_lines.append(
        _format_list(
            "Percentages",
            semantic.get(
                "percentage",
                [],
            ),
        )
    )

    semantic_lines = [
        line
        for line in semantic_lines
        if line
    ]

    if semantic_lines:

        lines.append(
            "Extracted Information:"
        )

        lines.extend(
            semantic_lines
        )

        lines.append("")

    # =====================================================
    # Actual Content
    # =====================================================

    lines.append(
        "Policy Content:"
    )

    lines.append(content)

    embedding_text = "\n".join(lines)

    # =====================================================
    # LOG FINAL EMBEDDING
    # =====================================================

    print("\nFINAL EMBEDDING TEXT")
    print("=" * 120)

    print(embedding_text)

    print("=" * 120)

    print(
        f"WORDS      : {len(embedding_text.split())}"
    )

    print(
        f"CHARACTERS : {len(embedding_text)}"
    )

    print("=" * 120)
    print("EMBEDDING TEXT READY")
    print("=" * 120)

    return embedding_text