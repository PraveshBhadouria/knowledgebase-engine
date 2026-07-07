from database.connection import (
    get_connection,
)


def save_references(
    document_id,
    references,
    created_by="system",
):

    if not references:

        print(
            "\n⚠️ NO REFERENCES FOUND TO SAVE"
        )

        return

    print("\n📚 USING NEW REFERENCE STORE")

    conn = get_connection()

    cur = conn.cursor()

    insert_query = """
        INSERT INTO module_document_references (

            document_id,
            reference_text,
            reference_url,
            reference_order,
            page_start,
            page_end,
            is_active,
            created_at,
            created_by

        )
        VALUES (

            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            TRUE,
            NOW(),
            %s

        )

        RETURNING reference_id
    """

    total_saved = 0

    for reference in references:

        try:

            cur.execute(
                insert_query,
                (
                    document_id,
                    reference.get(
                        "reference_text"
                    ),
                    reference.get(
                        "reference_url"
                    ),
                    reference.get(
                        "reference_order"
                    ),
                    reference.get(
                        "page_start"
                    ),
                    reference.get(
                        "page_end"
                    ),
                    created_by,
                ),
            )

            reference_id = cur.fetchone()[0]

            conn.commit()

            print(
                f"✅ REFERENCE SAVED : "
                f"{reference_id}"
            )

            total_saved += 1

        except Exception as e:

            conn.rollback()

            print(
                "\n❌ FAILED TO SAVE REFERENCE"
            )

            print(
                f"ERROR : {str(e)}"
            )

            print(
                f"REFERENCE TEXT : "
                f"{reference.get('reference_text', '')[:200]}"
            )

    cur.close()
    conn.close()

    print(
        f"\n📚 TOTAL REFERENCES SAVED : "
        f"{total_saved}"
    )