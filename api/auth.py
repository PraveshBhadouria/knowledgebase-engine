from fastapi import APIRouter, HTTPException

from models.auth import (
    SignupRequest,
    LoginRequest,
    LoginResponse,
)

from services.auth_service import (
    signup_user,
    login_user,
)

router = APIRouter(
    prefix="",
    tags=["Authentication"],
)


# ==========================================================
# SIGNUP
# ==========================================================

@router.post(
    "/signup",
)
def signup(
    request: SignupRequest,
):

    try:

        user = signup_user(
            full_name=request.full_name,
            email=request.email,
            password=request.password,
        )

        return {

            "status": "success",

            "message": "User created successfully.",

            "user": user,

        }

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


# ==========================================================
# LOGIN
# ==========================================================

@router.post(
    "/login",
    response_model=LoginResponse,
)
def login(
    request: LoginRequest,
):

    try:

        return login_user(
            email=request.email,
            password=request.password,
        )

    except Exception as e:

        raise HTTPException(
            status_code=401,
            detail=str(e),
        )