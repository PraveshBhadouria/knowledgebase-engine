import re


# ==========================================================
# Clause Patterns
# ==========================================================

CLAUSE_PATTERNS = [

    ("Number", re.compile(r"^\d+$")),

    ("Number.Number", re.compile(r"^\d+\.\d+$")),

    ("Number.Number.Number", re.compile(r"^\d+\.\d+\.\d+$")),

    ("Clause", re.compile(r"^clause\s+\d+", re.I)),

    ("Section", re.compile(r"^section\s+\d+", re.I)),
]


def is_clause_heading(element):

    text = element["text"].strip()

    if not text:

        return False, "Empty"

    # -------------------------------------------------
    # Regex Patterns
    # -------------------------------------------------

    for name, pattern in CLAUSE_PATTERNS:

        if pattern.match(text):

            return True, f"Matched Pattern : {name}"

    # -------------------------------------------------
    # Bold Numbered Heading
    # -------------------------------------------------

    if (

        element["bold"]

        and element["font_size"] >= 11

        and re.match(r"^\d+(\.\d+)*", text)

    ):

        return True, "Bold Number Heading"

    return False, "No Match"


def detect_clauses(pages):

    """
    Adds

        clause_id
        clause_title

    to every element.
    """

    print("\n" + "=" * 120)
    print("CLAUSE DETECTION STARTED")
    print("=" * 120)

    current_clause = "0"

    current_title = "General"

    clause_counter = 0

    # =====================================================
    # Process Pages
    # =====================================================

    for page in pages:

        print("\n" + "=" * 120)
        print(f"PAGE {page['page']}")
        print("=" * 120)

        elements = page["elements"]

        print(
            f"TOTAL ELEMENTS : {len(elements)}"
        )

        index = 0

        while index < len(elements):

            element = elements[index]

            matched, reason = is_clause_heading(
                element
            )

            print("\n" + "-" * 100)

            print(f"ELEMENT {index + 1}")

            print("-" * 100)

            print(f"TEXT       : {element['text']}")

            print(f"FONT SIZE  : {element['font_size']}")

            print(f"BOLD       : {element['bold']}")

            print(
                f"BBOX       : {tuple(round(x,1) for x in element['bbox'])}"
            )

            print(f"RESULT     : {matched}")

            print(f"REASON     : {reason}")

            # =====================================================
            # Clause Found
            # =====================================================

            if matched:

                clause_counter += 1

                current_clause = element["text"]

                title = current_clause

                print("\nCLAUSE DETECTED")

                print(f"CLAUSE ID : {current_clause}")

                # -----------------------------------------
                # Next line as title
                # -----------------------------------------

                if index + 1 < len(elements):

                    next_element = elements[index + 1]

                    print("\nNEXT ELEMENT")

                    print(
                        f"TEXT      : {next_element['text']}"
                    )

                    print(
                        f"BOLD      : {next_element['bold']}"
                    )

                    print(
                        f"FONT SIZE : {next_element['font_size']}"
                    )

                    if (

                        next_element["bold"]

                        and len(
                            next_element["text"].split()
                        ) <= 12

                    ):

                        title = (
                            current_clause
                            + " "
                            + next_element["text"]
                        )

                        print(
                            "USING NEXT ELEMENT AS TITLE"
                        )

                    else:

                        print(
                            "NEXT ELEMENT NOT USED"
                        )

                current_title = title

                print(
                    f"FINAL TITLE : {current_title}"
                )

            # =====================================================
            # Assign Clause
            # =====================================================

            element["clause_id"] = current_clause

            element["clause_title"] = current_title

            print("\nASSIGNED")

            print(
                f"Clause ID    : {current_clause}"
            )

            print(
                f"Clause Title : {current_title}"
            )

            index += 1

        print("\nPAGE SUMMARY")

        print(
            f"Current Clause : {current_clause}"
        )

    # =====================================================
    # Summary
    # =====================================================

    print("\n" + "=" * 120)

    print("CLAUSE DETECTION SUMMARY")

    print("=" * 120)

    print(
        f"TOTAL PAGES   : {len(pages)}"
    )

    print(
        f"TOTAL CLAUSES : {clause_counter}"
    )

    print("=" * 120)

    print("CLAUSE DETECTION COMPLETE")

    print("=" * 120)

    return pages