import re


MAX_WORDS = 900
OVERLAP_WORDS = 80


def detect_chunk_type(clause):

    section = clause.get(
        "section",
        "",
    ).lower()

    title = clause.get(
        "clause_title",
        "",
    ).lower()

    text = clause.get(
        "content",
        "",
    ).lower()

    combined = f"{section} {title} {text}"

    if "definition" in combined:
        return "definition"

    if "benefit" in combined:
        return "benefit"

    if "exclusion" in combined:
        return "exclusion"

    if "waiting period" in combined:
        return "waiting_period"

    if "claim" in combined:
        return "claim"

    if "condition" in combined:
        return "condition"

    return "clause"


def split_large_clause(text):

    """
    Split a very large clause while preserving sentence boundaries.
    """

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text,
    )

    chunks = []

    current = []

    current_words = 0

    for sentence in sentences:

        words = len(sentence.split())

        if (
            current_words + words > MAX_WORDS
            and current
        ):

            chunks.append(
                " ".join(current)
            )

            overlap = []

            overlap_words = 0

            for s in reversed(current):

                overlap.insert(0, s)

                overlap_words += len(
                    s.split()
                )

                if overlap_words >= OVERLAP_WORDS:

                    break

            current = overlap

            current_words = sum(
                len(x.split())
                for x in current
            )

        current.append(sentence)

        current_words += words

    if current:

        chunks.append(
            " ".join(current)
        )

    return chunks


def create_semantic_chunks(clauses):

    print("\n" + "=" * 120)
    print("SEMANTIC CHUNKING STARTED")
    print("=" * 120)

    chunks = []

    chunk_id = 1

    total_words = 0

    for clause_index, clause in enumerate(
        clauses,
        start=1,
    ):

        print("\n" + "=" * 120)
        print(f"CLAUSE {clause_index}")
        print("=" * 120)

        content = clause.get(
            "content",
            "",
        ).strip()

        if not content:

            print("EMPTY CLAUSE -> SKIPPED")
            continue

        words = len(content.split())

        total_words += words

        chunk_type = detect_chunk_type(
            clause
        )

        print(f"SECTION      : {clause.get('section')}")
        print(f"CLAUSE ID    : {clause.get('clause_id')}")
        print(f"TITLE        : {clause.get('clause_title')}")
        print(f"PAGES        : {clause.get('page_start')} -> {clause.get('page_end')}")
        print(f"WORDS        : {words}")
        print(f"CHUNK TYPE   : {chunk_type}")

        print("\nMETADATA")

        metadata = clause.get(
            "metadata",
            {},
        )

        if metadata:

            for key, value in metadata.items():

                print(f"{key} : {value}")

        else:

            print("No metadata")

        print("\nCONTENT PREVIEW")
        print("-" * 80)

        preview = content[:800]

        print(preview)

        if len(content) > 800:

            print("\n...")

        print("-" * 80)

        # =====================================================
        # SMALL CLAUSE
        # =====================================================

        if words <= MAX_WORDS:

            chunk = {

                "chunk_id": chunk_id,

                "section": clause.get(
                    "section",
                    "General",
                ),

                "clause_id": clause.get(
                    "clause_id",
                    "",
                ),

                "clause_title": clause.get(
                    "clause_title",
                    "",
                ),

                "page_start": clause.get(
                    "page_start",
                    1,
                ),

                "page_end": clause.get(
                    "page_end",
                    1,
                ),

                "chunk_type": chunk_type,

                "metadata": metadata,

                "content": content,
            }

            chunks.append(chunk)

            print("\nCREATED SINGLE CHUNK")
            print(f"Chunk ID : {chunk_id}")
            print(f"Words    : {words}")

            chunk_id += 1

            continue

        # =====================================================
        # LARGE CLAUSE
        # =====================================================

        print("\nLARGE CLAUSE DETECTED")

        parts = split_large_clause(
            content
        )

        print(f"TOTAL PARTS : {len(parts)}")

        total_parts = len(parts)

        for part_number, part in enumerate(
            parts,
            start=1,
        ):

            chunk = {

                "chunk_id": chunk_id,

                "section": clause.get(
                    "section",
                    "General",
                ),

                "clause_id": clause.get(
                    "clause_id",
                    "",
                ),

                "clause_title": clause.get(
                    "clause_title",
                    "",
                ),

                "page_start": clause.get(
                    "page_start",
                    1,
                ),

                "page_end": clause.get(
                    "page_end",
                    1,
                ),

                "chunk_type": chunk_type,

                "part": part_number,

                "total_parts": total_parts,

                "metadata": metadata,

                "content": part,
            }

            chunks.append(chunk)

            print("\n" + "-" * 80)
            print(f"CHUNK {chunk_id}")
            print("-" * 80)

            print(
                f"PART : {part_number}/{total_parts}"
            )

            print(
                f"WORDS : {len(part.split())}"
            )

            print("\nCONTENT")

            print(part[:500])

            if len(part) > 500:

                print("\n...")

            chunk_id += 1

    print("\n" + "=" * 120)
    print("SEMANTIC CHUNKING SUMMARY")
    print("=" * 120)

    print(f"TOTAL CLAUSES      : {len(clauses)}")
    print(f"TOTAL CHUNKS       : {len(chunks)}")
    print(f"TOTAL WORDS        : {total_words}")

    if chunks:

        average = round(
            total_words / len(chunks),
            2,
        )

        print(
            f"AVERAGE WORDS/CHUNK : {average}"
        )

    print("=" * 120)

    print("SEMANTIC CHUNKING COMPLETE")

    print("=" * 120)

    return chunks