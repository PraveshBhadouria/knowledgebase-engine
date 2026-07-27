from fastapi import Depends
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer

from database.connection import get_connection

from auth.jwt_handler import (
    verify_access_token,
)

# ==========================================================
# HTTP BEARER
# ==========================================================

security = HTTPBearer()

# ==========================================================
# GET CURRENT USER
# ==========================================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        security
    ),
):

    print("\n" + "=" * 100)
    print("AUTHENTICATING USER")
    print("=" * 100)

    token = credentials.credentials

    payload = verify_access_token(
        token
    )

    if payload is None:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token.",
        )

    user_id = int(
        payload["sub"]
    )

    print(f"USER ID : {user_id}")

    conn = get_connection()

    cur = conn.cursor()

    try:

        cur.execute(
            """
            SELECT
                id,
                full_name,
                email,
                is_active
            FROM users
            WHERE id = %s
            """,
            (
                user_id,
            ),
        )

        row = cur.fetchone()

        if row is None:

            raise HTTPException(
                status_code=401,
                detail="User not found.",
            )

        if not row[3]:

            raise HTTPException(
                status_code=401,
                detail="User is inactive.",
            )

        user = {

            "id": row[0],

            "full_name": row[1],

            "email": row[2],

        }

        print("USER AUTHENTICATED")

        print(user)

        print("=" * 100)

        return user

    finally:

        cur.close()

        conn.close()