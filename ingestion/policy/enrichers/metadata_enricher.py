import re


MONEY_PATTERN = re.compile(
    r"(₹\s?\d[\d,]*|\bINR\s?\d[\d,]*)",
    re.IGNORECASE,
)

PERCENT_PATTERN = re.compile(
    r"\d+(?:\.\d+)?\s?%",
)

WAITING_PATTERN = re.compile(
    r"\d+\s*(?:day|days|month|months|year|years)",
    re.IGNORECASE,
)

AGE_PATTERN = re.compile(
    r"\d+\s*years?",
    re.IGNORECASE,
)


BENEFIT_KEYWORDS = [

    "ambulance",

    "icu",

    "room rent",

    "hospitalization",

    "organ donor",

    "dialysis",

    "chemotherapy",

    "ayush",

    "maternity",

    "day care",

    "road ambulance",

    "air ambulance",

    "domiciliary",

    "pre hospitalization",

    "post hospitalization",

]


EXCLUSION_KEYWORDS = [

    "cosmetic",

    "war",

    "suicide",

    "self injury",

    "alcohol",

    "drug abuse",

    "fertility",

]


def enrich_metadata(clauses):

    print("\n" + "=" * 120)
    print("METADATA ENRICHMENT STARTED")
    print("=" * 120)

    enriched = []

    total_money = 0
    total_benefits = 0
    total_exclusions = 0

    for index, clause in enumerate(
        clauses,
        start=1,
    ):

        print("\n" + "=" * 120)
        print(f"CLAUSE {index}")
        print("=" * 120)

        print(f"CLAUSE ID : {clause.get('clause_id')}")
        print(f"SECTION   : {clause.get('section')}")
        print(f"TITLE     : {clause.get('clause_title')}")

        text = clause["content"]

        lower = text.lower()

        print(
            f"WORDS     : {len(text.split())}"
        )

        print("\nCONTENT PREVIEW")
        print("-" * 100)

        preview = text[:700]

        print(preview)

        if len(text) > 700:

            print("\n...")

        print("-" * 100)

        metadata = {}

        # =====================================================
        # MONEY
        # =====================================================

        metadata["money"] = sorted(
            list(
                set(
                    MONEY_PATTERN.findall(text)
                )
            )
        )

        total_money += len(
            metadata["money"]
        )

        # =====================================================
        # PERCENTAGE
        # =====================================================

        metadata["percentage"] = sorted(
            list(
                set(
                    PERCENT_PATTERN.findall(text)
                )
            )
        )

        # =====================================================
        # WAITING PERIOD
        # =====================================================

        metadata["waiting_period"] = sorted(
            list(
                set(
                    WAITING_PATTERN.findall(text)
                )
            )
        )

        # =====================================================
        # AGE
        # =====================================================

        metadata["age"] = sorted(
            list(
                set(
                    AGE_PATTERN.findall(text)
                )
            )
        )

        # =====================================================
        # BENEFITS
        # =====================================================

        benefits = []

        for word in BENEFIT_KEYWORDS:

            if word in lower:

                benefits.append(word)

        metadata["benefits"] = benefits

        total_benefits += len(benefits)

        # =====================================================
        # EXCLUSIONS
        # =====================================================

        exclusions = []

        for word in EXCLUSION_KEYWORDS:

            if word in lower:

                exclusions.append(word)

        metadata["exclusions"] = exclusions

        total_exclusions += len(
            exclusions
        )

        clause["metadata"] = metadata

        enriched.append(clause)

        # =====================================================
        # LOG METADATA
        # =====================================================

        print("\nEXTRACTED METADATA")
        print("-" * 100)

        for key, value in metadata.items():

            print(f"{key:<20}: {value}")

        print("-" * 100)

    # =====================================================
    # SUMMARY
    # =====================================================

    print("\n" + "=" * 120)
    print("METADATA ENRICHMENT SUMMARY")
    print("=" * 120)

    print(
        f"TOTAL CLAUSES      : {len(enriched)}"
    )

    print(
        f"TOTAL MONEY VALUES : {total_money}"
    )

    print(
        f"TOTAL BENEFITS     : {total_benefits}"
    )

    print(
        f"TOTAL EXCLUSIONS   : {total_exclusions}"
    )

    print("=" * 120)
    print("METADATA ENRICHMENT COMPLETE")
    print("=" * 120)

    return enriched