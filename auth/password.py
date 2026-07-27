from passlib.context import CryptContext

# ==========================================================
# PASSWORD HASHING CONFIGURATION
# ==========================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


# ==========================================================
# HASH PASSWORD
# ==========================================================

def hash_password(password: str) -> str:
    """
    Hash a plain text password.
    """
    print(f"PASSWORD TYPE   : {type(password)}")
    print(f"PASSWORD LENGTH : {len(password)}")
    print(f"PASSWORD VALUE  : {password}")
    print("\n" + "=" * 80)
    print("HASHING PASSWORD")
    print("=" * 80)
    print(f"PASSWORD VALUE  : {password}")

    hashed = pwd_context.hash(password)

    print("PASSWORD HASH GENERATED")
    print("=" * 80)

    return hashed


# ==========================================================
# VERIFY PASSWORD
# ==========================================================

def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Verify a plain password against the stored hash.
    """
    print(f"LOGIN PASSWORD LENGTH : {len(plain_password)}")
    print(f"HASH LENGTH           : {len(hashed_password)}")
    print("\n" + "=" * 80)
    print("VERIFYING PASSWORD")
    print("=" * 80)

    result = pwd_context.verify(
        plain_password,
        hashed_password,
    )

    print(f"PASSWORD MATCH : {result}")

    print("=" * 80)

    return result