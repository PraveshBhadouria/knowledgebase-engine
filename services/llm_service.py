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

# ==============================================================================
# GENERATE ANSWER
# ==============================================================================

def generate_answer(question, context):
    """
    Generate an answer using the Qwen3 model hosted on AWS Bedrock.
    The model is instructed to answer strictly from the provided context.
    """

    prompt = f"""
You are an AI assistant for a Retrieval-Augmented Generation (RAG) system.

Answer ONLY using the provided context.

Rules:
- Do not use outside knowledge.
- If the answer is not present in the context, reply exactly:
  "I couldn't find the answer in the provided document."
- Keep the answer clear and concise.
- If the context contains the answer, provide it accurately.

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

        return answer

    except Exception as e:
        print("\nLLM ERROR")
        print(e)
        return "Sorry, an error occurred while generating the answer."