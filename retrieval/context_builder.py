from retrieval.search.hybrid_search import hybrid_search

MAX_CONTEXT_WORDS = 2500


def get_context(question):

    results = hybrid_search(question)

    print("\nCONTEXT BUILDER")

    print("Retrieved Chunks:", len(results))

    chunks = []

    total_words = 0

    for row in results:

        chunk_words = len(row["content"].split())

        if total_words + chunk_words > MAX_CONTEXT_WORDS:
            break

        print("Chunk Length:", chunk_words)

        chunks.append(row["content"])

        total_words += chunk_words

    context = "\n\n".join(chunks)

    print("Final Context Words:", total_words)

    return context
