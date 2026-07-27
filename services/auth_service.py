from database.connection import get_connection

from auth.password import (
    hash_password,
    verify_password,
)

from auth.jwt_handler import (
    create_access_token,
)


# ==========================================================
# CREATE USER
# ==========================================================

def signup_user(
    full_name: str,
    email: str,
    password: str,
):

    print("\n" + "=" * 100)
    print("USER SIGNUP")
    print("=" * 100)

    conn = get_connection()

    cur = conn.cursor()

    try:

        # --------------------------------------------------
        # CHECK EMAIL
        # --------------------------------------------------

        print(f"CHECKING EMAIL : {email}")

        cur.execute(
            """
            SELECT id
            FROM users
            WHERE email = %s
            """,
            (
                email,
            ),
        )

        existing = cur.fetchone()

        if existing:

            print("EMAIL ALREADY EXISTS")

            raise Exception(
                "Email already registered."
            )

        # --------------------------------------------------
        # HASH PASSWORD
        # --------------------------------------------------

        print("HASHING PASSWORD")

        password_hash = hash_password(
            password
        )

        # --------------------------------------------------
        # INSERT USER
        # --------------------------------------------------

        print("INSERTING USER")

        cur.execute(
            """
            INSERT INTO users
            (
                full_name,
                email,
                password_hash
            )
            VALUES
            (
                %s,
                %s,
                %s
            )
            RETURNING id
            """,
            (
                full_name,
                email,
                password_hash,
            ),
        )

        user_id = cur.fetchone()[0]

        conn.commit()

        print(f"USER CREATED : {user_id}")

        return {

            "id": user_id,

            "full_name": full_name,

            "email": email,

        }

    finally:

        cur.close()

        conn.close()


# ==========================================================
# LOGIN USER
# ==========================================================

def login_user(
    email: str,
    password: str,
):

    print("\n" + "=" * 100)
    print("USER LOGIN")
    print("=" * 100)

    conn = get_connection()

    cur = conn.cursor()

    try:

        # --------------------------------------------------
        # GET USER
        # --------------------------------------------------

        print(f"SEARCHING USER : {email}")

        cur.execute(
            """
            SELECT
                id,
                full_name,
                email,
                password_hash
            FROM users
            WHERE email = %s
            """,
            (
                email,
            ),
        )

        row = cur.fetchone()

        if row is None:

            raise Exception(
                "Invalid email or password."
            )

        user_id = row[0]

        full_name = row[1]

        email = row[2]

        password_hash = row[3]

        # --------------------------------------------------
        # VERIFY PASSWORD
        # --------------------------------------------------

        if not verify_password(
            password,
            password_hash,
        ):

            raise Exception(
                "Invalid email or password."
            )

        # --------------------------------------------------
        # CREATE JWT
        # --------------------------------------------------

        token = create_access_token(
            user_id=user_id,
            email=email,
        )

        print("LOGIN SUCCESSFUL")

        return {

            "access_token": token,

            "token_type": "bearer",

            "user_id": user_id,

            "full_name": full_name,

            "email": email,

        }

    finally:

        cur.close()

        conn.close()