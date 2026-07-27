from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File
from fastapi import Depends

import tempfile

from auth.dependencies import (
    get_current_user,
)

from services.ingestion_service import (
    ingest_policy,
)

router = APIRouter()


# ==========================================================
# POLICY UPLOAD
# ==========================================================

@router.post("/upload/policy")
async def upload_policy_pdf(
    file: UploadFile = File(...),
    current_user=Depends(get_current_user),
):

    print("\n" + "=" * 80)
    print("POLICY UPLOAD STARTED")
    print("=" * 80)

    print(f"USER ID   : {current_user['id']}")
    print(f"USER NAME : {current_user['full_name']}")
    print(f"EMAIL     : {current_user['email']}")
    print(f"FILENAME  : {file.filename}")

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf",
    ) as temp:

        temp.write(
            await file.read()
        )

        pdf_path = temp.name

    total_chunks = ingest_policy(
        pdf_path=pdf_path,
        filename=file.filename,
        user_id=current_user["id"],
    )

    print(f"TOTAL POLICY CHUNKS : {total_chunks}")

    print("POLICY UPLOAD COMPLETED")

    print("=" * 80)

    return {

        "status": "success",

        "pipeline": "policy",

        "user_id": current_user["id"],

        "filename": file.filename,

        "chunks": total_chunks,

    }