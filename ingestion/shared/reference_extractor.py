import re

URL_PATTERN = re.compile(
    r"https?://[^\s]+"
)


def extract_references(reference_pages):

    references = []

    current_reference = None
    order = 1

    skip_patterns = [
        "RECOMMENDED RESOURCES",
        "ARTICLES",
        "MULTIMEDIA",
        "BOOKS",
        "VARIOUS RESOURCES",
    ]

    for page in reference_pages:

        page_number = page["page"]

        for item in page["elements"]:

            text = item["text"].strip()

            if not text:
                continue

            if text == "•":
                continue

            if any(
                p in text.upper()
                for p in skip_patterns
            ):
                continue

            # New reference starts with author + year
            if re.search(
                r"\(\d{4}\)",
                text
            ):

                if current_reference:

                    references.append(
                        current_reference
                    )

                urls = URL_PATTERN.findall(text)

                current_reference = {
                    "reference_type": "REFERENCE",
                    "reference_text": text,
                    "reference_url":
                        urls[0] if urls else None,
                    "reference_order": order,
                    "page_start": page_number,
                    "page_end": page_number,
                }

                order += 1

            else:

                if current_reference:

                    current_reference[
                        "reference_text"
                    ] += " " + text

                    urls = URL_PATTERN.findall(text)

                    if (
                        urls
                        and not current_reference[
                            "reference_url"
                        ]
                    ):
                        current_reference[
                            "reference_url"
                        ] = urls[0]

    if current_reference:

        references.append(
            current_reference
        )

    return references