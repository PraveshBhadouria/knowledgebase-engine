import fitz


def is_text_pdf(pdf_path):

    doc = fitz.open(pdf_path)

    total_words = 0

    pages_to_check = min(
        5,
        len(doc),
    )

    for page_number in range(
        pages_to_check
    ):

        text = doc[
            page_number
        ].get_text()

        total_words += len(
            text.split()
        )

    print(
        f"\nPDF WORDS FOUND: {total_words}"
    )

    return total_words > 100