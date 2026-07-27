from services.llm_service import (
    generate_answer_with_status,
    summarize_web_results,
)

from services.question_classifier import (
    classify_question,
)

from services.web_search_service import (
    search_web,
)

# ==============================================================================
# CONSTANT MESSAGES
# ==============================================================================

DOCUMENT_NOT_FOUND_MESSAGE = (
    "I couldn't find this information in the selected document. "
    "It seems this detail isn't available in the document. "
    "If you think it should be included, please make sure you've selected the correct document. "
    "Otherwise, feel free to ask another question about it."
)

IRRELEVANT_MESSAGE = (
    "This question isn't related to the selected document. "
    "I can help answer questions about the document itself or explain general concepts related to its subject area."
)


# ==============================================================================
# ANSWER ROUTER
# ==============================================================================

def route_answer(
    question: str,
    context: str,
    document_type: str = "document",
):
    """
    Routes a question to one of the following:

    1. Document Answer
    2. Web Search
    3. Missing Document Information
    4. Irrelevant Question
    """

    print("\n" + "=" * 100)
    print("ANSWER ROUTER")
    print("=" * 100)

    print(f"Question      : {question}")
    print(f"Document Type : {document_type}")

    # ==========================================================
    # NO CONTEXT
    # ==========================================================

    if not context.strip():

        print("No context retrieved.")

        return {
            "answer": DOCUMENT_NOT_FOUND_MESSAGE,
            "source": "document",
            "classification": "NO_CONTEXT",
            "used_web_search": False,
        }

    # ==========================================================
    # TRY DOCUMENT
    # ==========================================================

    result = generate_answer_with_status(
        question,
        context,
    )

    if result["answer_found"]:

        print("Answer found in document.")

        return {
            "answer": result["answer"],
            "source": "document",
            "classification": "DOCUMENT",
            "used_web_search": False,
        }

    print("Answer not found in document.")

    # ==========================================================
    # CLASSIFY QUESTION
    # ==========================================================

    label = classify_question(
        question,
        document_type,
    )

    print(f"Question Classification : {label}")

    # ==========================================================
    # GENERAL DOMAIN
    # ==========================================================

    if label == "GENERAL_DOMAIN":

        print("Searching the web...")

        search_results = search_web(question)

        if not search_results:

            print("No search results found.")

            return {
                "answer": DOCUMENT_NOT_FOUND_MESSAGE,
                "source": "none",
                "classification": label,
                "used_web_search": False,
            }

        answer = summarize_web_results(
            question,
            search_results,
        )

        return {
            "answer": answer,
            "source": "web",
            "classification": label,
            "used_web_search": True,
        }

    # ==========================================================
    # PERSONAL DOCUMENT
    # ==========================================================

    if label == "PERSONAL_DOCUMENT":

        return {
            "answer": DOCUMENT_NOT_FOUND_MESSAGE,
            "source": "document",
            "classification": label,
            "used_web_search": False,
        }

    # ==========================================================
    # IRRELEVANT
    # ==========================================================

    return {
        "answer": IRRELEVANT_MESSAGE,
        "source": "none",
        "classification": "IRRELEVANT",
        "used_web_search": False,
    }