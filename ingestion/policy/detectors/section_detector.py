import re


# ==========================================================
# Common Policy Section Keywords
# ==========================================================

SECTION_KEYWORDS = [

    "definitions",

    "coverage",

    "coverages",

    "benefits",

    "exclusions",

    "waiting period",

    "general conditions",

    "special conditions",

    "claim procedure",

    "claim process",

    "renewal",

    "cancellation",

    "termination",

    "eligibility",

    "premium",

    "sum insured",

    "co-payment",

    "copayment",

    "room rent",

    "day care procedures",

    "grievance",

    "customer service",

    "free look period",

    "portability",

    "nomination",

    "renewability",

    "policy period",

]


NUMBERING_PATTERN = re.compile(
    r"^(\d+(\.\d+)*)"
)


def detect_sections(pages):
    """
    Detect policy sections.

    Adds

        element["section"]

    to every element.
    """

    print("\n" + "=" * 120)
    print("SECTION DETECTION STARTED")
    print("=" * 120)

    current_section = "General"

    section_counter = 0

    detected_sections = []

    # =====================================================
    # PROCESS PAGES
    # =====================================================

    for page in pages:

        print("\n" + "=" * 120)
        print(f"PAGE {page['page']}")
        print("=" * 120)

        print(
            f"TOTAL ELEMENTS : {len(page['elements'])}"
        )

        for index, element in enumerate(
            page["elements"],
            start=1,
        ):

            text = element["text"].strip()

            lower = text.lower()

            is_heading = False

            reason = "Not a Section"

            print("\n" + "-" * 100)

            print(f"ELEMENT {index}")

            print("-" * 100)

            print(f"TEXT       : {text}")

            print(
                f"FONT SIZE  : {element['font_size']}"
            )

            print(
                f"BOLD       : {element['bold']}"
            )

            print(
                f"BBOX       : {tuple(round(x,1) for x in element['bbox'])}"
            )

            # =====================================================
            # Keyword Match
            # =====================================================

            for keyword in SECTION_KEYWORDS:

                if lower == keyword:

                    is_heading = True

                    reason = (
                        f"Keyword Match ({keyword})"
                    )

                    break

            # =====================================================
            # Numbered Heading
            # =====================================================

            if (
                not is_heading
                and NUMBERING_PATTERN.match(text)
                and element["bold"]
                and element["font_size"] >= 11
            ):

                is_heading = True

                reason = (
                    "Bold Numbered Heading"
                )

            # =====================================================
            # Large Bold Heading
            # =====================================================

            if (
                not is_heading
                and element["bold"]
                and element["font_size"] >= 13
                and len(text.split()) <= 8
            ):

                is_heading = True

                reason = (
                    "Large Bold Heading"
                )

            # =====================================================
            # SECTION FOUND
            # =====================================================

            if is_heading:

                current_section = text

                section_counter += 1

                detected_sections.append(text)

                print("\nSECTION DETECTED")

                print(
                    f"SECTION : {current_section}"
                )

                print(
                    f"REASON  : {reason}"
                )

            else:

                print(
                    f"NOT A SECTION : {reason}"
                )

            element["section"] = current_section

            print(
                f"ASSIGNED SECTION : {current_section}"
            )

        print("\nPAGE SUMMARY")

        print(
            f"CURRENT SECTION : {current_section}"
        )

    # =====================================================
    # SUMMARY
    # =====================================================

    print("\n" + "=" * 120)

    print("SECTION DETECTION SUMMARY")

    print("=" * 120)

    print(
        f"TOTAL PAGES     : {len(pages)}"
    )

    print(
        f"TOTAL SECTIONS  : {section_counter}"
    )

    print("\nUNIQUE SECTIONS")

    print("-" * 120)

    for section in sorted(
        set(detected_sections)
    ):

        print(section)

    print("-" * 120)

    print("SECTION DETECTION COMPLETE")

    print("=" * 120)

    return pages