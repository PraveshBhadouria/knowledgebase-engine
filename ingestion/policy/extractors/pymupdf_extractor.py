import fitz
from collections import Counter


def extract_pdf(pdf_path):
    """
    Extract PDF while preserving layout information.
    """

    doc = fitz.open(pdf_path)

    pages = []

    print("\n" + "=" * 120)
    print("PYMUPDF EXTRACTION STARTED")
    print("=" * 120)

    print(f"PDF : {pdf_path}")

    print(f"TOTAL PAGES : {len(doc)}")

    font_counter = Counter()

    total_elements = 0

    for page_number, page in enumerate(doc, start=1):

        print("\n" + "=" * 120)
        print(f"PAGE {page_number}")
        print("=" * 120)

        print(
            f"PAGE SIZE : "
            f"{round(page.rect.width)} x {round(page.rect.height)}"
        )

        page_dict = page.get_text("dict")

        page_elements = []

        for block_index, block in enumerate(page_dict["blocks"]):

            if "lines" not in block:
                continue

            for line_index, line in enumerate(block["lines"]):

                for span_index, span in enumerate(line["spans"]):

                    text = span["text"].strip()

                    if not text:
                        continue

                    font_name = span["font"]

                    font_lower = font_name.lower()

                    is_bold = any(

                        keyword in font_lower

                        for keyword in (

                            "bold",

                            "black",

                            "heavy",

                            "semibold",

                            "demi",

                        )

                    )

                    font_size = round(
                        span["size"],
                        2,
                    )

                    bbox = tuple(
                        span["bbox"]
                    )

                    page_elements.append(
                        {
                            "text": text,
                            "page": page_number,
                            "bbox": bbox,
                            "font_size": font_size,
                            "font_name": font_name,
                            "bold": is_bold,
                            "block_no": block_index,
                            "line_no": line_index,
                            "span_no": span_index,
                        }
                    )

                    font_counter[
                        (
                            font_size,
                            is_bold,
                            font_name,
                        )
                    ] += 1

                    total_elements += 1

        page_elements.sort(
            key=lambda x: (
                x["bbox"][1],
                x["bbox"][0],
            )
        )

        print(
            f"\nTOTAL ELEMENTS : {len(page_elements)}"
        )

        print("\nELEMENTS")

        print("-" * 120)

        for index, element in enumerate(
            page_elements,
            start=1,
        ):

            print(
                f"[{index}]"
            )

            print(
                f"TEXT       : {element['text']}"
            )

            print(
                f"FONT SIZE  : {element['font_size']}"
            )

            print(
                f"FONT NAME  : {element['font_name']}"
            )

            print(
                f"BOLD       : {element['bold']}"
            )

            print(
                f"BBOX       : {element['bbox']}"
            )

            print(
                f"BLOCK      : {element['block_no']}"
            )

            print(
                f"LINE       : {element['line_no']}"
            )

            print(
                f"SPAN       : {element['span_no']}"
            )

            print("-" * 120)

        pages.append(
            {
                "page": page_number,
                "width": page.rect.width,
                "height": page.rect.height,
                "elements": page_elements,
            }
        )

    print("\n" + "=" * 120)
    print("FONT DISTRIBUTION")
    print("=" * 120)

    for (
        (size, bold, font),
        count,
    ) in sorted(
        font_counter.items(),
        key=lambda x: (
            -x[1],
            -x[0][0],
        ),
    ):

        print(
            f"FONT SIZE : {size:<6}"
            f" | BOLD : {str(bold):<5}"
            f" | COUNT : {count:<5}"
            f" | FONT : {font}"
        )

    print("\n" + "=" * 120)

    print("PYMUPDF EXTRACTION SUMMARY")

    print("=" * 120)

    print(
        f"TOTAL PAGES    : {len(pages)}"
    )

    print(
        f"TOTAL ELEMENTS : {total_elements}"
    )

    print("=" * 120)

    print("PYMUPDF EXTRACTION COMPLETE")

    print("=" * 120)

    doc.close()

    return pages