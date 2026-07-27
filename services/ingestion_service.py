from ingestion.ingest_router import (
    ingest_pdf_auto,
)

from ingestion.text.text_ingest import (
    ingest_pdf_text,
)

from ingestion.vision.vision_ingest import (
    ingest_pdf_vision,
)

from ingestion.policy.policy_ingest import (
    ingest_policy_pdf,
)


# ==========================================================
# AUTO INGESTION
# ==========================================================

def ingest_auto(
    pdf_path,
    filename,
    user_id=None,
):

    print("\n" + "=" * 80)
    print("AUTO INGESTION")
    print("=" * 80)

    print(f"USER ID : {user_id}")

    return ingest_pdf_auto(
        pdf_path,
        filename,
        user_id=user_id,
    )


# ==========================================================
# TEXT INGESTION
# ==========================================================

def ingest_text(
    pdf_path,
    filename,
    user_id=None,
):

    print("\n" + "=" * 80)
    print("TEXT INGESTION")
    print("=" * 80)

    print(f"USER ID : {user_id}")

    return ingest_pdf_text(
        pdf_path,
        filename,
        user_id=user_id,
    )


# ==========================================================
# VISION INGESTION
# ==========================================================

def ingest_vision(
    pdf_path,
    filename,
    user_id=None,
):

    print("\n" + "=" * 80)
    print("VISION INGESTION")
    print("=" * 80)

    print(f"USER ID : {user_id}")

    return ingest_pdf_vision(
        pdf_path,
        filename,
        user_id=user_id,
    )


# ==========================================================
# POLICY INGESTION
# ==========================================================

def ingest_policy(
    pdf_path,
    filename,
    user_id=None,
):

    print("\n" + "=" * 80)
    print("POLICY INGESTION")
    print("=" * 80)

    print(f"USER ID : {user_id}")

    return ingest_policy_pdf(
        pdf_path,
        filename,
        user_id=user_id,
    )