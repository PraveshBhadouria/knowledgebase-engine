from ingestion.shared.pdf_detector import (
    is_text_pdf,
)

from ingestion.text.text_ingest import (
    ingest_pdf_text,
)

from ingestion.vision.vision_ingest import (
    ingest_pdf_vision,
)


# ==========================================================
# AUTO INGEST ROUTER
# ==========================================================

def ingest_pdf_auto(
    pdf_path,
    filename,
    user_id=None,
):

    print("\n" + "=" * 80)
    print("AUTO INGEST ROUTER")
    print("=" * 80)

    print(f"FILE    : {filename}")
    print(f"USER ID : {user_id}")

    # =====================================================
    # TEXT PDF
    # =====================================================

    if is_text_pdf(pdf_path):

        print("\nTEXT PDF DETECTED")

        return ingest_pdf_text(
            pdf_path,
            filename,
            user_id=user_id,
        )

    # =====================================================
    # IMAGE PDF
    # =====================================================

    print("\nIMAGE PDF DETECTED")

    return ingest_pdf_vision(
        pdf_path,
        filename,
        user_id=user_id,
    )