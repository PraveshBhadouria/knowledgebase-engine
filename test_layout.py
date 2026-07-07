from ingestion.text.hierarchy.layout_extractor import (
    extract_layout,
)

from ingestion.text.hierarchy.hierarchy_builder import (
    build_hierarchy,
)

from ingestion.text.text_normalizer import (
    normalize_text,
)


PDF_PATH = "MBA_INV_SG_2026_v1_e_f 2.pdf"


print("\n" + "=" * 120)
print("STEP 1 : EXTRACTING LAYOUT")
print("=" * 120)

layout = extract_layout(
    PDF_PATH,
)

print("\n" + "=" * 120)
print("LAYOUT SUMMARY")
print("=" * 120)

print(f"TOTAL LAYOUT PAGES : {len(layout)}")

for page in layout:

    print(
        f"PAGE {page['page']} -> "
        f"{len(page['elements'])} ELEMENTS"
    )


print("\n" + "=" * 120)
print("STEP 2 : BUILDING HIERARCHY")
print("=" * 120)

structured_pages, reference_pages = build_hierarchy(
    layout
)

print("\n" + "=" * 120)
print("HIERARCHY SUMMARY")
print("=" * 120)

print(
    f"TOTAL STRUCTURED PAGES : "
    f"{len(structured_pages)}"
)

print(
    f"TOTAL REFERENCE PAGES : "
    f"{len(reference_pages)}"
)

for page in structured_pages:

    print("\n" + "-" * 100)

    print(
        f"PAGE : {page['page']}"
    )

    print(
        f"ELEMENT COUNT : "
        f"{len(page['elements'])}"
    )

    for element in page["elements"]:

        print(
            f"\nTEXT        : "
            f"{element['text']}"
        )

        print(
            f"HEADING TYPE: "
            f"{element.get('heading_type', '')}"
        )

        print(
            f"CHAPTER     : "
            f"{element.get('chapter', '')}"
        )

        print(
            f"SECTION     : "
            f"{element.get('section', '')}"
        )

        print(
            f"SUBSECTION  : "
            f"{element.get('subsection', '')}"
        )

        print(
            f"SUBSUBSECTION : "
            f"{element.get('subsubsection', '')}"
        )


print("\n" + "=" * 120)
print("STEP 3 : NORMALIZATION")
print("=" * 120)

units = normalize_text(
    structured_pages
)

print("\n" + "=" * 120)
print("NORMALIZATION SUMMARY")
print("=" * 120)

print(
    f"TOTAL UNITS CREATED : "
    f"{len(units)}"
)

for index, unit in enumerate(
    units,
    start=1,
):

    print("\n" + "#" * 100)

    print(
        f"UNIT #{index}"
    )

    print(
        f"PAGE : {unit['page']}"
    )

    print(
        f"TYPE : {unit['type']}"
    )

    print(
        f"CHAPTER : "
        f"{unit['chapter']}"
    )

    print(
        f"SECTION : "
        f"{unit['section']}"
    )

    print(
        f"SUBSECTION : "
        f"{unit['subsection']}"
    )

    print(
        f"SUBSUBSECTION : "
        f"{unit['subsubsection']}"
    )

    print(
        f"CONTENT :\n"
        f"{unit['content'][:300]}"
    )

print("\n" + "=" * 120)
print("DEBUG COMPLETE")
print("=" * 120)