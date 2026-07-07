from ingestion.text.hierarchy.layout_extractor import (
    extract_layout,
)

from ingestion.text.hierarchy.hierarchy_builder import (
    build_hierarchy,
)

from ingestion.text.chunking.text_chunker import (
    create_chunks,
)

pages = extract_layout(
    "test.pdf"
)

structured = build_hierarchy(
    pages
)

chunks = create_chunks(
    structured
)

print(
    "TOTAL CHUNKS:",
    len(chunks)
)

for chunk in chunks[:5]:

    print()

    print(
        "CHAPTER:",
        chunk["chapter"]
    )

    print(
        "SECTION:",
        chunk["section"]
    )

    print(
        "SUBSECTION:",
        chunk["subsection"]
    )

    print(
        "WORDS:",
        len(
            chunk["content"].split()
        )
    )

    print(
        chunk["content"][:300]
    )