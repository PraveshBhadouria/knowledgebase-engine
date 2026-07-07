import fitz
import json


def extract_blocks(pdf_path):

    doc = fitz.open(pdf_path)

    blocks = []

    for page_num, page in enumerate(doc, start=1):

        data = page.get_text("dict")

        for block in data["blocks"]:

            if "lines" not in block:
                continue

            text_parts = []

            max_size = 0
            bold = False

            for line in block["lines"]:

                for span in line["spans"]:

                    txt = span["text"].strip()

                    if txt:
                        text_parts.append(txt)

                    max_size = max(
                        max_size,
                        span["size"]
                    )

                    if "bold" in span["font"].lower():
                        bold = True

            text = " ".join(text_parts)

            if not text:
                continue

            blocks.append({
                "page": page_num,
                "text": text,
                "font_size": round(max_size, 1),
                "bold": bold
            })

    return blocks