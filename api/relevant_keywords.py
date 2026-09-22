from fastapi import APIRouter, Depends, HTTPException

from auth.dependencies import get_current_user

from models.relevant_keywords import (
    RelevantKeywordRequest,
)

from ingestion.shared.relevant_keyword_service import (
    generate_relevant_keywords,
)


router = APIRouter(
    prefix="/keywords",
    tags=["Keywords"],
)


# ==========================================================
# GENERATE RELEVANT KEYWORDS
# ==========================================================

@router.post("/relevant")
def generate_relevant_keywords_endpoint(
    request: RelevantKeywordRequest,
    current_user=Depends(get_current_user),
):

    try:

        result = generate_relevant_keywords(
            document_id=request.document_id,
            user_id=current_user["id"],
        )

        return result

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )