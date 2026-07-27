from collections import Counter
import re


HEADER_REGION = 90
FOOTER_REGION = 90

MIN_REPEAT_RATIO = 0.60


def normalize(text):

    text = text.strip()

    text = re.sub(r"\s+", " ", text)

    return text.lower()


def remove_headers_and_footers(pages):

    print("\n" + "=" * 120)
    print("HEADER / FOOTER CLEANING STARTED")
    print("=" * 120)

    total_pages = len(pages)

    repeated_counter = Counter()

    # =====================================================
    # FIND REPEATED HEADER / FOOTER CANDIDATES
    # =====================================================

    print("\nSCANNING FOR REPEATED HEADERS / FOOTERS...")

    for page in pages:

        page_height = page["height"]

        seen = set()

        for item in page["elements"]:

            y0 = item["bbox"][1]

            text = normalize(item["text"])

            if not text:
                continue

            if (
                y0 <= HEADER_REGION
                or y0 >= page_height - FOOTER_REGION
            ):

                if text not in seen:

                    repeated_counter[text] += 1

                    seen.add(text)

    repeated_text = set()

    threshold = max(
        2,
        int(total_pages * MIN_REPEAT_RATIO),
    )

    print(f"\nTOTAL PAGES : {total_pages}")
    print(f"REPEAT THRESHOLD : {threshold} pages")

    print("\nREPEATED CANDIDATES")

    print("-" * 120)

    for text, count in sorted(
        repeated_counter.items(),
        key=lambda x: x[1],
        reverse=True,
    ):

        print(
            f"{count:>3} pages | {text}"
        )

        if count >= threshold:

            repeated_text.add(text)

    print("-" * 120)

    # =====================================================
    # REMOVE HEADERS / FOOTERS
    # =====================================================

    cleaned_pages = []

    removed_total = 0

    for page in pages:

        page_number = page["page"]

        page_height = page["height"]

        original_count = len(page["elements"])

        cleaned = []

        removed_on_page = 0

        print("\n" + "=" * 100)
        print(f"PAGE {page_number}")
        print("=" * 100)

        for item in page["elements"]:

            text = normalize(item["text"])

            y0 = item["bbox"][1]

            reason = None

            # ------------------------------------------------
            # Repeated Header/Footer
            # ------------------------------------------------

            if (
                text in repeated_text
                and (
                    y0 <= HEADER_REGION
                    or y0 >= page_height - FOOTER_REGION
                )
            ):

                reason = "Repeated Header/Footer"

            # ------------------------------------------------
            # Page Number
            # ------------------------------------------------

            elif re.fullmatch(
                r"\d+",
                item["text"].strip(),
            ):

                reason = "Page Number"

            # ------------------------------------------------
            # Page X
            # ------------------------------------------------

            elif re.fullmatch(
                r"page\s+\d+",
                text,
            ):

                reason = "Page X"

            # ------------------------------------------------
            # Page X of Y
            # ------------------------------------------------

            elif re.fullmatch(
                r"page\s+\d+\s+of\s+\d+",
                text,
            ):

                reason = "Page X of Y"

            if reason:

                removed_total += 1

                removed_on_page += 1

                print("\nREMOVED")

                print(f"Reason : {reason}")

                print(f"Text   : {item['text']}")

                print(f"Y      : {round(y0,2)}")

                continue

            cleaned.append(item)

        cleaned_pages.append(
            {
                **page,
                "elements": cleaned,
            }
        )

        print("\nPAGE SUMMARY")

        print(
            f"Original Elements : {original_count}"
        )

        print(
            f"Removed Elements  : {removed_on_page}"
        )

        print(
            f"Remaining Elements: {len(cleaned)}"
        )

    # =====================================================
    # SUMMARY
    # =====================================================

    print("\n" + "=" * 120)

    print("HEADER / FOOTER CLEANING SUMMARY")

    print("=" * 120)

    print(
        f"TOTAL PAGES            : {total_pages}"
    )

    print(
        f"TOTAL REMOVED ELEMENTS : {removed_total}"
    )

    print(
        f"TOTAL REMAINING        : {sum(len(page['elements']) for page in cleaned_pages)}"
    )

    print("=" * 120)

    print("HEADER / FOOTER CLEANING COMPLETE")

    print("=" * 120)

    return cleaned_pages