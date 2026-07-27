from ingestion.policy.extractors.pymupdf_extractor import (
    extract_pdf as pymupdf_extract,
)

from ingestion.policy.extractors.pdfplumber_extractor import (
    extract_pdf as pdfplumber_extract,
)


def extract_pdf(pdf_path):
    """
    Merge outputs from PyMuPDF and pdfplumber.

    Output Structure

    [
        {
            "page": 1,
            "width": ...,
            "height": ...,
            "elements": [...],
            "tables": [...],
            "text": "..."
        }
    ]
    """

    print("\n" + "=" * 120)
    print("STARTING POLICY EXTRACTION")
    print("=" * 120)
    print(f"PDF PATH : {pdf_path}")

    # =====================================================
    # Run Extractors
    # =====================================================

    print("\nRunning PyMuPDF Extractor...")
    pymupdf_pages = pymupdf_extract(pdf_path)

    print("\nRunning pdfplumber Extractor...")
    pdfplumber_pages = pdfplumber_extract(pdf_path)

    print("\n" + "-" * 120)
    print("EXTRACTION SUMMARY")
    print("-" * 120)

    print(f"PyMuPDF Pages    : {len(pymupdf_pages)}")
    print(f"pdfplumber Pages : {len(pdfplumber_pages)}")

    if len(pymupdf_pages) != len(pdfplumber_pages):

        print("\nWARNING : PAGE COUNT MISMATCH")
        print(
            f"Using minimum page count = {min(len(pymupdf_pages), len(pdfplumber_pages))}"
        )

    merged_pages = []

    total_pages = min(
        len(pymupdf_pages),
        len(pdfplumber_pages),
    )

    total_elements = 0
    total_tables = 0
    total_text_chars = 0

    # =====================================================
    # Merge Pages
    # =====================================================

    for index in range(total_pages):

        fitz_page = pymupdf_pages[index]

        plumber_page = pdfplumber_pages[index]

        merged_page = {
            "page": fitz_page["page"],
            "width": fitz_page["width"],
            "height": fitz_page["height"],
            "elements": fitz_page["elements"],
            "tables": plumber_page["tables"],
            "text": plumber_page["text"],
        }

        merged_pages.append(merged_page)

        element_count = len(fitz_page["elements"])
        table_count = len(plumber_page["tables"])
        text_length = len(plumber_page["text"])

        total_elements += element_count
        total_tables += table_count
        total_text_chars += text_length

        print("\n" + "-" * 80)
        print(f"PAGE {fitz_page['page']}")
        print("-" * 80)
        print(f"Dimensions      : {round(fitz_page['width'])} x {round(fitz_page['height'])}")
        print(f"Text Elements   : {element_count}")
        print(f"Tables          : {table_count}")
        print(f"Text Characters : {text_length}")

        if fitz_page["elements"]:

            print("\nFirst 5 Extracted Elements:")

            for element in fitz_page["elements"][:5]:

                print(
                    f"  • {element['text'][:100]}"
                )

        if plumber_page["tables"]:

            print(f"\nTable Preview (First Table):")

            first_table = plumber_page["tables"][0]

            for row in first_table["rows"][:5]:

                print("   ", row)

    # =====================================================
    # Final Summary
    # =====================================================

    print("\n" + "=" * 120)
    print("POLICY EXTRACTION SUMMARY")
    print("=" * 120)

    print(f"Total Pages           : {len(merged_pages)}")
    print(f"Total Text Elements   : {total_elements}")
    print(f"Total Tables          : {total_tables}")
    print(f"Total Text Characters : {total_text_chars}")

    print("=" * 120)
    print("POLICY EXTRACTION COMPLETE")
    print("=" * 120)

    return merged_pages