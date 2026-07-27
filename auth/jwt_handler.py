from datetime import datetime, timedelta

from jose import jwt
from jose.exceptions import JWTError

# ==========================================================
# JWT CONFIGURATION
# ==========================================================

SECRET_KEY = "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET_KEY"

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 Hours


# ==========================================================
# CREATE ACCESS TOKEN
# ==========================================================

def create_access_token(
    user_id: int,
    email: str,
):
    """
    Generate JWT token.
    """

    print("\n" + "=" * 80)
    print("CREATING ACCESS TOKEN")
    print("=" * 80)

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expire,
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )

    print(f"USER ID : {user_id}")
    print(f"EMAIL   : {email}")
    print(f"EXPIRES : {expire}")

    print("TOKEN CREATED")

    print("=" * 80)

    return token


# ==========================================================
# VERIFY TOKEN
# ==========================================================

def verify_access_token(
    token: str,
):
    """
    Verify JWT token.

    Returns payload if valid,
    otherwise None.
    """

    print("\n" + "=" * 80)
    print("VERIFYING ACCESS TOKEN")
    print("=" * 80)

    try:

        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        print("TOKEN VERIFIED")

        print(f"USER ID : {payload.get('sub')}")
        print(f"EMAIL   : {payload.get('email')}")

        print("=" * 80)

        return payload

    except JWTError as e:

        print("TOKEN VERIFICATION FAILED")

        print(e)

        print("=" * 80)

        return None