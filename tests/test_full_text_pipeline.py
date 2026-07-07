from ingestion.text.hierarchy.layout_extractor import (
    extract_layout,
)

from ingestion.text.hierarchy.hierarchy_builder import (
    build_hierarchy,
)

from ingestion.text.text_normalizer import (
    normalize_text,
)

from ingestion.shared.rule_chunker import (
    create_chunks,
)

PDF_PATH = "Business Management And Organization Booklet.pdf"

print("\n" + "=" * 80)
print("LAYOUT EXTRACTION")
print("=" * 80)

layout_pages = extract_layout(
    PDF_PATH
)

print("\n" + "=" * 80)
print("HIERARCHY BUILDING")
print("=" * 80)

structured_pages = build_hierarchy(
    layout_pages
)

print("\n" + "=" * 80)
print("NORMALIZATION")
print("=" * 80)

units = normalize_text(
    structured_pages
)

print(
    f"\nTOTAL UNITS: {len(units)}"
)

print("\n" + "=" * 80)
print("CHUNKING")
print("=" * 80)

chunks = create_chunks(
    units
)

print("\n")
print("=" * 80)
print("TOTAL CHUNKS")
print("=" * 80)

print(len(chunks))

for i, chunk in enumerate(
    chunks[:20],
    start=1,
):

    print("\n")
    print("=" * 80)
    print(f"CHUNK {i}")
    print("=" * 80)

    print(
        "PAGE:",
        chunk.get("page"),
    )

    print(
        "TYPE:",
        chunk.get("chunk_type"),
    )

    print(
        "CHAPTER:",
        chunk.get("chapter"),
    )

    print(
        "SECTION:",
        chunk.get("section"),
    )

    print(
        "SUBSECTION:",
        chunk.get("subsection"),
    )

    print(
        "WORDS:",
        len(
            chunk["content"].split()
        ),
    )

    print("\nCONTENT:\n")

    print(
        chunk["content"][:1000]
    )