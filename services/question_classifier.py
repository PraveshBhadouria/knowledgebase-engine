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

VALID_LABELS = {
    "GENERAL_DOMAIN",
    "PERSONAL_DOCUMENT",
    "IRRELEVANT",
}


# ==============================================================================
# QUESTION CLASSIFIER
# ==============================================================================

def classify_question(
    question: str,
    document_type: str = "document",
) -> str:
    """
    Classifies a question into exactly one of:

    GENERAL_DOMAIN
    PERSONAL_DOCUMENT
    IRRELEVANT
    """

    prompt = f"""
You are a routing classifier for a Retrieval-Augmented Generation (RAG) system.

The user has selected a document.

Document Type:
{document_type}

Your job is to classify the user's question into EXACTLY ONE of these labels.

============================================================
GENERAL_DOMAIN
============================================================

Choose GENERAL_DOMAIN ONLY if the question asks for a
general concept, definition, explanation, terminology,
framework, process, or principle that belongs to the SAME
domain as the selected document.

These questions MAY be answered using trusted public
information if the selected document does not contain
the answer.

Examples:

What is insurance?

What is health insurance?

What is a health policy?

What is hospitalization?

What is a deductible?

What is reimbursement?

What is a waiting period?

What is a claim?

What is a premium?

What is cancer insurance?

What is a legal contract?

What is an SOP?

What is machine learning?

What is a neural network?

What is hypertension?

============================================================
PERSONAL_DOCUMENT
============================================================

Choose PERSONAL_DOCUMENT if the answer should come ONLY
from the selected document.

Never search the web for these questions.

Examples:

What is my policy number?

What is my premium?

What is my sum insured?

When does my policy expire?

Who is insured?

What are my exclusions?

What is my deductible?

What is my claim amount?

Which chapter explains neural networks?

Which section discusses transformers?

Who signed this agreement?

What is the employee notice period?

============================================================
IRRELEVANT
============================================================

Choose IRRELEVANT if the question is NOT related to
the selected document or its domain.

Never use web search for these.

Examples:

Who is PM?

Who is the Prime Minister of India?

Who is Narendra Modi?

Who is Donald Trump?

Who is Virat Kohli?

Who won yesterday's cricket match?

What is the Moon?

What is Mars?

What is the capital of France?

Tell me a joke.

Weather today.

Bitcoin price.

IPL score.

Latest news.

============================================================
IMPORTANT RULES
============================================================

1. GENERAL_DOMAIN is ONLY for concepts that belong to the
same subject as the selected document.

2. If the answer would normally come from
Google,
Wikipedia,
news,
current affairs,
politics,
sports,
history,
geography,
entertainment,
or general knowledge,

then classify it as IRRELEVANT.

3. If the question asks for information that should exist
inside the selected document, classify it as
PERSONAL_DOCUMENT.

4. If you are uncertain between GENERAL_DOMAIN and
IRRELEVANT, choose IRRELEVANT.

============================================================

User Question:

{question}

Return ONLY ONE label.

GENERAL_DOMAIN

PERSONAL_DOCUMENT

IRRELEVANT

Do not explain.
Do not return JSON.
Do not return markdown.
Return ONLY the label.
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

        label = response.choices[0].message.content.strip().upper()

        if label not in VALID_LABELS:
            print(f"Invalid classifier response: {label}")
            return "IRRELEVANT"

        print(f"Question classified as: {label}")

        return label

    except Exception as e:

        print(f"Question Classification Error: {e}")

        return "IRRELEVANT"