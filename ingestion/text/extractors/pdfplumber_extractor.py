import pdfplumber


def extract_text(pdf_path):

    pages = []

    with pdfplumber.open(pdf_path) as pdf:

        for page_num, page in enumerate(pdf.pages, start=1):

            text = page.extract_text() or ""

            pages.append(
                {
                    "page": page_num,
                    "text": text,
                }
            )

    return pages