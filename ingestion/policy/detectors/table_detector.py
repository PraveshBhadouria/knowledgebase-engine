import re


def detect_tables(pages):
    """
    Converts extracted pdfplumber tables into structured objects.

    Input:
        pages from extractor_router()

    Output:
        Same pages with an additional key:

            page["detected_tables"]
    """

    print("\n" + "=" * 120)
    print("TABLE DETECTION STARTED")
    print("=" * 120)

    processed_pages = []

    total_tables = 0

    total_rows = 0

    # =====================================================
    # PROCESS PAGES
    # =====================================================

    for page in pages:

        print("\n" + "=" * 120)
        print(f"PAGE {page['page']}")
        print("=" * 120)

        print(
            f"RAW TABLES FOUND : {len(page['tables'])}"
        )

        detected_tables = []

        # -------------------------------------------------
        # Process Every Table
        # -------------------------------------------------

        for table in page["tables"]:

            print("\n" + "-" * 100)
            print(
                f"PROCESSING TABLE {table['table_id']}"
            )
            print("-" * 100)

            rows = table.get(
                "rows",
                [],
            )

            print(
                f"RAW ROWS : {len(rows)}"
            )

            if not rows:

                print("EMPTY TABLE -> SKIPPED")

                continue

            # -------------------------------------------------
            # Remove Empty Rows
            # -------------------------------------------------

            cleaned_rows = []

            removed_rows = 0

            for row in rows:

                cleaned = [

                    "" if cell is None

                    else str(cell).strip()

                    for cell in row

                ]

                if any(cleaned):

                    cleaned_rows.append(cleaned)

                else:

                    removed_rows += 1

            print(
                f"REMOVED EMPTY ROWS : {removed_rows}"
            )

            if not cleaned_rows:

                print(
                    "NO VALID ROWS REMAINING"
                )

                continue

            # -------------------------------------------------
            # Header
            # -------------------------------------------------

            header = cleaned_rows[0]

            body = cleaned_rows[1:]

            table_type = classify_table(
                header
            )

            table_object = {

                "table_id": table["table_id"],

                "page": page["page"],

                "header": header,

                "rows": body,

                "column_count": len(header),

                "row_count": len(body),

                "table_type": table_type,

            }

            detected_tables.append(
                table_object
            )

            total_tables += 1

            total_rows += len(body)

            # =====================================================
            # LOG TABLE
            # =====================================================

            print("\nTABLE DETECTED")

            print(
                f"TABLE ID      : {table['table_id']}"
            )

            print(
                f"TABLE TYPE    : {table_type}"
            )

            print(
                f"COLUMNS       : {len(header)}"
            )

            print(
                f"ROWS          : {len(body)}"
            )

            print("\nHEADER")

            print("-" * 80)

            print(header)

            print("-" * 80)

            print("\nROW PREVIEW")

            preview = min(
                10,
                len(body),
            )

            for row_index, row in enumerate(
                body[:preview],
                start=1,
            ):

                print(
                    f"{row_index:02d}. {row}"
                )

            if len(body) > preview:

                print("...")

        processed_pages.append(
            {
                **page,
                "detected_tables": detected_tables,
            }
        )

        print("\nPAGE SUMMARY")

        print(
            f"TABLES DETECTED : {len(detected_tables)}"
        )

    # =====================================================
    # SUMMARY
    # =====================================================

    print("\n" + "=" * 120)
    print("TABLE DETECTION SUMMARY")
    print("=" * 120)

    print(
        f"TOTAL PAGES   : {len(processed_pages)}"
    )

    print(
        f"TOTAL TABLES  : {total_tables}"
    )

    print(
        f"TOTAL ROWS    : {total_rows}"
    )

    print("=" * 120)

    print("TABLE DETECTION COMPLETE")

    print("=" * 120)

    return processed_pages


# ==========================================================
# TABLE CLASSIFICATION
# ==========================================================

def classify_table(header):

    text = " ".join(header).lower()

    print("\nCLASSIFYING TABLE")

    print(f"HEADER : {header}")

    if any(

        word in text

        for word in [

            "premium",

            "annual premium",

            "gst",

        ]

    ):

        print("MATCHED : PREMIUM")

        return "premium"

    if any(

        word in text

        for word in [

            "benefit",

            "coverage",

            "covered",

        ]

    ):

        print("MATCHED : BENEFIT")

        return "benefit"

    if any(

        word in text

        for word in [

            "waiting period",

            "months",

            "days",

        ]

    ):

        print("MATCHED : WAITING PERIOD")

        return "waiting_period"

    if any(

        word in text

        for word in [

            "sum insured",

            "limit",

            "maximum",

        ]

    ):

        print("MATCHED : LIMIT")

        return "limit"

    if any(

        word in text

        for word in [

            "disease",

            "illness",

        ]

    ):

        print("MATCHED : DISEASE")

        return "disease"

    if any(

        word in text

        for word in [

            "room rent",

            "icu",

        ]

    ):

        print("MATCHED : ROOM RENT")

        return "room_rent"

    if any(

        word in text

        for word in [

            "copay",

            "co-pay",

        ]

    ):

        print("MATCHED : COPAY")

        return "copay"

    print("MATCHED : GENERIC")

    return "generic"