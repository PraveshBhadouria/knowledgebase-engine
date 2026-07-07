# tests/test_hierarchy.py

from ingestion.text.hierarchy.layout_extractor import (
    extract_layout,
)

from ingestion.text.hierarchy.hierarchy_builder import (
    build_hierarchy,
)

pages = extract_layout(
    "Business Management And Organization Booklet.pdf"
)

structured = build_hierarchy(
    pages
)

for page in structured:

    print("\n" + "=" * 80)
    print("PAGE:", page["page"])
    print("=" * 80)

    for item in page["elements"]:

        if (
            item["chapter"]
            or item["section"]
            or item["subsection"]
        ):

            print("\nTEXT:", item["text"])

            print("CHAPTER:", item["chapter"])

            print("SECTION:", item["section"])

            print("SUBSECTION:", item["subsection"])