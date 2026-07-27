from retrieval.search.hybrid_search import (
    hybrid_search,
)

MAX_CONTEXT_WORDS = 2500


def get_context(
    question,
    document_id,
):

    print("\n" + "=" * 80)
    print("CONTEXT BUILDER")
    print("=" * 80)

    print(f"QUESTION    : {question}")
    print(f"DOCUMENT ID : {document_id}")

    results = hybrid_search(
        question,
        document_id,
    )

    print(
        f"\nRETRIEVED CHUNKS : {len(results)}"
    )

    chunks = []

    total_words = 0

    for row in results:

        chunk_words = len(
            row["content"].split()
        )

        if total_words + chunk_words > MAX_CONTEXT_WORDS:

            print(
                "\nMAX CONTEXT SIZE REACHED"
            )

            break

        print(
            f"ADDING CHUNK : {row['id']}"
        )

        print(
            f"CHUNK WORDS : {chunk_words}"
        )

        chunks.append(
            row["content"]
        )

        total_words += chunk_words

    context = "\n\n".join(chunks)

    print(
        f"\nFINAL CONTEXT WORDS : {total_words}"
    )

    print("=" * 80)

    return context