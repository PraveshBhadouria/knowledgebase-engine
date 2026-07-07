from ingestion.text.extractors.pymupdf_extractor import (
    extract_text as pymupdf_extract,
)

from ingestion.text.extractors.pdfplumber_extractor import (
    extract_text as pdfplumber_extract,
)


def extract_text(pdf_path):

    pages = pymupdf_extract(pdf_path)

    total_words = sum(
        len(page["text"].split())
        for page in pages
    )

    print(
        f"\nPYMUPDF WORDS: {total_words}"
    )

    if total_words > 100:

        print(
            "USING PYMUPDF EXTRACTOR"
        )

        return pages

    print(
        "FALLBACK TO PDFPLUMBER"
    )

    return pdfplumber_extract(pdf_path)