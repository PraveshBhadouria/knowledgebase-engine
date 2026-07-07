def rerank(
    keyword_results,
    vector_results,
):

    merged = {}

    print("\n")
    print("=" * 80)
    print("RERANKING")
    print("=" * 80)

    # --------------------------------------------------
    # KEYWORD RESULTS
    # --------------------------------------------------

    for row in keyword_results:

        chunk_id = row[0]

        keyword_score = (
            float(row[3]) * 100
        )

        print("\nKEYWORD MATCH")

        print(
            f"Chunk ID: {chunk_id}"
        )

        print(
            f"Keyword Score: {keyword_score:.4f}"
        )

        merged[chunk_id] = {
            "id": row[0],
            "section": row[1],
            "content": row[2],
            "score": keyword_score,
        }

    # --------------------------------------------------
    # VECTOR RESULTS
    # --------------------------------------------------

    for row in vector_results:

        chunk_id = row[0]

        distance = float(row[3])

        vector_score = (
            1 - distance
        )

        print("\nVECTOR MATCH")

        print(
            f"Chunk ID: {chunk_id}"
        )

        print(
            f"Distance: {distance:.4f}"
        )

        print(
            f"Vector Score: {vector_score:.4f}"
        )

        if chunk_id in merged:

            merged[chunk_id][
                "score"
            ] += (
                vector_score * 5
            )

        else:

            merged[chunk_id] = {
                "id": row[0],
                "section": row[1],
                "content": row[2],
                "score": vector_score * 5,
            }

    # --------------------------------------------------
    # SORT
    # --------------------------------------------------

    results = sorted(
        merged.values(),
        key=lambda x: x["score"],
        reverse=True,
    )

    print("\n")
    print("=" * 80)
    print("FINAL RANKING")
    print("=" * 80)

    for result in results[:10]:

        print(
            f"\nChunk ID: {result['id']}"
        )

        print(
            f"Score: {result['score']:.4f}"
        )

        print(
            f"Section: {result['section']}"
        )

        print(
            result["content"][:200]
        )

    return results[:5]