import time

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


def hybrid_search(
    query,
    document_id,
):

    total_start = time.perf_counter()

    print("\n")
    print("=" * 80)
    print("SEARCH REQUEST")
    print("=" * 80)

    print(f"Query       : {query}")
    print(f"Document ID : {document_id}")

    # ==========================================================
    # EXACT SEARCH
    # ==========================================================

    start = time.perf_counter()

    exact_results = exact_search(
        query,
        document_id,
    )

    exact_time = time.perf_counter() - start

    print(
        f"\n⏱ Exact Search Time : {exact_time:.4f} sec"
    )

    if exact_results:

        print(
            f"\nEXACT MATCH FOUND : {len(exact_results)}"
        )

        results = []

        for row in exact_results:

            results.append(
                {
                    "id": row[0],
                    "section": row[1],
                    "content": row[2],
                    "score": 999.0,
                }
            )

        total_time = time.perf_counter() - total_start

        print("\n" + "=" * 80)
        print("SEARCH PERFORMANCE")
        print("=" * 80)
        print(f"Total Search Time : {total_time:.4f} sec")
        print("=" * 80)

        return results

    # ==========================================================
    # QUERY KEYWORD EXTRACTION
    # ==========================================================

    start = time.perf_counter()

    query_keywords = extract_keywords(
        query
    )

    keyword_extract_time = (
        time.perf_counter() - start
    )

    print(
        f"\n⏱ Keyword Extraction Time : {keyword_extract_time:.4f} sec"
    )

    print("\nQUERY KEYWORDS")

    for keyword in query_keywords:

        print(f"- {keyword}")

    # ==========================================================
    # KEYWORD SEARCH
    # ==========================================================

    start = time.perf_counter()

    keyword_results = keyword_search(
        query_keywords,
        document_id,
    )

    keyword_search_time = (
        time.perf_counter() - start
    )

    print(
        f"\n⏱ Keyword Search Time : {keyword_search_time:.4f} sec"
    )

    print(
        "Keyword Results:",
        len(keyword_results),
    )

    # ==========================================================
    # VECTOR SEARCH
    # ==========================================================

    start = time.perf_counter()

    vector_results = vector_search(
        query,
        document_id,
    )

    vector_search_time = (
        time.perf_counter() - start
    )

    print(
        f"\n⏱ Vector Search Time : {vector_search_time:.4f} sec"
    )

    print(
        "Vector Results:",
        len(vector_results),
    )

    # ==========================================================
    # RERANK
    # ==========================================================

    start = time.perf_counter()

    results = rerank(
        keyword_results,
        vector_results,
    )

    rerank_time = (
        time.perf_counter() - start
    )

    print(
        f"\n⏱ Rerank Time : {rerank_time:.4f} sec"
    )

    print(
        "\nFinal Results:",
        len(results),
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

    total_time = time.perf_counter() - total_start

    print("\n")
    print("=" * 80)
    print("SEARCH PERFORMANCE")
    print("=" * 80)
    print(f"Exact Search        : {exact_time:.4f} sec")
    print(f"Keyword Extraction  : {keyword_extract_time:.4f} sec")
    print(f"Keyword Search      : {keyword_search_time:.4f} sec")
    print(f"Vector Search       : {vector_search_time:.4f} sec")
    print(f"Rerank              : {rerank_time:.4f} sec")
    print("-" * 80)
    print(f"TOTAL SEARCH TIME   : {total_time:.4f} sec")
    print("=" * 80)

    return results