from fastapi import APIRouter

from models.evaluation import EvaluateRequest

from services.evaluation_service import evaluate_answer

router = APIRouter()


@router.post("/evaluate")
def evaluate(req: EvaluateRequest):

    return evaluate_answer(req.question, req.answer)
