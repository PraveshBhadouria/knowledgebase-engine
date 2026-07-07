from collections import Counter
import re
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# =============================================================================
# CONFIG
# =============================================================================

REFERENCE_SECTIONS = {
    "REFERENCES",
    "BIBLIOGRAPHY",
}

RESOURCE_SECTIONS = {
    "1. RECOMMENDED RESOURCES",
    "1 RECOMMENDED RESOURCES",
    "1.1 BOOKS",
    "1.2 ARTICLES",
    "1.3 MULTIMEDIA",
}

SPECIAL_HEADINGS = {
    "section overview",
    "learning outcomes",
    "key points",
    "prescribed textbooks",
    "prescribed multimedia",
    "timeframe",
}

TABLE_SECTION_LABELS = {
    "timeframe",
    "learning outcomes",
    "prescribed textbooks",
    "prescribed multimedia",
    "section overview",
    "assessment criteria",
    "key concepts",
    "additional resources",
}

NOISE_PHRASES = [
    "copyright",
    "all rights reserved",
    "contact us",
    "visit us",
    "privacy policy",
    "terms and conditions",
]

MAX_HEADING_WORDS = 25


# =============================================================================
# HELPERS
# =============================================================================

def _bucket_font(size):
    return round(round(size / 0.5) * 0.5, 1)


# =============================================================================
# PAGE SKIPPING
# =============================================================================

def is_cover_page(elements):

    page_text = " ".join(
        item["text"].lower()
        for item in elements
    )

    cover_keywords = [
        "master of business",
        "contact details",
        "regenesys business school",
        "www.regenesys",
        "e-mail:",
        "fax:",
        "tel:",
    ]

    matches = sum(
        1
        for keyword in cover_keywords
        if keyword in page_text
    )

    return matches >= 3


def is_copyright_page(elements):

    page_text = " ".join(
        item["text"].lower()
        for item in elements
    )

    keywords = [
        "copyright",
        "all rights reserved",
        "retrieval system",
        "criminal prosecution",
        "civil claims",
    ]

    matches = sum(
        1
        for keyword in keywords
        if keyword in page_text
    )

    return matches >= 2


def is_toc_page(elements):

    dot_lines = 0
    numbered_lines = 0

    for e in elements:

        text = e["text"].strip()

        if re.search(
            r"\.{5,}",
            text,
        ):
            dot_lines += 1

        # Detect numbers like 3.10, 3.11, 4, 5 OR "3.1 Introduction"
        if re.match(
            r"^\d+(\.\d+)*(\s+.*)?$",
            text,
        ):
            numbered_lines += 1

    return (
        dot_lines >= 5
        or numbered_lines >= 15
        or (
            numbered_lines >= 8
            and dot_lines >= 3
        )
    )


def is_resource_page(elements):

    for item in elements:
        text = item["text"].strip().upper()
        
        if text in RESOURCE_SECTIONS:
            logger.info(f"📚 RESOURCE PAGE DETECTED "f"| Text='{text}'")
            return True
    return False


# =============================================================================
# NOISE DETECTION
# =============================================================================

def is_noise(text, dynamic_noise):

    t = text.strip().lower()

    if not t:
        return True

    if t in dynamic_noise:
        return True

    if re.match(
        r"^(page\s+\d+|\d+\s*/\s*\d+|\d+)$",
        t,
    ):
        return True

    if re.match(
        r"^©\s*regenesys",
        t,
        re.I,
    ):
        return True

    if any(
        phrase in t
        for phrase in NOISE_PHRASES
    ):
        return True

    if t == "•":
        return True

    return False


def detect_dynamic_headers_footers(
    layout_pages,
):

    candidates = Counter()

    for page in layout_pages:

        for item in page["elements"]:

            text = item["text"].strip()

            if len(text) < 3:
                continue

            bbox = item.get("bbox")

            if not bbox:
                continue

            y0 = bbox[1]
            y1 = bbox[3]

            if y0 < 80 or y1 > 730:

                candidates[
                    text.lower()
                ] += 1

    return {
        text
        for text, count in candidates.items()
        if count >= 3
    }


# =============================================================================
# FALSE POSITIVE FILTER (UPDATED WITH STRICT MATH REJECTION)
# =============================================================================

def is_false_positive(text):

    t = text.strip()

    if not t:
        logger.info(f"❌ FALSE POSITIVE | Reason=EMPTY_TEXT | Text='{t}'")
        return True

    # Too long
    if len(t.split()) > MAX_HEADING_WORDS:
        logger.info(f"❌ FALSE POSITIVE | Reason=TOO_LONG | Text='{t}'")
        return True

    # Single character
    if len(t) <= 2:
        logger.info(f"❌ FALSE POSITIVE | Reason=TOO_SHORT | Text='{t}'")
        return True

    # Single short word
    if len(t.split()) == 1 and len(t) < 15:
        logger.info(f"❌ FALSE POSITIVE | Reason=SINGLE_SHORT_WORD | Text='{t}'")
        return True

    # Pure numbering
    if re.match(
        r"^\d+(\.\d+)*$",
        t,
    ):
        logger.info(f"❌ FALSE POSITIVE | Reason=PURE_NUMBERING | Text='{t}'")
        return True

    # ==========================================
    # MATH & FORMULA DETECTION
    # ==========================================
    
    # Check for math symbols AND standard Greek letters often used in formulas
    if re.search(
        r"[μσ√∑±≈≤≥Σαβγπ∞∫∆θ]", 
        t,
    ):
        logger.info(f"❌ FALSE POSITIVE | Reason=MATH_SYMBOL | Text='{t}'")
        return True

    # Detect common equation patterns (e.g., "x = ...", "y=", "P(x)")
    # If a short string contains an equals sign, it is almost certainly a formula, not a heading
    if "=" in t and len(t.split()) <= 8:
        logger.info(f"❌ FALSE POSITIVE | Reason=FORMULA | Text='{t}'")
        return True
        
    if re.match(r"^[A-Za-z]\s*=", t):
        logger.info(f"❌ FALSE POSITIVE | Reason=FORMULA | Text='{t}'")
        return True

    # Mostly symbols (fractions, math notation)
    symbol_count = sum(
        not c.isalnum() and not c.isspace()
        for c in t
    )

    if len(t) > 0:

        if (
            symbol_count / len(t)
            > 0.30
        ):
            logger.info(f"❌ FALSE POSITIVE | Reason=SYMBOL_HEAVY | Text='{t}'")
            return True

    # Citations
    if re.search(
        r"\(\d{4}",
        t,
    ):
        logger.info(f"❌ FALSE POSITIVE | Reason=CITATION | Text='{t}'")
        return True

    if re.search(
        r"\b(et al\.|doi|isbn|issn|vol\.|pp\.)\b",
        t,
        re.I,
    ):
        logger.info(f"❌ FALSE POSITIVE | Reason=CITATION | Text='{t}'")
        return True

    # Author names
    if re.search(
        r"^[A-Z][a-z]+,\s+[A-Z]",
        t,
    ):
        logger.info(f"❌ FALSE POSITIVE | Reason=AUTHOR_NAME | Text='{t}'")
        return True

    # Contact information
    if re.search(
        r"(fax|phone|email|tel)\s*:",
        t,
        re.I,
    ):
        logger.info(f"❌ FALSE POSITIVE | Reason=CONTACT_INFO | Text='{t}'")
        return True

    # URLs
    if re.search(
        r"https?://|www\.|@",
        t,
        re.I,
    ):
        logger.info(f"❌ FALSE POSITIVE | Reason=URL | Text='{t}'")
        return True

    # Figure/Table captions
    if re.match(
        r"^(figure|fig|table|chart|graph)\s+\d+",
        t,
        re.I,
    ):
        logger.info(f"❌ FALSE POSITIVE | Reason=FIGURE_TABLE_CAPTION | Text='{t}'")
        return True

    # Explicit garbage headings
    invalid = {
        "general",
        "professional",
        "scales",
        "anova",
        "summary output",
        "n",
        "5 +",
        "5+",
    }

    if t.lower() in invalid:
        logger.info(f"❌ FALSE POSITIVE | Reason=INVALID_KEYWORD | Text='{t}'")
        return True

    return False


# =============================================================================
# EXPLICIT HEADING DETECTION
# =============================================================================

def detect_explicit_heading(text):

    t = text.strip()

    if is_false_positive(t):
        return None

    if t.lower() in SPECIAL_HEADINGS:
        logger.info(f"🎯 EXPLICIT HEADING | Type=SUBSECTION | Text='{t}'")
        return "subsection"

    if re.match(
        r"^(CHAPTER|UNIT|PART|MODULE|LESSON|APPENDIX)\s+\d+",
        t,
        re.I,
    ):
        logger.info(f"🎯 EXPLICIT HEADING | Type=CHAPTER | Text='{t}'")
        return "chapter"

    if re.match(
        r"^\d+\.\d+\.\d+\.\d+\s+",
        t,
    ):
        logger.info(f"🎯 EXPLICIT HEADING | Type=SUBSUBSECTION | Text='{t}'")
        return "subsubsection"

    if re.match(
        r"^\d+\.\d+\.\d+\s+",
        t,
    ):
        logger.info(f"🎯 EXPLICIT HEADING | Type=SUBSECTION | Text='{t}'")
        return "subsection"

    if re.match(
        r"^\d+\.\d+\s+",
        t,
    ):
        logger.info(f"🎯 EXPLICIT HEADING | Type=SECTION | Text='{t}'")
        return "section"

    if re.match(
        r"^\d+\s+[A-Z]",
        t,
    ):
        logger.info(f"🎯 EXPLICIT HEADING | Type=CHAPTER | Text='{t}'")
        return "chapter"

    return None


def detect_semantic_label(text):

    t = text.strip().lower()

    if t in TABLE_SECTION_LABELS:
        return "subsection"

    return None


def is_sentence(text):

    words = text.split()

    if len(words) > 10:
        return True

    if text.endswith(":"):
        return True

    if text.endswith("."):
        return True

    return False


# =============================================================================
# HEADING VALIDATION
# =============================================================================

def is_valid_heading(text):

    t = text.strip()

    if is_false_positive(t):
        return False

    if len(t) < 4:
        return False

    # Reject single random words
    if (
        len(t.split()) == 1
        and not re.match(
            r"^\d+\.\d+\.\d+\s+",
            t,
        )
    ):
        return False

    return True


# =============================================================================
# VISUAL HEADING DETECTION
# =============================================================================

def detect_visual_heading(
    item,
    body_font,
    in_reference_mode,
):

    if in_reference_mode:
        return None

    text = item["text"].strip()

    if is_false_positive(text):
        return None

    if is_sentence(text):
        return None

    words = len(text.split())

    if words > 10:
        return None

    size = item["font_size"]

    # -------------------------------------------------
    # CHAPTER
    # -------------------------------------------------

    if (
        size >= body_font + 6
        and words <= 8
        and len(text) >= 5
    ):
        logger.info(f"👀 VISUAL HEADING | Type=CHAPTER | Font={size} | BodyFont={body_font} | Text='{text}'")
        return "chapter"

    # -------------------------------------------------
    # SECTION
    # -------------------------------------------------

    if (
        size >= body_font + 2
        and words <= 8
        and len(text) >= 5
        and not text.endswith(":")
    ):

        # Reject short random words
        if words == 1:
            return None

        logger.info(f"👀 VISUAL HEADING | Type=SECTION | Font={size} | BodyFont={body_font} | Text='{text}'")
        return "section"

    # -------------------------------------------------
    # SUBSECTION
    # -------------------------------------------------

    alpha = re.findall(
        r"[A-Za-z]",
        text,
    )

    if alpha:

        upper_ratio = (
            sum(
                c.isupper()
                for c in alpha
            )
            / len(alpha)
        )

        if (
            upper_ratio > 0.80
            and words > 1
            and words <= 8
        ):
            logger.info(f"👀 VISUAL HEADING | Type=SUBSECTION | Font={size} | BodyFont={body_font} | UppercaseRatio={upper_ratio:.2f} | Text='{text}'")
            return "subsection"

    return None


# =============================================================================
# MAIN ENGINE
# =============================================================================

def build_hierarchy(layout_pages):

    dynamic_noise = detect_dynamic_headers_footers(
        layout_pages
    )

    font_sizes = []

    # ======================================================
    # DETECT BODY FONT
    # ======================================================

    for page in layout_pages:

        for item in page["elements"]:

            if is_noise(
                item["text"],
                dynamic_noise,
            ):
                continue

            font_sizes.append(
                _bucket_font(
                    item["font_size"]
                )
            )

    body_font = Counter(
        font_sizes
    ).most_common(1)[0][0]

    print(
        f"\nBODY FONT DETECTED: {body_font}"
    )

    current_chapter = ""
    current_section = ""
    current_subsection = ""
    current_subsubsection = ""

    in_reference_mode = False
    in_resource_section = False

    structured = []
    reference_pages = []

    for page in layout_pages:

        # ======================================================
        # SKIP COVER PAGE
        # ======================================================

        if is_cover_page(page["elements"]):

            logger.info(
                f"⏭️ SKIPPING PAGE {page['page']} | Reason=COVER_PAGE"
            )

            structured.append(
                {
                    "page": page["page"],
                    "elements": [],
                }
            )

            continue

        # ======================================================
        # SKIP COPYRIGHT PAGE
        # ======================================================

        if is_copyright_page(page["elements"]):

            logger.info(
                f"⏭️ SKIPPING PAGE {page['page']} | Reason=COPYRIGHT_PAGE"
            )

            structured.append(
                {
                    "page": page["page"],
                    "elements": [],
                }
            )

            continue

        # ======================================================
        # SKIP TOC PAGE
        # ======================================================

        if is_toc_page(page["elements"]):

            logger.info(
                f"⏭️ SKIPPING PAGE {page['page']} | Reason=TOC_PAGE"
            )

            structured.append(
                {
                    "page": page["page"],
                    "elements": [],
                }
            )

            continue



        # ======================================================
        # SKIP VERSION CONTROL
        # ======================================================

        if any(
            "VERSION CONTROL" in e["text"].upper()
            for e in page["elements"]
        ):

            logger.info(
                f"⏭️ SKIPPING PAGE {page['page']} | Reason=VERSION_CONTROL"
            )

            structured.append(
                {
                    "page": page["page"],
                    "elements": [],
                }
            )

            continue

        # ======================================================
        # RESOURCE SECTION START
        # ======================================================

        if is_resource_page(page["elements"]):
            in_resource_section = True

        page_text = " ".join(
            e["text"]
            for e in page["elements"]
        ).upper()

        # ======================================================
        # RESOURCE SECTION END
        # ======================================================

        if (
            "2. INTRODUCTION TO THIS COURSE" in page_text
            or
            "2 INTRODUCTION TO THIS COURSE" in page_text
        ):

            logger.info(
                f"📚 RESOURCE SECTION ENDED ON PAGE {page['page']}"
            )

            in_resource_section = False

        if in_resource_section:

            logger.info(
                f"⏭️ SKIPPING PAGE {page['page']} | Reason=RESOURCE_PAGE"
            )

            structured.append(
                {
                    "page": page["page"],
                    "elements": [],
                }
            )

            continue

        page_output = []
        if any(
            "GLOSSARY" in e["text"].upper()
            or "VERSION CONTROL" in e["text"].upper()
            for e in page["elements"]
        ):
            if in_reference_mode:
                logger.info(
                    f"📚 EXITING REFERENCE MODE | PAGE={page['page']}"
                )

            in_reference_mode = False

        for item in page["elements"]:

            text = item["text"].strip()

            if is_noise(
                text,
                dynamic_noise,
            ):
                continue

            # ======================================================
            # REFERENCE SECTION DETECTION
            # ======================================================

            if any(
                re.search(
                    rf"\b{ref}\b",
                    text.upper()
                )
                for ref in REFERENCE_SECTIONS
            ):

                logger.info(
                    f"📚 ENTERING REFERENCE MODE | "
                    f"PAGE={page['page']} | "
                    f"TEXT='{text}'"
                )

                in_reference_mode = True

            # ======================================================
            # HEADING DETECTION
            # ======================================================

            detector_used = "NONE"

            heading_type = detect_explicit_heading(
                text
            )

            if heading_type:
                detector_used = "EXPLICIT"

            if (
                heading_type
                and not is_valid_heading(text)
            ):
                heading_type = None
                detector_used = "NONE"

            if not heading_type:

                heading_type = detect_semantic_label(
                    text
                )

                if heading_type:
                    detector_used = "SEMANTIC"

            if not heading_type:

                heading_type = detect_visual_heading(
                    item,
                    body_font,
                    in_reference_mode,
                )

                if heading_type:
                    detector_used = "VISUAL"

            if (
                heading_type
                and not is_valid_heading(text)
            ):
                heading_type = None
                detector_used = "NONE"


            # ======================================================
            # UPDATE HIERARCHY
            # ======================================================

            if heading_type == "chapter":

                logger.info(
                    f"📘 NEW CHAPTER -> {text}"
                )

                current_chapter = text
                current_section = ""
                current_subsection = ""
                current_subsubsection = ""


            elif heading_type == "section":

                logger.info(
                    f"📗 NEW SECTION -> {text}"
                )

                current_section = text
                current_subsection = ""
                current_subsubsection = ""

            elif heading_type == "subsection":

                if not in_reference_mode:

                    logger.info(
                        f"📙 NEW SUBSECTION -> {text}"
                    )

                    current_subsection = text
                    current_subsubsection = ""

            elif heading_type == "subsubsection":

                if not in_reference_mode:

                    logger.info(
                        f"📕 NEW SUBSUBSECTION -> {text}"
                    )

                    current_subsubsection = text

            logger.info(
                "\n"
                f"PAGE            : {page['page']}\n"
                f"TEXT            : {text}\n"
                f"FONT            : {item['font_size']}\n"
                f"BOLD            : {item.get('bold', False)}\n"
                f"DETECTOR        : {detector_used}\n"
                f"HEADING TYPE    : {heading_type}\n"
                f"CHAPTER         : {current_chapter}\n"
                f"SECTION         : {current_section}\n"
                f"SUBSECTION      : {current_subsection}\n"
                f"SUBSUBSECTION   : {current_subsubsection}"
            )

            page_output.append(
                {
                    **item,
                    "is_heading": bool(
                        heading_type
                    ),
                    "heading_type": heading_type,
                    "chapter": current_chapter,
                    "section": current_section,
                    "subsection": current_subsection,
                    "subsubsection": current_subsubsection,
                }
            )

        # ======================================================
        # STORE REFERENCE PAGE ONCE PER PAGE
        # ======================================================

        if in_reference_mode:

            logger.info(
                f"📚 STORING REFERENCE PAGE {page['page']}"
            )

            reference_pages.append(
                {
                    "page": page["page"],
                    "elements": page_output
                }
            )

        structured.append(
            {
                "page": page["page"],
                "elements": page_output,
            }
        )

    return structured, reference_pages