from fastapi import (
    FastAPI,
    UploadFile,
    File,
    Depends,
    HTTPException,
)
from fastapi.middleware.cors import CORSMiddleware
import tempfile

from models.search import SearchRequest
from models.evaluation import EvaluateRequest

from retrieval.search.hybrid_search import hybrid_search
from retrieval.context_builder import get_context

from services.ingestion_service import (
    ingest_auto,
    ingest_text,
    ingest_vision,
)

from services.answer_router import route_answer
from services.evaluation_service import evaluate_answer
from services.keyword_service import generate_keywords

from database.connection import get_connection
from api.dashboard import (
    router as dashboard_router,
)


from auth.dependencies import (
    get_current_user,
)

# ==========================================================
# AUTH ROUTER
# ==========================================================

from api.auth import (
    router as auth_router,
)

# ==========================================================
# POLICY ROUTER
# ==========================================================

from api.policy_upload import (
    router as policy_router,
)

from api.progress import router as progress_router

# ==========================================================
# FASTAPI APP
# ==========================================================

app = FastAPI(
    title="Knowledge Base API",
    version="1.0.0",
)

# ==========================================================
# CORS
# ==========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================================
# REGISTER ROUTERS
# ==========================================================

app.include_router(auth_router)
app.include_router(policy_router)
app.include_router(dashboard_router)
app.include_router(progress_router)

# ==========================================================
# ROOT
# ==========================================================

@app.get("/")
def root():

    return {
        "message": "Knowledge Base API Running"
    }


# ==========================================================
# SEARCH
# ==========================================================

@app.get("/search")
def search(query: str):

    return hybrid_search(query)


# ==========================================================
# AUTO PIPELINE
# ==========================================================

@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...)
):

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf",
    ) as temp:

        print("\n" + "=" * 80)
        print("UPLOAD STARTED")
        print("Filename:", file.filename)

        temp.write(
            await file.read()
        )

        pdf_path = temp.name

        print(
            "Temp Path:",
            pdf_path,
        )

        total_chunks = ingest_auto(
            pdf_path,
            file.filename,
        )

    print(
        "TOTAL CHUNKS STORED:",
        total_chunks,
    )

    print("UPLOAD COMPLETED")
    print("=" * 80)

    return {
        "message": "PDF processed successfully",
        "filename": file.filename,
        "chunks": total_chunks,
    }


# ==========================================================
# CHAT
# ==========================================================

@app.post("/chat")
def chat(
    req: SearchRequest,
    current_user=Depends(get_current_user),
):

    print("\n" + "=" * 100)
    print("CHAT REQUEST")
    print("=" * 100)

    print(f"USER ID     : {current_user['id']}")
    print(f"DOCUMENT ID : {req.document_id}")
    print(f"QUESTION    : {req.query}")

    conn = get_connection()
    cur = conn.cursor()

    try:

        # ==================================================
        # VERIFY DOCUMENT OWNERSHIP
        # ==================================================

        cur.execute(
            """
            SELECT
                id,
                document_name,
                document_type,
                status
            FROM documents
            WHERE
                id = %s
                AND user_id = %s
                AND is_active = TRUE
            """,
            (
                req.document_id,
                current_user["id"],
            ),
        )

        document = cur.fetchone()

        if document is None:

            print("\nDOCUMENT ACCESS DENIED")

            raise HTTPException(
                status_code=403,
                detail="You do not have access to this document.",
            )

        if document[3] != "READY":

            raise HTTPException(
                status_code=400,
                detail=f"Document status is '{document[3]}'. It is not ready for chat.",
            )

        print(f"DOCUMENT VERIFIED : {document[1]}")

        # ==================================================
        # BUILD CONTEXT
        # ==================================================

        context = get_context(
            req.query,
            req.document_id,
        )

        # ==================================================
        # ROUTE ANSWER
        # ==================================================

        try:

            result = route_answer(
                question=req.query,
                context=context,
                document_type=document[2],
            )   

        except Exception as e:

            print("\n" + "=" * 100)
            print("ROUTE ANSWER ERROR")
            print("=" * 100)
            print(e)

            raise HTTPException(
                status_code=500,
                detail="An error occurred while generating the answer.",
            )

        return {
            "document_id": req.document_id,
            "document_name": document[1],
            "document_type": document[2],
            "answer": result["answer"],
            "source": result["source"],
            "classification": result["classification"],
            "used_web_search": result["used_web_search"],
        }

    finally:

        cur.close()
        conn.close()
# ==========================================================
# EVALUATION
# ==========================================================

@app.post("/evaluate")
def evaluate(
    req: EvaluateRequest,
):

    result = evaluate_answer(
        req.question,
        req.answer,
    )

    return {
        "result": result
    }


# ==========================================================
# BOOK TEXT PIPELINE
# ==========================================================

@app.post("/upload/text")
async def upload_text_pdf(
    file: UploadFile = File(...)
):

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf",
    ) as temp:

        temp.write(
            await file.read()
        )

        pdf_path = temp.name

    total_chunks = ingest_text(
        pdf_path,
        file.filename,
    )

    return {
        "pipeline": "text",
        "filename": file.filename,
        "chunks": total_chunks,
    }


# ==========================================================
# BOOK VISION PIPELINE
# ==========================================================

@app.post("/upload/vision")
async def upload_vision_pdf(
    file: UploadFile = File(...)
):

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf",
    ) as temp:

        temp.write(
            await file.read()
        )

        pdf_path = temp.name

    total_chunks = ingest_vision(
        pdf_path,
        file.filename,
    )

    return {
        "pipeline": "vision",
        "filename": file.filename,
        "chunks": total_chunks,
    }


# ==========================================================
# DOCUMENTS
# ==========================================================

@app.get("/documents")
def get_documents(
    current_user=Depends(get_current_user),
):

    print("\n" + "=" * 100)
    print("FETCH USER DOCUMENTS")
    print("=" * 100)

    print(f"USER ID : {current_user['id']}")

    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            id,
            document_name,
            document_type,
            status,
            created_at
        FROM documents
        WHERE
            is_active = TRUE
            AND user_id = %s
        ORDER BY created_at DESC
        """,
        (
            current_user["id"],
        ),
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    print(f"TOTAL DOCUMENTS : {len(rows)}")

    print("=" * 100)

    return [
        {
            "id": row[0],
            "document_name": row[1],
            "document_type": row[2],
            "status": row[3],
            "created_at": row[4],
        }
        for row in rows
    ]

# ==========================================================
# KEYWORD GENERATION
# ==========================================================

@app.post("/keywords/generate")
def keyword_generation(
    document_ids: list[int],
):

    return generate_keywords(
        document_ids,
    )