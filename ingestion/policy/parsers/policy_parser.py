import re


def normalize_text(text):

    if not text:
        return ""

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def parse_policy(pages):

    """
    Convert extracted policy pages into semantic units.
    """

    print("\n" + "=" * 120)
    print("POLICY PARSER STARTED")
    print("=" * 120)

    units = []

    paragraph_count = 0
    table_count = 0

    # =====================================================
    # PROCESS EACH PAGE
    # =====================================================

    for page in pages:

        print("\n" + "=" * 120)
        print(f"PAGE {page['page']}")
        print("=" * 120)

        current_section = "General"
        current_clause_id = ""
        current_clause_title = ""

        print(
            f"TEXT ELEMENTS : {len(page['elements'])}"
        )

        print(
            f"TABLES        : {len(page.get('detected_tables', []))}"
        )

        # =====================================================
        # TEXT ELEMENTS
        # =====================================================

        for index, element in enumerate(
            page["elements"],
            start=1,
        ):

            text = normalize_text(
                element.get(
                    "text",
                    "",
                )
            )

            if not text:
                continue

            current_section = element.get(
                "section",
                current_section,
            )

            current_clause_id = element.get(
                "clause_id",
                current_clause_id,
            )

            current_clause_title = element.get(
                "clause_title",
                current_clause_title,
            )

            unit = {

                "page": page["page"],

                "section": current_section,

                "clause_id": current_clause_id,

                "clause_title": current_clause_title,

                "type": "paragraph",

                "content": text,

            }

            units.append(unit)

            paragraph_count += 1

            print("\n" + "-" * 100)

            print(f"TEXT UNIT {paragraph_count}")

            print("-" * 100)

            print(f"ELEMENT      : {index}")

            print(f"SECTION      : {current_section}")

            print(f"CLAUSE ID    : {current_clause_id}")

            print(f"CLAUSE TITLE : {current_clause_title}")

            print(f"WORDS        : {len(text.split())}")

            print("\nCONTENT")

            print(text)

        # =====================================================
        # TABLES
        # =====================================================

        for table in page.get(
            "detected_tables",
            [],
        ):

            print("\n" + "-" * 100)

            print(
                f"PROCESSING TABLE {table.get('table_id')}"
            )

            print("-" * 100)

            print(
                f"TABLE TYPE : {table.get('table_type')}"
            )

            print(
                f"ROWS       : {len(table.get('rows', []))}"
            )

            header = table.get(
                "header",
                [],
            )

            rows = table.get(
                "rows",
                [],
            )

            print("\nHEADER")

            print(header)

            for row_index, row in enumerate(
                rows,
                start=1,
            ):

                values = []

                for column_name, value in zip(
                    header,
                    row,
                ):

                    column_name = normalize_text(
                        column_name
                    )

                    value = normalize_text(
                        value
                    )

                    if not value:
                        continue

                    values.append(
                        f"{column_name}: {value}"
                    )

                if not values:

                    continue

                table_content = "\n".join(values)

                unit = {

                    "page": page["page"],

                    "section": current_section,

                    "clause_id": current_clause_id,

                    "clause_title": current_clause_title,

                    "type": "table",

                    "table_id": table.get(
                        "table_id",
                        0,
                    ),

                    "table_type": table.get(
                        "table_type",
                        "generic",
                    ),

                    "content": table_content,

                }

                units.append(unit)

                table_count += 1

                print("\nTABLE UNIT")

                print(f"ROW          : {row_index}")

                print(f"SECTION      : {current_section}")

                print(f"CLAUSE ID    : {current_clause_id}")

                print(f"TABLE TYPE   : {table.get('table_type')}")

                print("\nCONTENT")

                print(table_content)

        print("\nPAGE SUMMARY")

        print(
            f"Paragraph Units : {paragraph_count}"
        )

        print(
            f"Table Units     : {table_count}"
        )

    # =====================================================
    # FINAL SUMMARY
    # =====================================================

    print("\n" + "=" * 120)

    print("POLICY PARSER SUMMARY")

    print("=" * 120)

    print(
        f"TOTAL PAGES           : {len(pages)}"
    )

    print(
        f"PARAGRAPH UNITS       : {paragraph_count}"
    )

    print(
        f"TABLE UNITS           : {table_count}"
    )

    print(
        f"TOTAL UNITS CREATED   : {len(units)}"
    )

    print("=" * 120)

    print("POLICY PARSER COMPLETE")

    print("=" * 120)

    return units