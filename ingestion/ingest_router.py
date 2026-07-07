from ingestion.shared.pdf_detector import (
    is_text_pdf,
)

from ingestion.text.text_ingest import (
    ingest_pdf_text,
)

from ingestion.vision.vision_ingest import (
    ingest_pdf_vision,
)


def ingest_pdf_auto(
    pdf_path,
    filename,
):

    if is_text_pdf(pdf_path):

        print(
            "\nTEXT PDF DETECTED"
        )

        return ingest_pdf_text(
            pdf_path,
            filename,
        )

    print(
        "\nIMAGE PDF DETECTED"
    )

    return ingest_pdf_vision(
        pdf_path,
        filename,
    )