import re

MAX_WORDS = 450

SPECIAL_TYPES = {
    "workflow",
    "business_rule",
    "definition",
    "formula",
    "table",
    "figure",
    "example",
    "key_point",
    "decision_tree",
    "relationship",
    "database_mapping",
}


def split_content(
    text,
    max_words=MAX_WORDS,
):

    paragraphs = re.split(
        r"\n+",
        text,
    )

    chunks = []

    current_chunk = []

    current_words = 0

    for para in paragraphs:

        para_words = len(
            para.split()
        )

        if (
            current_words + para_words > max_words
            and current_chunk
        ):

            chunks.append(
                "\n".join(current_chunk)
            )

            current_chunk = []

            current_words = 0

        current_chunk.append(
            para
        )

        current_words += para_words

    if current_chunk:

        chunks.append(
            "\n".join(current_chunk)
        )

    return chunks


def create_chunks(units):

    chunks = []

    node_map = {}

    next_node_id = 1

    grouped_content = {}

    print(
        "\n" + "=" * 120
    )

    print(
        "STARTING CHUNK CREATION"
    )

    print(
        "=" * 120
    )

    for unit in units:

        unit_type = unit["type"]

        if unit_type == "learning_outcome":
            continue

        content = (
            unit["content"]
            .strip()
        )

        if not content:
            continue

        chapter = unit.get(
            "chapter",
            "",
        )

        section = unit.get(
            "section",
            "",
        )

        subsection = unit.get(
            "subsection",
            "",
        )

        subsubsection = unit.get(
            "subsubsection",
            "",
        )

        node_key = (
            chapter,
            section,
            subsection,
            subsubsection,
        )

        if node_key not in node_map:

            node_map[node_key] = (
                next_node_id
            )

            next_node_id += 1

        node_id = node_map[node_key]

        print("\nNODE ASSIGNED")

        print(
            f"NODE ID: {node_id}"
        )

        print(
            f"PAGE: {unit['page']}"
        )

        print(
            f"TYPE: {unit_type}"
        )

        print(
            f"CHAPTER: {chapter}"
        )

        print(
            f"SECTION: {section}"
        )

        print(
            f"SUBSECTION: {subsection}"
        )

        print(
            f"SUBSUBSECTION: {subsubsection}"
        )

        print(
            f"TEXT: {content[:200]}"
        )

        if unit_type in SPECIAL_TYPES:

            chunks.append(
                {
                    "node_id": node_id,
                    "page_start": unit["page"],
                    "page_end": unit["page"],
                    "chapter": chapter,
                    "section": section,
                    "subsection": subsection,
                    "subsubsection": subsubsection,
                    "chunk_type": unit_type,
                    "content": content,
                }
            )

            continue

        if node_key not in grouped_content:

            grouped_content[node_key] = {
                "node_id": node_id,
                "page_start": unit["page"],
                "page_end": unit["page"],
                "chapter": chapter,
                "section": section,
                "subsection": subsection,
                "subsubsection": subsubsection,
                "content": [],
            }

        grouped_content[node_key][
            "page_end"
        ] = unit["page"]

        print(
            f"\nADDING CONTENT TO NODE {node_id}"
        )

        print(
            f"PAGE={unit['page']}"
        )

        print(
            f"WORDS={len(content.split())}"
        )

        print(
            content[:250]
        )

        grouped_content[node_key][
            "content"
        ].append(content)

    for node_data in grouped_content.values():

        full_content = "\n".join(
            node_data["content"]
        )

        print(
            "\n" + "#" * 120
        )

        print(
            "NODE SUMMARY"
        )

        print(
            f"NODE ID: {node_data['node_id']}"
        )

        print(
            f"PAGE START: {node_data['page_start']}"
        )

        print(
            f"PAGE END: {node_data['page_end']}"
        )

        print(
            f"CHAPTER: {node_data['chapter']}"
        )

        print(
            f"SECTION: {node_data['section']}"
        )

        print(
            f"SUBSECTION: {node_data['subsection']}"
        )

        print(
            f"SUBSUBSECTION: {node_data['subsubsection']}"
        )

        print(
            f"TOTAL WORDS: {len(full_content.split())}"
        )

        print(
            "#" * 120
        )

        split_chunks = split_content(
            full_content
        )

        for chunk_text in split_chunks:

            chunks.append(
                {
                    "node_id": node_data["node_id"],
                    "page_start": node_data["page_start"],
                    "page_end": node_data["page_end"],
                    "chapter": node_data["chapter"],
                    "section": node_data["section"],
                    "subsection": node_data["subsection"],
                    "subsubsection": node_data["subsubsection"],
                    "chunk_type": "content",
                    "content": chunk_text,
                }
            )

    print(
        f"\nFINAL CHUNKS CREATED: {len(chunks)}"
    )

    return chunks