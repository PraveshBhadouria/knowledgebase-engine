import re


def detect_block_type(item):

    text = item["text"].strip()

    # ------------------------------------------------
    # TABLE TITLE
    # ------------------------------------------------

    if re.match(
        r"^(TABLE|TAB)\s+\d+",
        text,
        re.I,
    ):
        return "table_title"

    # ------------------------------------------------
    # FIGURE TITLE
    # ------------------------------------------------

    if re.match(
        r"^(FIGURE|FIG)\s+\d+",
        text,
        re.I,
    ):
        return "figure_title"

    # ------------------------------------------------
    # ACTIVITY
    # ------------------------------------------------

    if (
        "case study" in text.lower()
        or "answer the questions" in text.lower()
    ):
        return "activity"

    # ------------------------------------------------
    # BULLET
    # ------------------------------------------------

    if text.startswith("•"):
        return "bullet"

    # ------------------------------------------------
    # NORMAL
    # ------------------------------------------------

    return "paragraph"