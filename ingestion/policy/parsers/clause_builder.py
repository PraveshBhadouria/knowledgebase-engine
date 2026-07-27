from collections import OrderedDict


def build_clauses(units):
    """
    Merge policy units belonging to the same clause.
    """

    print("\n" + "=" * 120)
    print("CLAUSE BUILDING STARTED")
    print("=" * 120)

    print(f"TOTAL INPUT UNITS : {len(units)}")

    clauses = OrderedDict()

    # =====================================================
    # PROCESS EVERY UNIT
    # =====================================================

    for index, unit in enumerate(units, start=1):

        print("\n" + "-" * 120)
        print(f"UNIT {index}")
        print("-" * 120)

        print(f"PAGE         : {unit.get('page')}")
        print(f"SECTION      : {unit.get('section')}")
        print(f"CLAUSE ID    : {unit.get('clause_id')}")
        print(f"CLAUSE TITLE : {unit.get('clause_title')}")
        print(f"TYPE         : {unit.get('type')}")

        preview = unit.get("content", "")[:300]

        print("\nCONTENT PREVIEW")

        print(preview)

        if len(unit.get("content", "")) > 300:

            print("...")

        clause_id = unit.get(
            "clause_id",
            "",
        ).strip()

        section = unit.get(
            "section",
            "General",
        )

        title = unit.get(
            "clause_title",
            "",
        ).strip()

        # =====================================================
        # GENERAL CONTENT
        # =====================================================

        if clause_id == "":

            clause_id = "__GENERAL__"

            if not title:

                title = "General"

        key = (
            section,
            clause_id,
        )

        # =====================================================
        # CREATE NEW CLAUSE
        # =====================================================

        if key not in clauses:

            print("\nNEW CLAUSE CREATED")

            print(f"SECTION : {section}")

            print(f"CLAUSE  : {clause_id}")

            clauses[key] = {

                "section": section,

                "clause_id": clause_id,

                "clause_title": title,

                "page_start": unit["page"],

                "page_end": unit["page"],

                "paragraphs": [],

                "tables": [],

            }

        clause = clauses[key]

        clause["page_end"] = max(
            clause["page_end"],
            unit["page"],
        )

        # =====================================================
        # STORE CONTENT
        # =====================================================

        if unit["type"] == "table":

            clause["tables"].append(
                unit["content"]
            )

            print("TABLE APPENDED")

            print(
                f"TOTAL TABLES : {len(clause['tables'])}"
            )

        else:

            clause["paragraphs"].append(
                unit["content"]
            )

            print("PARAGRAPH APPENDED")

            print(
                f"TOTAL PARAGRAPHS : {len(clause['paragraphs'])}"
            )

        print(
            f"CURRENT PAGE RANGE : {clause['page_start']} -> {clause['page_end']}"
        )

    # =====================================================
    # BUILD FINAL CLAUSES
    # =====================================================

    print("\n" + "=" * 120)
    print("MERGING CLAUSES")
    print("=" * 120)

    output = []

    total_words = 0

    for index, clause in enumerate(
        clauses.values(),
        start=1,
    ):

        paragraph_text = "\n\n".join(
            clause["paragraphs"]
        )

        table_text = "\n\n".join(
            clause["tables"]
        )

        full_content = paragraph_text

        if table_text:

            full_content += "\n\n" + table_text

        full_content = full_content.strip()

        word_count = len(
            full_content.split()
        )

        total_words += word_count

        output.append(
            {

                "page_start": clause["page_start"],

                "page_end": clause["page_end"],

                "section": clause["section"],

                "clause_id": clause["clause_id"],

                "clause_title": clause["clause_title"],

                "content": full_content,

            }
        )

        print("\n" + "-" * 120)

        print(f"FINAL CLAUSE {index}")

        print("-" * 120)

        print(
            f"SECTION        : {clause['section']}"
        )

        print(
            f"CLAUSE ID      : {clause['clause_id']}"
        )

        print(
            f"CLAUSE TITLE   : {clause['clause_title']}"
        )

        print(
            f"PAGES          : {clause['page_start']} -> {clause['page_end']}"
        )

        print(
            f"PARAGRAPHS     : {len(clause['paragraphs'])}"
        )

        print(
            f"TABLES         : {len(clause['tables'])}"
        )

        print(
            f"WORDS          : {word_count}"
        )

        print(
            f"CHARACTERS     : {len(full_content)}"
        )

        print("\nCONTENT PREVIEW")

        print("-" * 100)

        print(full_content[:700])

        if len(full_content) > 700:

            print("\n...")

        print("-" * 100)

    # =====================================================
    # SUMMARY
    # =====================================================

    print("\n" + "=" * 120)

    print("CLAUSE BUILDING SUMMARY")

    print("=" * 120)

    print(
        f"INPUT UNITS           : {len(units)}"
    )

    print(
        f"FINAL CLAUSES         : {len(output)}"
    )

    print(
        f"TOTAL WORDS           : {total_words}"
    )

    if output:

        average = round(
            total_words / len(output),
            2,
        )

    else:

        average = 0

    print(
        f"AVERAGE WORDS/CLAUSE  : {average}"
    )

    print("=" * 120)

    print("CLAUSE BUILDING COMPLETE")

    print("=" * 120)

    return output