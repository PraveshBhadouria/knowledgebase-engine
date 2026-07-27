import os
from dotenv import load_dotenv
from openai import OpenAI

# ==============================================================================
# LOAD ENVIRONMENT
# ==============================================================================

load_dotenv()

MODEL_ID = "qwen.qwen3-coder-30b-a3b-instruct"

client = OpenAI(
    api_key=os.getenv("AWS_BEARER_TOKEN_BEDROCK"),
    base_url=os.getenv(
        "OPENAI_BASE_URL",
        "https://bedrock-mantle.ap-south-1.api.aws/v1",
    ),
)

NOT_FOUND_TOKEN = "NOT_FOUND"


# ==============================================================================
# GENERATE ANSWER
# ==============================================================================

def generate_answer(question, context):
    """
    Backward-compatible function.

    Returns only the answer string.
    """

    result = generate_answer_with_status(question, context)

    if result["answer_found"]:
        return result["answer"]

    return NOT_FOUND_TOKEN


# ==============================================================================
# GENERATE ANSWER WITH STATUS
# ==============================================================================

def generate_answer_with_status(question, context):
    """
    Generates an answer from the retrieved document context.

    Returns:
    {
        "answer_found": bool,
        "answer": str | None
    }
    """

    prompt = f"""
You are an AI assistant for a Retrieval-Augmented Generation (RAG) system.

Answer ONLY using the provided context.

Rules:

1. Use ONLY the provided context.

2. Do NOT use outside knowledge.

3. If the answer is clearly present in the context,
provide a concise and accurate answer.

4. If the answer is NOT present in the context,
reply with EXACTLY this text:

NOT_FOUND

Do not explain why.
Do not apologize.
Do not add punctuation.
Do not generate anything else.

Context:

{context}

Question:

{question}
"""

    print("\n" + "=" * 80)
    print("LLM REQUEST")
    print("=" * 80)
    print(f"Question      : {question}")
    print(f"Context Words : {len(context.split())}")
    print("=" * 80)

    try:

        response = client.chat.completions.create(
            model=MODEL_ID,
            temperature=0.2,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        answer = response.choices[0].message.content.strip()

        print("\n" + "=" * 80)
        print("LLM RESPONSE")
        print("=" * 80)
        print(answer)
        print("=" * 80)

        if answer == NOT_FOUND_TOKEN:

            return {
                "answer_found": False,
                "answer": None,
            }

        return {
            "answer_found": True,
            "answer": answer,
        }

    except Exception as e:

        print("\nLLM ERROR")
        print(e)

        return {
            "answer_found": False,
            "answer": None,
        }


# ==============================================================================
# SUMMARIZE WEB SEARCH RESULTS
# ==============================================================================

def summarize_web_results(question, search_results):
    """
    Generate a concise answer using web search results.

    The response must clearly state that the information
    comes from general online sources and not from the selected document.
    """

    context = ""

    for result in search_results:

        context += f"""
Title:
{result["title"]}

Content:
{result["content"]}

Source:
{result["url"]}

"""

    prompt = f"""
The selected document does not provide the requested information.

Using ONLY the web search results below, answer the user's question.

Rules:

- Clearly mention that the answer is NOT from the selected document.
- Mention that it comes from general information available online.
- Keep the answer concise.
- Keep the answer under 150 words.
- Do not invent facts.
- If the search results are insufficient, say so.

Search Results:

{context}

Question:

{question}
"""

    try:

        response = client.chat.completions.create(
            model=MODEL_ID,
            temperature=0.2,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return response.choices[0].message.content.strip()

    except Exception as e:

        print("\nWEB SUMMARY ERROR")
        print(e)

        return (
            "The selected document doesn't provide this information, "
            "and I couldn't retrieve a reliable general explanation at this time."
        )