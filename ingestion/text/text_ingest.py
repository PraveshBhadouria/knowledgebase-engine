from ingestion.shared.reference_extractor import (
    extract_references,
)

from ingestion.shared.reference_store import (
    save_references,
)

from ingestion.text.extractors.extractor_router import (
    extract_text,
)

from ingestion.text.hierarchy.layout_extractor import (
    extract_layout,
)

from ingestion.text.hierarchy.hierarchy_builder import (
    build_hierarchy,
)

from ingestion.text.text_normalizer import (
    normalize_text,
)

from ingestion.shared.rule_chunker import (
    create_chunks,
)

from ingestion.shared.metadata_builder import (
    build_metadata,
)

from ingestion.shared.store import (
    save_chunk,
)

from ingestion.shared.document_store import (
    create_document,
    update_document_status,
)


def ingest_pdf_text(
    pdf_path,
    filename,
    user_id=None,
):

    print("\n" + "🚀" * 40)
    print("STARTING TEXT INGESTION PIPELINE")
    print("🚀" * 40)

    # ==========================================================
    # DOCUMENT CREATION
    # ==========================================================

    print("\n" + "📄" * 40)
    print("STEP 1 : CREATING DOCUMENT ENTRY")
    print("📄" * 40)

    document_id = create_document(
        filename=filename,
        pdf_path=pdf_path,
        document_type="TEXT",
        user_id=user_id,
    )

    print(f"✅ DOCUMENT CREATED : {document_id}")

    # ==========================================================
    # LAYOUT EXTRACTION
    # ==========================================================

    print("\n" + "🔍" * 40)
    print("STEP 2 : LAYOUT EXTRACTION STARTED")
    print("🔍" * 40)

    layout_pages = extract_layout(
        pdf_path
    )

    print("\n" + "✅" * 40)
    print("LAYOUT EXTRACTION COMPLETED")
    print(
        f"TOTAL LAYOUT PAGES : "
        f"{len(layout_pages)}"
    )
    print("✅" * 40)

    # ==========================================================
    # HIERARCHY BUILDING
    # ==========================================================

    print("\n" + "🌳" * 40)
    print("STEP 3 : BUILDING DOCUMENT HIERARCHY")
    print("🌳" * 40)

    structured_pages, reference_pages = (
        build_hierarchy(layout_pages)
    )

    print("\n" + "📚" * 20)
    print("REFERENCE EXTRACTION")
    print("📚" * 20)

    print(
        f"TOTAL REFERENCE PAGES : "
        f"{len(reference_pages)}"
    )

    print("\n" + "✅" * 40)
    print("HIERARCHY BUILDING COMPLETED")
    print(
        f"STRUCTURED PAGES : "
        f"{len(structured_pages)}"
    )
    print("✅" * 40)

    # ==========================================================
    # REFERENCE EXTRACTION & SAVE
    # ==========================================================

    print("\n" + "📖" * 40)
    print("STEP 4 : EXTRACTING REFERENCES")
    print("📖" * 40)

    references = extract_references(
        reference_pages
    )

    print(
        f"TOTAL REFERENCES FOUND : "
        f"{len(references)}"
    )

    if references:

        save_references(
            document_id=document_id,
            references=references,
            created_by="system",
        )

        print(
            f"TOTAL REFERENCES SAVED : "
            f"{len(references)}"
        )

    else:

        print(
            "⚠️ NO REFERENCES FOUND"
        )

    # ==========================================================
    # TEXT NORMALIZATION
    # ==========================================================

    print("\n" + "🧹" * 40)
    print("STEP 5 : NORMALIZING TEXT")
    print("🧹" * 40)

    units = normalize_text(
        structured_pages
    )

    print("\n" + "✅" * 40)
    print("TEXT NORMALIZATION COMPLETED")
    print(
        f"TOTAL UNITS : "
        f"{len(units)}"
    )
    print("✅" * 40)

    # ==========================================================
    # CHUNK CREATION
    # ==========================================================

    print("\n" + "✂️" * 40)
    print("STEP 6 : CREATING CHUNKS")
    print("✂️" * 40)

    chunks = create_chunks(
        units
    )

    print("\n" + "✅" * 40)
    print("CHUNK CREATION COMPLETED")
    print(
        f"TOTAL CHUNKS : "
        f"{len(chunks)}"
    )
    print("✅" * 40)

    # ==========================================================
    # CHUNK PREVIEW
    # ==========================================================

    print("\n" + "👀" * 40)
    print("STEP 7 : CHUNK PREVIEW")
    print("👀" * 40)

    for i, chunk in enumerate(
        chunks,
        start=1,
    ):

        print("\n" + "=" * 120)
        print(f"CHUNK #{i}")

        print(
            f"NODE ID      : "
            f"{chunk['node_id']}"
        )

        print(
            f"PAGE START   : "
            f"{chunk.get('page_start')}"
        )

        print(
            f"PAGE END     : "
            f"{chunk.get('page_end')}"
        )

        print(
            f"SECTION      : "
            f"{chunk.get('section')}"
        )

        print(
            f"SUBSECTION   : "
            f"{chunk.get('subsection')}"
        )

        print(
            f"SUBSUBSECTION: "
            f"{chunk.get('subsubsection')}"
        )

        print("-" * 120)

        print(
            chunk["content"][:1000]
        )

        print("=" * 120)

    # ==========================================================
    # DATABASE SAVE
    # ==========================================================

    print("\n" + "💾" * 40)
    print("STEP 8 : SAVING CHUNKS TO DATABASE")
    print("💾" * 40)

    total_chunks = 0

    for index, chunk in enumerate(
        chunks,
        start=1,
    ):

        print(
            f"\n💾 SAVING CHUNK "
            f"{index}/{len(chunks)}"
        )

        metadata = build_metadata(
            chunk,
            document_id,
        )

        save_chunk(
            chunk,
            filename,
            metadata,
        )

        total_chunks += 1

    print("\n" + "✅" * 40)
    print("DATABASE SAVE COMPLETED")
    print(
        f"TOTAL CHUNKS SAVED : "
        f"{total_chunks}"
    )
    print("✅" * 40)

    # ==========================================================
    # DOCUMENT STATUS UPDATE
    # ==========================================================

    print("\n" + "🔄" * 40)
    print("STEP 9 : UPDATING DOCUMENT STATUS")
    print("🔄" * 40)

    update_document_status(
        document_id,
        "READY",
    )

    print("\n" + "🎉" * 40)
    print(
        "TEXT INGESTION COMPLETED "
        "SUCCESSFULLY"
    )

    print(
        f"DOCUMENT ID : "
        f"{document_id}"
    )

    print(
        f"TOTAL CHUNKS SAVED : "
        f"{total_chunks}"
    )

    print(
        f"TOTAL REFERENCES SAVED : "
        f"{len(references)}"
    )

    print("🎉" * 40)

    return total_chunks