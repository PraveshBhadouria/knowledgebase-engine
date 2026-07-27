import os
import json
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
# GENERIC WORDS TO IGNORE
# ==============================================================================

GENERIC_WORDS = {
    "business",
    "company",
    "companies",
    "organization",
    "organizations",
    "management",
    "manager",
    "system",
    "systems",
    "process",
    "processes",
    "activity",
    "activities",
    "people",
    "person",
    "department",
    "document",
    "documents",
    "information",
    "content",
    "chapter",
    "chapters",
    "section",
    "sections",
    "topic",
    "topics",
    "overview",
    "summary",
    "introduction",
    "material",
    "materials",
    "book",
    "books",
    "course",
    "courses",
    "student",
    "students",
    "page",
    "pages",
}


# ==============================================================================
# KEYWORD EXTRACTION
# ==============================================================================

def extract_keywords(content):

    prompt = f"""
You are generating search keywords for an enterprise Retrieval-Augmented Generation (RAG) system.

The document may be:

- Textbook
- Insurance Policy
- Legal Contract
- SOP
- Technical Manual
- Research Paper
- Academic Notes
- HR Policy
- Financial Report
- Medical Document
- Government Document
- Compliance Document

Extract EXACTLY 40 unique keywords or key phrases.

Return ONLY a valid JSON array.

Example:

[
  "research methodology",
  "qualitative research",
  "hypothesis testing"
]

Rules:

- Return ONLY JSON.
- No markdown.
- No explanations.
- No numbering.
- Exactly 40 keywords.
- Every keyword must improve search accuracy.
- Every keyword must represent a unique concept.

Prioritize:

- Core concepts
- Technical terminology
- Domain terminology
- Frameworks
- Models
- Methodologies
- Processes
- Standards
- Regulations
- Policies
- Benefits
- Coverage
- Exclusions
- Conditions
- Important noun phrases
- Named entities
- Acronyms
- Abbreviations
- Industry terminology
- Searchable phrases

Avoid:

- Generic words.
- Duplicate keywords.
- Near-duplicate phrases.
- Repeating the same concept with different wording.
- Single generic words.

Prefer keywords that users would naturally search for.

Text:

{content}
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

        result = response.choices[0].message.content.strip()

        print("\nRAW MODEL OUTPUT:")
        print(result)

        start = result.find("[")
        end = result.rfind("]") + 1

        if start == -1 or end == 0:
            raise ValueError("No valid JSON array found.")

        keywords = json.loads(result[start:end])

        cleaned = []
        seen = set()

        for keyword in keywords:

            if not isinstance(keyword, str):
                continue

            keyword = keyword.strip()

            if not keyword:
                continue

            keyword = " ".join(keyword.split())

            lower = keyword.lower()

            if lower in GENERIC_WORDS:
                continue

            if lower in seen:
                continue

            if len(lower) < 3:
                continue

            seen.add(lower)
            cleaned.append(keyword)

        print("\n" + "=" * 80)
        print("FINAL KEYWORDS")
        print("=" * 80)

        for index, keyword in enumerate(cleaned, start=1):
            print(f"{index:02d}. {keyword}")

        print("=" * 80)
        print(f"TOTAL UNIQUE KEYWORDS : {len(cleaned)}")
        print("=" * 80)

        return cleaned[:40]

    except Exception as e:

        print("\nKEYWORD EXTRACTION FAILED")
        print(e)

        return []