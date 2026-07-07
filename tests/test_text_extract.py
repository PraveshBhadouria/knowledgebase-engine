import pdfplumber
import fitz  # PyMuPDF

PDF_PATH = "MBA_INV_SG_2026_v1_e_f 2.pdf"


def test_pdfplumber():
    print("\n" + "=" * 80)
    print("TESTING PDFPLUMBER")
    print("=" * 80)

    with pdfplumber.open(PDF_PATH) as pdf:
        total_pages = len(pdf.pages)

        text_pages = 0
        image_pages = 0

        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text()

            if text and len(text.strip()) > 100:
                text_pages += 1
                print(
                    f"✅ PAGE {i} -> TEXT FOUND "
                    f"({len(text)} chars)"
                )
            else:
                image_pages += 1
                print(
                    f"❌ PAGE {i} -> NO TEXT FOUND"
                )

        print("\nSUMMARY")
        print("-" * 40)
        print(f"TOTAL PAGES : {total_pages}")
        print(f"TEXT PAGES  : {text_pages}")
        print(f"IMAGE PAGES : {image_pages}")


def test_pymupdf():
    print("\n" + "=" * 80)
    print("TESTING PYMUPDF")
    print("=" * 80)

    doc = fitz.open(PDF_PATH)

    total_pages = len(doc)

    text_pages = 0
    image_pages = 0

    for i in range(total_pages):
        page = doc[i]

        text = page.get_text()

        if text and len(text.strip()) > 100:
            text_pages += 1
            print(
                f"✅ PAGE {i + 1} -> TEXT FOUND "
                f"({len(text)} chars)"
            )
        else:
            image_pages += 1
            print(
                f"❌ PAGE {i + 1} -> NO TEXT FOUND"
            )

    print("\nSUMMARY")
    print("-" * 40)
    print(f"TOTAL PAGES : {total_pages}")
    print(f"TEXT PAGES  : {text_pages}")
    print(f"IMAGE PAGES : {image_pages}")


if __name__ == "__main__":
    test_pdfplumber()
    test_pymupdf()