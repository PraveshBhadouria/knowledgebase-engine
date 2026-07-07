from retrieval.search.exact_search import (
    exact_search,
)

from retrieval.search.keyword_search import (
    keyword_search,
)

from retrieval.search.vector_search import (
    vector_search,
)

from retrieval.rerankers.reranker import (
    rerank,
)

from ingestion.shared.keyword_extractor import (
    extract_keywords,
)


def hybrid_search(query):

    print("\n")
    print("=" * 80)
    print("SEARCH REQUEST")
    print("=" * 80)

    print("Query:", query)

    # -----------------------------------------
    # EXACT SEARCH
    # -----------------------------------------

    exact_results = exact_search(
        query
    )

    if exact_results:

        print(
            f"\nEXACT MATCH FOUND: {len(exact_results)}"
        )

        results = []

        for row in exact_results:

            results.append(
                {
                    "id": row[0],
                    "section": row[1],
                    "content": row[2],
                    "score": 999,
                }
            )

        return results

    # -----------------------------------------
    # QUERY KEYWORDS
    # -----------------------------------------

    query_keywords = extract_keywords(
        query
    )

    print("\nQUERY KEYWORDS")

    for keyword in query_keywords:

        print(
            f"- {keyword}"
        )

    # -----------------------------------------
    # KEYWORD SEARCH
    # -----------------------------------------

    keyword_results = keyword_search(
        query_keywords
    )

    print(
        "\nKeyword Results:",
        len(keyword_results)
    )

    # -----------------------------------------
    # VECTOR SEARCH
    # -----------------------------------------

    vector_results = vector_search(
        query
    )

    print(
        "Vector Results:",
        len(vector_results)
    )

    # -----------------------------------------
    # RERANK
    # -----------------------------------------

    results = rerank(
        keyword_results,
        vector_results,
    )

    print(
        "\nFinal Results:",
        len(results)
    )

    print("\nTOP RESULTS")

    for result in results:

        print(
            f"\nScore={result['score']:.3f}"
        )

        print(
            f"Chunk ID={result['id']}"
        )

        print(
            f"Section={result['section']}"
        )

        print(
            result["content"][:300]
        )

        print("-" * 80)

    return results