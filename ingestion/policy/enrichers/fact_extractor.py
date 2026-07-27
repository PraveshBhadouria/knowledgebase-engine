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


BENEFIT_PATTERNS = [

    "ambulance",

    "room rent",

    "icu",

    "maternity",

    "day care",

    "dialysis",

    "chemotherapy",

    "organ donor",

    "ayush",

    "domiciliary",

    "pre hospitalization",

    "post hospitalization",

]


def extract_facts(clauses):

    print("\n" + "=" * 120)
    print("FACT EXTRACTION STARTED")
    print("=" * 120)

    processed = []

    benefit_counter = {}

    covered_true = 0
    covered_false = 0

    for index, clause in enumerate(
        clauses,
        start=1,
    ):

        print("\n" + "=" * 120)
        print(f"CLAUSE {index}")
        print("=" * 120)

        print(f"CLAUSE ID    : {clause.get('clause_id')}")
        print(f"SECTION      : {clause.get('section')}")
        print(f"TITLE        : {clause.get('clause_title')}")

        text = clause["content"]

        lower = text.lower()

        print(
            f"TOTAL WORDS  : {len(text.split())}"
        )

        print("\nCONTENT PREVIEW")
        print("-" * 100)

        print(text[:600])

        if len(text) > 600:
            print("\n...")

        print("-" * 100)

        metadata = clause.get(
            "metadata",
            {},
        )

        # =====================================================
        # Benefit
        # =====================================================

        metadata["benefit_name"] = None

        for benefit in BENEFIT_PATTERNS:

            if benefit in lower:

                metadata["benefit_name"] = benefit

                benefit_counter[benefit] = (
                    benefit_counter.get(
                        benefit,
                        0,
                    )
                    + 1
                )

                break

        # =====================================================
        # Coverage
        # =====================================================

        money = MONEY_PATTERN.findall(text)

        metadata["coverage_limit"] = (

            money[0]

            if money

            else None

        )

        # =====================================================
        # Waiting Period
        # =====================================================

        waiting = WAITING_PATTERN.findall(text)

        metadata["waiting_period_value"] = (

            waiting[0]

            if waiting

            else None

        )

        # =====================================================
        # Copayment
        # =====================================================

        percentage = PERCENT_PATTERN.findall(text)

        metadata["copayment"] = (

            percentage[0]

            if percentage

            else None

        )

        # =====================================================
        # Covered
        # =====================================================

        metadata["covered"] = None

        if any(

            word in lower

            for word in [

                "covered",

                "payable",

                "reimburse",

                "indemnify",

            ]

        ):

            metadata["covered"] = True

            covered_true += 1

        if any(

            word in lower

            for word in [

                "not covered",

                "excluded",

                "shall not",

                "not payable",

            ]

        ):

            metadata["covered"] = False

            covered_false += 1

        # =====================================================
        # Room Type
        # =====================================================

        metadata["room_type"] = None

        if "single private" in lower:

            metadata["room_type"] = "Single Private Room"

        elif "shared room" in lower:

            metadata["room_type"] = "Shared Room"

        elif "icu" in lower:

            metadata["room_type"] = "ICU"

        clause["metadata"] = metadata

        processed.append(clause)

        # =====================================================
        # LOG FACTS
        # =====================================================

        print("\nEXTRACTED FACTS")
        print("-" * 100)

        for key, value in metadata.items():

            print(f"{key:<25}: {value}")

        print("-" * 100)

    # =====================================================
    # SUMMARY
    # =====================================================

    print("\n" + "=" * 120)
    print("FACT EXTRACTION SUMMARY")
    print("=" * 120)

    print(
        f"TOTAL CLAUSES : {len(processed)}"
    )

    print(
        f"COVERED TRUE  : {covered_true}"
    )

    print(
        f"COVERED FALSE : {covered_false}"
    )

    print("\nBENEFITS FOUND")

    print("-" * 100)

    if benefit_counter:

        for benefit, count in sorted(
            benefit_counter.items(),
            key=lambda x: x[1],
            reverse=True,
        ):

            print(
                f"{benefit:<25} : {count}"
            )

    else:

        print("No benefits detected.")

    print("-" * 100)

    print("FACT EXTRACTION COMPLETE")
    print("=" * 120)

    return processed