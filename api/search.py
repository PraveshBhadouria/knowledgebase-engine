from fastapi import APIRouter

from models.search import SearchRequest
from retrieval.search.hybrid_search import hybrid_search

router = APIRouter()


@router.post("/search")
def search(req: SearchRequest):

    return hybrid_search(req.query)
