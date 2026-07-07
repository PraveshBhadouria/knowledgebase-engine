import re


def normalize_text(structured_pages):

    units = []

    for page in structured_pages:

        if not page["elements"]:
            continue

        page_number = page["page"]

        for item in page["elements"]:

            text = item["text"].strip()

            text = re.sub(
                r"\s+",
                " ",
                text
            ).strip()

            if not text:
                continue

            if re.search(
                r"\.{5,}\s*\d+$",
                text,
            ):
                continue

            if text.lower().startswith(
                "© regenesys"
            ):
                continue

            if text.isdigit():
                continue

            unit_type = item.get(
                "heading_type"
            )

            if not unit_type:
                unit_type = "paragraph"

            print("\nUNIT CREATED")

            print(
                f"PAGE={page_number}"
            )

            print(
                f"TYPE={unit_type}"
            )

            print(
                f"CHAPTER={item['chapter']}"
            )

            print(
                f"SECTION={item['section']}"
            )

            print(
                f"SUBSECTION={item['subsection']}"
            )

            print(
                f"SUBSUBSECTION={item.get('subsubsection', '')}"
            )

            print(
                f"TEXT={text[:150]}"
            )

            units.append(
                {
                    "page": page_number,
                    "chapter": item["chapter"],
                    "section": item["section"],
                    "subsection": item["subsection"],
                    "subsubsection": item.get(
                        "subsubsection",
                        "",
                    ),
                    "type": unit_type,
                    "content": text,
                }
            )

    print(
        "\nTEXT NORMALIZATION COMPLETE"
    )

    print(
        f"TOTAL UNITS: {len(units)}"
    )

    return units