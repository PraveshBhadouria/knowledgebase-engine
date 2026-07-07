from fastapi import FastAPI, UploadFile, File
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
from services.llm_service import generate_answer
from services.evaluation_service import evaluate_answer
from services.keyword_service import (
    generate_keywords,
)
from database.connection import get_connection

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():

    return {
        "message": "Knowledge Base API Running"
    }


@app.get("/search")
def search(query: str):

    return hybrid_search(query)


@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...)
):

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf"
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
            pdf_path
        )

        total_chunks = ingest_auto(
            pdf_path,
            file.filename,
        )

    print(
        "TOTAL CHUNKS STORED:",
        total_chunks
    )

    print("UPLOAD COMPLETED")
    print("=" * 80)

    return {
        "message": "PDF processed successfully",
        "filename": file.filename,
        "chunks": total_chunks,
    }


@app.post("/chat")
def chat(
    req: SearchRequest
):

    context = get_context(
        req.query
    )

    answer = generate_answer(
        req.query,
        context,
    )

    return {
        "answer": answer
    }


@app.post("/evaluate")
def evaluate(
    req: EvaluateRequest
):

    result = evaluate_answer(
        req.question,
        req.answer,
    )

    return {
        "result": result
    }




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


@app.get("/documents")
def get_documents():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            id,
            document_name
        FROM documents
        WHERE is_active = TRUE
        ORDER BY id DESC
        """
    )

    rows = cur.fetchall()

    cur.close()
    conn.close()

    return [
        {
            "id": row[0],
            "name": row[1],
        }
        for row in rows
    ]

@app.post("/keywords/generate")
def keyword_generation(
    document_ids: list[int]
):

    return generate_keywords(
        document_ids
    )