def build_metadata(
    chunk,
    document_id,
):

    return {
        "document_id": document_id,
        "node_id": chunk.get(
            "node_id",
            0,
        ),
        "chapter": chunk.get(
            "chapter",
            "",
        ),
        "section": chunk.get(
            "section",
            "",
        ),
        "subsection": chunk.get(
            "subsection",
            "",
        ),
        "subsubsection": chunk.get(
            "subsubsection",
            "",
        ),
    }