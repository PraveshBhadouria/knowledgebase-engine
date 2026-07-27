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
    Generates an answer strictly from the retrieved document context.

    Returns:
    {
        "answer_found": bool,
        "answer": str | None
    }
    """

    prompt = f"""
You are an AI assistant for a Retrieval-Augmented Generation (RAG) system.

Your ONLY source of truth is the provided context.

==============================================================================
RULES
==============================================================================

1. Use ONLY the provided context.

2. Never use outside knowledge.

3. Never use common knowledge.

4. Never infer information that is not explicitly written in the context.

5. A word or phrase merely appearing in the context DOES NOT mean it has been
explained.

For example, if the context only contains terms like:

- Policy
- Policy Number
- Health Insurance Policy
- Premium
- Hospitalization
- Waiting Period
- Claim

but does NOT explicitly define or explain them,
you MUST return:

NOT_FOUND

6. Only answer if the context explicitly contains the information needed
to answer the user's question.

7. Do NOT complete missing information using your own knowledge.

8. Do NOT generate definitions from memory.

9. If answering requires even a small amount of outside knowledge,
return:

NOT_FOUND

10. Even if you personally know the answer, ignore it unless it is clearly
written in the context.

==============================================================================
HOW TO WRITE THE ANSWER
==============================================================================

When the answer is available in the context:

- Keep the response concise (preferably under 80 words).
- Answer the user's question directly.
- Write in a professional and natural tone.
- Rewrite the information instead of copying sentences from the document.
- Remove OCR artifacts and repeated text.
- Make the answer easy to scan.
- Use bullet points ONLY when there are multiple items.
- Group similar information together.
- Highlight important information using Markdown bold (**text**).
- Do NOT add unnecessary introductions or conclusions.

If the answer is a single value, format it like this:

**Policy Number:** **14593437**

**Sum Insured:** **$100,000**

**Waiting Period:** **30 days**

If the answer contains multiple benefits, features, exclusions, or conditions,
present them as concise bullet points.

Example:

**This policy covers:**

- **Hospitalization:** In-patient care, day care treatment
- **Medical Expenses:** Pre- and post-hospitalization expenses
- **Emergency Services:** Ambulance cover
- **Additional Benefits:** OPD expenses, annual health check-up

Never dump raw extracted text from the document.

==============================================================================
OUTPUT
==============================================================================

If the answer is explicitly present in the context:

Return ONLY the formatted answer.

If the answer is NOT explicitly present:

Return EXACTLY

NOT_FOUND

Do not explain.
Do not apologize.
Do not add punctuation.
Do not return JSON.
Do not return markdown code blocks.
Return ONLY the answer or NOT_FOUND.

==============================================================================
CONTEXT
==============================================================================

{context}

==============================================================================
QUESTION
==============================================================================

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
            temperature=0,
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
    Generates a concise answer using trusted web search results.
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
The selected document does not contain the requested information.

Your task is ONLY to generate the explanation using the search results.

Use ONLY the search results below.

Rules:

- Do NOT mention the selected document.
- Do NOT mention Google.
- Do NOT mention web search.
- Do NOT mention online sources.
- Do NOT add introductions.
- Do NOT add conclusions.
- Return ONLY the explanation.
- Keep it under 120 words.
- Be factual.
- Do not invent information.
- If the search results are insufficient, say:
  "I couldn't find enough reliable information to answer this question."

Search Results:

{context}

Question:

{question}
"""

    try:

        response = client.chat.completions.create(
            model=MODEL_ID,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        web_answer = response.choices[0].message.content.strip()

        return (
            "I couldn't find this information in the selected document. "
            "I searched trusted online sources and found the following information:\n\n"
            f"{web_answer}"
        )

    except Exception as e:

        print("\nWEB SUMMARY ERROR")
        print(e)

        return (
            "I couldn't find this information in the selected document. "
            "I also couldn't retrieve reliable information from trusted online sources at this time."
        )