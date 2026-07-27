from fastapi import APIRouter, Depends

from auth.dependencies import (
    get_current_user,
)

from database.connection import (
    get_connection,
)

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get("/stats")
def dashboard_stats(
    current_user=Depends(get_current_user),
):

    print("\n" + "=" * 100)
    print("DASHBOARD STATS")
    print("=" * 100)

    print(f"USER ID : {current_user['id']}")

    conn = get_connection()

    cur = conn.cursor()

    try:

        cur.execute(
            """
            SELECT

                COUNT(*)                                                   AS total_documents,

                COUNT(*) FILTER (
                    WHERE status = 'READY'
                )                                                          AS ready_documents,

                COUNT(*) FILTER (
                    WHERE status = 'INDEXING'
                )                                                          AS indexing_documents,

                COUNT(*) FILTER (
                    WHERE status = 'FAILED'
                )                                                          AS failed_documents,

                COUNT(*) FILTER (
                    WHERE status = 'PARTIAL'
                )                                                          AS partial_documents

            FROM documents

            WHERE
                user_id = %s
                AND is_active = TRUE
            """,
            (
                current_user["id"],
            ),
        )

        row = cur.fetchone()

        response = {

            "total_documents": row[0],

            "ready": row[1],

            "indexing": row[2],

            "failed": row[3],

            "partial": row[4],

        }

        print("\nDashboard Statistics")

        for key, value in response.items():

            print(f"{key} : {value}")

        print("=" * 100)

        return response

    finally:

        cur.close()

        conn.close()