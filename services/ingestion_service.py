from ingestion.ingest_router import (
    ingest_pdf_auto,
)

from ingestion.text.text_ingest import (
    ingest_pdf_text,
)

from ingestion.vision.vision_ingest import (
    ingest_pdf_vision,
)


def ingest_auto(
    pdf_path,
    filename,
):

    print("\n" + "=" * 80)
    print("AUTO INGESTION")
    print("=" * 80)

    return ingest_pdf_auto(
        pdf_path,
        filename,
    )


def ingest_text(
    pdf_path,
    filename,
):

    print("\n" + "=" * 80)
    print("TEXT INGESTION")
    print("=" * 80)

    return ingest_pdf_text(
        pdf_path,
        filename,
    )


def ingest_vision(
    pdf_path,
    filename,
):

    print("\n" + "=" * 80)
    print("VISION INGESTION")
    print("=" * 80)

    return ingest_pdf_vision(
        pdf_path,
        filename,
    )