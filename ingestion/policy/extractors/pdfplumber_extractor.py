import pdfplumber


def extract_pdf(pdf_path):
    """
    Extract tables and plain text using pdfplumber.

    Returns
    -------
    [
        {
            "page": 1,
            "tables": [...],
            "text": "..."
        }
    ]
    """

    pages = []

    print("\n" + "=" * 120)
    print("PDFPLUMBER EXTRACTION STARTED")
    print("=" * 120)

    with pdfplumber.open(pdf_path) as pdf:

        print(f"TOTAL PDF PAGES : {len(pdf.pages)}")

        total_tables = 0

        for page_number, page in enumerate(pdf.pages, start=1):

            print("\n" + "=" * 120)
            print(f"PAGE {page_number}")
            print("=" * 120)

            page_tables = []

            # =====================================================
            # TABLE EXTRACTION
            # =====================================================

            try:

                tables = page.extract_tables()

            except Exception as e:

                print(f"TABLE EXTRACTION FAILED : {e}")

                tables = []

            print(f"TABLES FOUND : {len(tables)}")

            for table_index, table in enumerate(tables):

                rows = []

                for row in table:

                    if row is None:

                        continue

                    cleaned = []

                    for cell in row:

                        if cell is None:

                            cleaned.append("")

                        else:

                            cleaned.append(
                                str(cell).strip()
                            )

                    rows.append(cleaned)

                if not rows:

                    continue

                page_tables.append(
                    {
                        "table_id": table_index + 1,
                        "rows": rows,
                    }
                )

                total_tables += 1

                print("\n" + "-" * 80)
                print(f"TABLE {table_index + 1}")
                print("-" * 80)

                print(
                    f"ROWS    : {len(rows)}"
                )

                print(
                    f"COLUMNS : {len(rows[0]) if rows else 0}"
                )

                print("\nTABLE PREVIEW")

                preview_rows = min(
                    5,
                    len(rows),
                )

                for row in rows[:preview_rows]:

                    print(row)

                if len(rows) > preview_rows:

                    print("...")

            # =====================================================
            # TEXT EXTRACTION
            # =====================================================

            page_text = page.extract_text() or ""

            print("\nTEXT SUMMARY")

            print(
                f"TOTAL CHARACTERS : {len(page_text)}"
            )

            print(
                f"TOTAL WORDS      : {len(page_text.split())}"
            )

            preview = page_text.replace(
                "\n",
                " ",
            )

            preview = preview[:400]

            print("\nTEXT PREVIEW")

            print(preview)

            if len(page_text) > 400:

                print("...")

            pages.append(
                {
                    "page": page_number,
                    "tables": page_tables,
                    "text": page_text,
                }
            )

            print("\nPAGE SUMMARY")

            print(
                f"Tables Saved : {len(page_tables)}"
            )

            print(
                f"Text Length  : {len(page_text)}"
            )

    print("\n" + "=" * 120)
    print("PDFPLUMBER EXTRACTION SUMMARY")
    print("=" * 120)

    print(
        f"TOTAL PAGES  : {len(pages)}"
    )

    print(
        f"TOTAL TABLES : {total_tables}"
    )

    print("=" * 120)
    print("PDFPLUMBER EXTRACTION COMPLETE")
    print("=" * 120)

    return pages