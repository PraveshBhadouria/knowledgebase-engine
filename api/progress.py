from fastapi import APIRouter

from services.progress_service import get_progress

router = APIRouter()

@router.get("/progress")
def progress():
    return get_progress()