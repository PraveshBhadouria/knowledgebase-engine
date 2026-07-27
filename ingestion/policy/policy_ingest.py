from numpy.strings import index

from api import progress
from database.connection import get_connection

from ingestion.policy.extractors.extractor_router import (
    extract_pdf,
)

from ingestion.policy.cleaners.reading_order import (
    reconstruct_reading_order,
)

from ingestion.policy.cleaners.header_footer_cleaner import (
    remove_headers_and_footers,
)

from ingestion.policy.detectors.table_detector import (
    detect_tables,
)

from ingestion.policy.detectors.section_detector import (
    detect_sections,
)

from ingestion.policy.detectors.clause_detector import (
    detect_clauses,
)

from ingestion.policy.parsers.policy_parser import (
    parse_policy,
)

from ingestion.policy.parsers.clause_builder import (
    build_clauses,
)

from ingestion.policy.enrichers.metadata_enricher import (
    enrich_metadata,
)

from ingestion.policy.enrichers.fact_extractor import (
    extract_facts,
)

from ingestion.policy.chunking.semantic_chunker import (
    create_semantic_chunks,
)

from ingestion.policy.metadata.metadata_builder import (
    build_metadata,
)

from ingestion.policy.store.store import (
    save_chunk,
)

from ingestion.shared.document_store import (
    create_document,
    update_document_status,
)

from services.progress_service import update_upload

def stage(name):

    print("\n")
    print("🚀" * 50)
    print(name)
    print("🚀" * 50)


def ingest_policy_pdf(
    pdf_path,
    filename,
    user_id=None,
):

    print("\n" + "=" * 120)
    print("POLICY INGESTION PIPELINE STARTED")
    print("=" * 120)

    print(f"FILE NAME : {filename}")
    print(f"PDF PATH  : {pdf_path}")

    # =====================================================
    # CREATE DOCUMENT
    # =====================================================

    stage("STEP 1 : CREATE DOCUMENT")
    update_upload(5, "Creating document")

    document_id = create_document(
        filename=filename,
        pdf_path=pdf_path,
        document_type="POLICY",
        user_id=user_id,
    )

    print(f"DOCUMENT ID : {document_id}")

    total_saved = 0

    try:

        # =====================================================
        # EXTRACTION
        # =====================================================

        stage("STEP 2 : PDF EXTRACTION")

        pages = extract_pdf(pdf_path)
        update_upload(15, "Extracting PDF")

        print(f"TOTAL PAGES EXTRACTED : {len(pages)}")

        # =====================================================
        # READING ORDER
        # =====================================================

        stage("STEP 3 : READING ORDER")

        pages = reconstruct_reading_order(
            pages
        )
        update_upload(25, "Reconstructing reading order")

        print(f"PAGES AFTER READING ORDER : {len(pages)}")

        # =====================================================
        # HEADER FOOTER CLEANING
        # =====================================================

        stage("STEP 4 : HEADER FOOTER CLEANING")

        pages = remove_headers_and_footers(
            pages
        )
        update_upload(35, "Removing headers and footers")

        print(f"PAGES AFTER CLEANING : {len(pages)}")

        # =====================================================
        # TABLE DETECTION
        # =====================================================

        stage("STEP 5 : TABLE DETECTION")

        pages = detect_tables(
            pages
        )
        update_upload(45, "Detecting tables")

        # =====================================================
        # SECTION DETECTION
        # =====================================================

        stage("STEP 6 : SECTION DETECTION")

        pages = detect_sections(
            pages
        )
        update_upload(55, "Detecting sections")
        # =====================================================
        # CLAUSE DETECTION
        # =====================================================

        stage("STEP 7 : CLAUSE DETECTION")

        pages = detect_clauses(
            pages
        )
        update_upload(65, "Detecting clauses")

        # =====================================================
        # PARSER
        # =====================================================

        stage("STEP 8 : POLICY PARSER")

        units = parse_policy(
            pages
        )

        print(f"TOTAL UNITS : {len(units)}")

        # =====================================================
        # CLAUSE BUILDER
        # =====================================================

        stage("STEP 9 : CLAUSE BUILDER")

        clauses = build_clauses(
            units
        )
        update_upload(72, "Building clauses")

        print(f"TOTAL CLAUSES : {len(clauses)}")

        # =====================================================
        # METADATA
        # =====================================================

        stage("STEP 10 : METADATA ENRICHMENT")

        clauses = enrich_metadata(
            clauses
        )
        update_upload(78, "Enriching metadata")

        print(f"CLAUSES AFTER METADATA : {len(clauses)}")

        # =====================================================
        # FACT EXTRACTION
        # =====================================================

        stage("STEP 11 : FACT EXTRACTION")

        clauses = extract_facts(
            clauses
        )
        update_upload(83, "Extracting facts")

        print(f"CLAUSES AFTER FACTS : {len(clauses)}")

        # =====================================================
        # CHUNKING
        # =====================================================

        stage("STEP 12 : SEMANTIC CHUNKING")

        chunks = create_semantic_chunks(
            clauses
        )
        update_upload(90, "Creating semantic chunks")

        print(f"TOTAL CHUNKS CREATED : {len(chunks)}")

        # =====================================================
        # SAVE
        # =====================================================

        stage("STEP 13 : DATABASE STORAGE")

        for index, chunk in enumerate(
            chunks,
            start=1,
        ):
            progress = 90 + int((index / len(chunks)) * 8)

            update_upload(
                progress,
                f"Saving chunk {index}/{len(chunks)}",
            )

            print("\n" + "-" * 120)

            print(
                f"SAVING CHUNK {index}/{len(chunks)}"
            )

            print(
                f"Chunk ID   : {chunk.get('chunk_id')}"
            )

            print(
                f"Clause     : {chunk.get('clause_id')}"
            )

            print(
                f"Section    : {chunk.get('section')}"
            )

            metadata = build_metadata(
                chunk,
                document_id,
            )

            try:

                save_chunk(
                    chunk,
                    filename,
                    metadata,
                )

                total_saved += 1

                print("✅ SAVED SUCCESSFULLY")

            except Exception as e:

                print("❌ SAVE FAILED")

                print(e)

        # =====================================================
        # VERIFY DATABASE
        # =====================================================

        stage("STEP 14 : DATABASE VERIFICATION")

        conn = get_connection()

        cur = conn.cursor()

        cur.execute(
            """
            SELECT COUNT(*)
            FROM document_chunks
            WHERE document_id = %s
            """,
            (
                document_id,
            ),
        )

        db_chunks = cur.fetchone()[0]

        cur.close()

        conn.close()

        print(f"EXPECTED CHUNKS : {len(chunks)}")

        print(f"SAVED CHUNKS    : {total_saved}")

        print(f"DB CHUNKS       : {db_chunks}")

        if db_chunks != len(chunks):

            print("\n⚠ WARNING")

            print(
                "Generated chunks and database chunks do not match."
            )

        else:

            print("\n✅ DATABASE VERIFICATION PASSED")

        # =====================================================
        # DOCUMENT STATUS
        # =====================================================

        stage("STEP 15 : UPDATE DOCUMENT STATUS")

        if db_chunks == len(chunks):

            update_document_status(
                document_id,
                "READY",
            )
            update_upload(100, "Completed")

            final_status = "READY"

        else:

            update_document_status(
                document_id,
                "PARTIAL",
            )
            update_upload(100, "Completed")

            final_status = "PARTIAL"

        # =====================================================
        # FINAL SUMMARY
        # =====================================================

        print("\n" + "=" * 120)

        print("POLICY INGESTION SUMMARY")

        print("=" * 120)

        print(f"DOCUMENT ID      : {document_id}")
        print(f"FILE             : {filename}")
        print(f"PAGES            : {len(pages)}")
        print(f"UNITS            : {len(units)}")
        print(f"CLAUSES          : {len(clauses)}")
        print(f"CHUNKS CREATED   : {len(chunks)}")
        print(f"CHUNKS SAVED     : {total_saved}")
        print(f"CHUNKS IN DB     : {db_chunks}")
        print(f"FINAL STATUS     : {final_status}")

        print("=" * 120)

        print("POLICY INGESTION COMPLETED")

        print("=" * 120)

        return total_saved

    except Exception as e:

        update_document_status(
            document_id,
            "FAILED",
        )

        print("\n" + "=" * 120)
        print("POLICY INGESTION FAILED")
        print("=" * 120)

        print(f"DOCUMENT ID : {document_id}")
        print(f"FILE        : {filename}")
        print(f"ERROR TYPE  : {type(e).__name__}")
        print(f"ERROR       : {e}")

        print("=" * 120)
        update_upload(100, "Failed")

        raise