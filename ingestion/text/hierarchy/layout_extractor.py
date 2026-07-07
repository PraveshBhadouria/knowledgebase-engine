import fitz
import re
from collections import Counter


# =====================================================
# GENERIC TABLE DETECTION
# =====================================================

LEFT_COLUMN_MAX_X = 220
MAX_KEY_WORDS = 6
ROW_ALIGNMENT_TOLERANCE = 20


def detect_table_rows(elements):

    processed = set()
    output = []

    for i, item in enumerate(elements):

        if i in processed:
            continue

        text = item["text"].strip()

        x0 = item["bbox"][0]
        y0 = item["bbox"][1]

        # -------------------------------------------------
        # Reject False Table Rows
        # -------------------------------------------------
        
        if (
            text == "•"
            or re.match(r"^\d+$", text)
            or re.match(r"^\d+(\.\d+)*$", text)
            or "." * 5 in text
        ):
            print(f"🚫 REJECTED FALSE TABLE ROW: {text}")
            item["block_type"] = "paragraph"
            output.append(item)
            continue

        # -------------------------------------------------
        # Candidate for left-column key
        # -------------------------------------------------

        is_key_candidate = (
            x0 <= LEFT_COLUMN_MAX_X
            and len(text.split()) <= MAX_KEY_WORDS
            and len(text) <= 80
            and not re.match(r"^\d+(\.\d+)*$", text)
            and text != "•"
        )

        if not is_key_candidate:

            item["block_type"] = "paragraph"
            output.append(item)
            continue

        values = []
        matched_indices = []

        # -------------------------------------------------
        # Find content on same row to the right
        # -------------------------------------------------

        for j, candidate in enumerate(elements):

            if j == i or j in processed:
                continue

            cx0 = candidate["bbox"][0]
            cy0 = candidate["bbox"][1]

            same_row = (
                abs(cy0 - y0)
                <= ROW_ALIGNMENT_TOLERANCE
            )

            if (
                same_row
                and cx0 > x0 + 60
            ):

                values.append(
                    candidate["text"]
                )

                matched_indices.append(j)

        if values:

            item["block_type"] = "table_row"

            item["table_key"] = text

            item["table_value"] = " ".join(
                values
            )

            output.append(item)

            processed.update(
                matched_indices
            )

            print("\n📊 TABLE ROW DETECTED")
            print(
                f"KEY   : {item['table_key']}"
            )
            print(
                f"VALUE : {item['table_value']}"
            )

        else:

            item["block_type"] = "paragraph"
            output.append(item)

    return output


# =====================================================
# MAIN EXTRACTION
# =====================================================

def extract_layout(
    pdf_path,
    start_page=None,
    end_page=None,
):

    doc = fitz.open(pdf_path)

    total_pages = len(doc)

    if start_page is None:
        start_page = 1

    if end_page is None:
        end_page = total_pages

    start_page = max(
        1,
        start_page,
    )

    end_page = min(
        total_pages,
        end_page,
    )

    pages = []

    print("\nLAYOUT EXTRACTION STARTED")

    print(
        f"TOTAL PDF PAGES : {total_pages}"
    )

    print(
        f"PROCESSING PAGES : "
        f"{start_page} -> {end_page}"
    )

    font_counter = Counter()

    # =====================================================
    # PROCESS PAGES
    # =====================================================

    for page_number in range(
        start_page,
        end_page + 1,
    ):

        page = doc[page_number - 1]

        page_data = []

        blocks = sorted(
            page.get_text("dict")["blocks"],
            key=lambda b: (
                b["bbox"][1],
                b["bbox"][0],
            ),
        )

        print("\n" + "=" * 120)
        print(f"PAGE {page_number}")
        print("=" * 120)

        # =====================================================
        # EXTRACT TEXT
        # =====================================================

        for block in blocks:

            if "lines" not in block:
                continue

            for line in block["lines"]:

                text = ""

                font_size = 0
                font_name = ""
                is_bold = False

                for span in line["spans"]:

                    text += span["text"]

                    if span["size"] > font_size:

                        font_size = span["size"]

                        font_name = span["font"]

                        font_lower = (
                            span["font"].lower()
                        )

                        is_bold = any(
                            keyword in font_lower
                            for keyword in [
                                "bold",
                                "black",
                                "heavy",
                                "demi",
                                "semibold",
                            ]
                        )

                text = text.strip()

                if not text:
                    continue

                bbox = line["bbox"]

                font_counter[
                    (
                        round(font_size, 1),
                        is_bold,
                    )
                ] += 1

                print(
                    f"[PAGE {page_number}] "
                    f"FONT={round(font_size,2)} | "
                    f"BOLD={is_bold} | "
                    f"X={round(bbox[0],1)} | "
                    f"Y={round(bbox[1],1)} | "
                    f"TEXT={text}"
                )

                page_data.append(
                    {
                        "text": text,
                        "font_size": round(
                            font_size,
                            2,
                        ),
                        "font_name": font_name,
                        "bold": is_bold,
                        "bbox": bbox,
                        "page": page_number,
                        "block_type": "paragraph",
                    }
                )

        # =====================================================
        # PAGE SKIPPING LOGIC
        # =====================================================

        page_text = " ".join(
            item["text"].lower()
            for item in page_data
        )

        skip_page = False

        if (
            "list of tables"
            in page_text
        ):

            print(
                f"\n❌ SKIPPING PAGE "
                f"{page_number}"
            )
            print(
                "REASON : LIST OF TABLES PAGE"
            )

            skip_page = True

        elif (
            "list of figures"
            in page_text
        ):

            print(
                f"\n❌ SKIPPING PAGE "
                f"{page_number}"
            )
            print(
                "REASON : LIST OF FIGURES PAGE"
            )

            skip_page = True

        elif (
            "contents" in page_text
            and (
                "study material"
                in page_text
                or "prescribed resources"
                in page_text
            )
        ):

            print(
                f"\n❌ SKIPPING PAGE "
                f"{page_number}"
            )
            print(
                "REASON : CONTENTS PAGE"
            )

            skip_page = True

        if skip_page:
            continue

        # =====================================================
        # TABLE DETECTION
        # =====================================================

        print(
            f"\n🔍 DETECTING TABLES "
            f"ON PAGE {page_number}"
        )

        page_data = detect_table_rows(
            page_data
        )

        # =====================================================
        # SAVE PAGE
        # =====================================================

        print(
            f"\n✅ ADDING PAGE "
            f"{page_number}"
        )

        pages.append(
            {
                "page": page_number,
                "elements": page_data,
            }
        )

    # =====================================================
    # FONT ANALYSIS
    # =====================================================

    print("\n" + "=" * 120)
    print("FONT DISTRIBUTION")
    print("=" * 120)

    for (
        (size, bold),
        count,
    ) in font_counter.most_common():

        print(
            f"FONT={size} "
            f"BOLD={bold} "
            f"COUNT={count}"
        )

    print("\nLAYOUT EXTRACTION COMPLETE")

    print(
        f"TOTAL PAGES RETAINED : "
        f"{len(pages)}"
    )

    doc.close()

    return pages