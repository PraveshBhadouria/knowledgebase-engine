import json
import os
import re
from typing import List

from openai import OpenAI

from database.connection import get_connection


# ==============================================================================
# LLM CONFIGURATION
# ==============================================================================

MODEL_ID = "qwen.qwen3-coder-30b-a3b-instruct"

BEDROCK_BASE_URL = "https://bedrock-mantle.ap-south-1.api.aws/v1"


# ==============================================================================
# LLM CLIENT
# ==============================================================================

client = OpenAI(
    base_url=BEDROCK_BASE_URL,
    api_key=os.getenv("AWS_BEARER_TOKEN_BEDROCK"),
)


# ==============================================================================
# FALLBACK SEARCH TERMS
# ==============================================================================


def extract_search_terms(text: str) -> List[str]:
    """
    Fallback keyword extraction.

    Used only when the LLM fails to return valid keywords.

    Logic:
        1. Extract words 4+ characters long
        2. Remove generic/irrelevant words
        3. Remove URLs and domains
        4. Remove duplicates
        5. Return maximum 10 terms
    """

    stop = {
        "question",
        "questions",
        "marks",
        "explain",
        "discuss",
        "following",
        "answer",
        "answers",
        "write",
        "based",
        "using",
        "with",
        "from",
        "that",
        "this",
        "there",
        "their",
        "about",
        "would",
        "should",
        "could",
        "your",
        "these",
        "those",
        "which",
        "where",
        "when",
        "what",
        "have",
        "been",
        "being",
        "also",
        "used",
        "such",
        "each",
        "more",
        "some",
        "other",
        "into",
        "through",
        "will",
        "must",
        "need",
        "needed",
        "student",
        "students",
        "chapter",
        "chapters",
        "section",
        "sections",
        "material",
        "materials",
        "guide",
        "reading",
        "readings",
        "book",
        "books",
        "prescribed",
        "course",
        "courses",
        "learning",
        "outcome",
        "outcomes",
        "introduction",
        "figure",
        "figures",
        "example",
        "examples",
        "following",
        "provided",
        "provide",
        "provides",
        "including",
        "include",
        "includes",
        "important",
        "information",
    }

    terms: List[str] = []

    for word in re.findall(
        r"[A-Za-z][A-Za-z0-9&._+-]{3,}",
        text or "",
    ):
        # ======================================================================
        # CLEAN
        # ======================================================================

        cleaned = word.strip(".,;:()[]{}<>\"'").strip()

        if not cleaned:
            continue

        lowered = cleaned.lower()

        # ======================================================================
        # IGNORE URLS / DOMAINS
        # ======================================================================

        if (
            lowered.startswith("http://")
            or lowered.startswith("https://")
            or lowered.startswith("www.")
            or "://" in lowered
            or ".com" in lowered
            or ".org" in lowered
            or ".gov" in lowered
            or ".edu" in lowered
        ):
            continue

        # ======================================================================
        # IGNORE STOP WORDS
        # ======================================================================

        if lowered in stop:
            continue

        # ======================================================================
        # IGNORE VERY SHORT / NUMERIC VALUES
        # ======================================================================

        if len(lowered) < 4:
            continue

        if lowered.isdigit():
            continue

        # ======================================================================
        # REMOVE DUPLICATES
        # ======================================================================

        if lowered in [term.lower() for term in terms]:
            continue

        terms.append(cleaned)

        # ======================================================================
        # MAXIMUM 10
        # ======================================================================

        if len(terms) >= 10:
            break

    return terms


# ==============================================================================
# CLEAN LLM KEYWORDS
# ==============================================================================


def clean_llm_keywords(
    keywords,
) -> List[str]:
    """
    Clean and validate keywords returned by the LLM.

    Returns a maximum of 10 keywords.
    """

    if not isinstance(keywords, list):
        return []

    cleaned_keywords: List[str] = []

    for keyword in keywords:
        if not isinstance(keyword, str):
            continue

        keyword = keyword.strip()

        if not keyword:
            continue

        # ==================================================================
        # REMOVE SURROUNDING PUNCTUATION
        # ==================================================================

        keyword = keyword.strip(".,;:()[]{}<>\"'").strip()

        if not keyword:
            continue

        lowered = keyword.lower()

        # ==================================================================
        # IGNORE URLS
        # ==================================================================

        if (
            lowered.startswith("http://")
            or lowered.startswith("https://")
            or lowered.startswith("www.")
            or "://" in lowered
        ):
            continue

        # ==================================================================
        # IGNORE DOMAINS
        # ==================================================================

        if (
            ".com" in lowered
            or ".org" in lowered
            or ".gov" in lowered
            or ".edu" in lowered
        ):
            continue

        # ==================================================================
        # IGNORE YOUTUBE / RANDOM IDENTIFIERS
        #
        # IMPORTANT:
        # Do NOT remove every long alphanumeric word.
        # Academic terms such as:
        #   positivism
        #   interpretivism
        #   pragmatism
        #   reliability
        #   methodology
        # are valid keywords.
        #
        # Only remove identifier-like strings containing numbers,
        # underscores, or hyphens.
        # ==================================================================

        if re.fullmatch(
            r"[A-Za-z0-9_-]{8,}",
            keyword,
        ) and re.search(
            r"[0-9_-]",
            keyword,
        ):
            continue

        # ==================================================================
        # IGNORE PURE NUMBERS
        # ==================================================================

        if lowered.isdigit():
            continue

        # ==================================================================
        # REMOVE DUPLICATES
        # ==================================================================

        if lowered in [item.lower() for item in cleaned_keywords]:
            continue

        # ==================================================================
        # STORE LOWERCASE
        # ==================================================================

        cleaned_keywords.append(lowered)

        # ==================================================================
        # MAXIMUM 10
        # ==================================================================

        if len(cleaned_keywords) >= 10:
            break

    return cleaned_keywords


# ==============================================================================
# EXTRACT RELEVANT KEYWORDS USING QWEN
# ==============================================================================


def extract_relevant_keywords(
    content: str,
) -> List[str]:
    """
    Generate content-side retrieval keywords using Qwen.

    The objective is to identify concepts that are actually
    supported by the supplied content and that can help a
    retrieval system find this chunk when answering questions.

    The LLM is instructed to:
        - Prefer meaningful academic/domain concepts
        - Prefer specific concepts over generic words
        - Prefer multi-word concepts where appropriate
        - Stay strictly grounded in the chunk
        - Avoid generic document/navigation terms
        - Avoid URLs and citation fragments
        - Return 5-10 keywords when enough concepts exist
    """

    if not content or not content.strip():
        return []

    prompt = f"""
You are an expert university faculty member and academic
knowledge-base curator.

You will be given ONE already-split chunk of educational,
academic, business, technical, legal, or reference content.

Your task is to generate retrieval keywords for THIS SPECIFIC
CONTENT CHUNK.

The purpose of these keywords is to help a search system find
this exact chunk when a student question asks about concepts
that are explained, described, defined, discussed, or taught
in the chunk.

==============================================================================
CORE RULE
==============================================================================

Generate keywords based ONLY on what this specific chunk contains.

Every keyword MUST be supported by the supplied content.

A keyword is valid when:

1. The exact term appears in the content, OR
2. The content clearly defines, explains, describes, discusses,
   or directly presents that concept.

Do NOT infer broader concepts merely because they are commonly
associated with the subject.

Do NOT add a concept just because it would normally appear in
the same academic topic.

If the chunk does not support a concept, DO NOT include it.

==============================================================================
KEYWORD SELECTION
==============================================================================

Prioritize:

- Academic concepts
- Subject-specific terminology
- Theories
- Models
- Frameworks
- Research methods
- Research strategies
- Statistical concepts
- Legal concepts
- Business concepts
- Technical concepts
- Processes
- Techniques
- Named methodologies
- Important multi-word concepts
- Specific terms that distinguish this chunk from other chunks

Prefer specific concepts over generic terms.

For example:

GOOD:

research methodology
research design
qualitative research
quantitative research
mixed methods
data collection methods

BAD:

research
data
student
information
method
process
question

==============================================================================
IMPORTANT RETRIEVAL RULE
==============================================================================

The keywords should help distinguish THIS chunk from other
chunks in the same document.

If a generic term such as "research methodology" appears throughout
many chunks but the current chunk contains a more specific concept
such as "positivism", "interpretivism", "research onion", or
"mixed methods", prefer those specific concepts.

Do not fill the keyword list with generic terms simply to reach
10 keywords.

==============================================================================
NUMBER OF KEYWORDS
==============================================================================

Return between 5 and 10 keywords when the chunk contains enough
distinct meaningful concepts.

If the chunk genuinely contains fewer than 5 meaningful concepts,
return fewer.

Never invent keywords just to reach 5 or 10.

Maximum: 10 keywords.

==============================================================================
DO NOT RETURN
==============================================================================

Do NOT return:

- URLs
- website domains
- hyperlinks
- YouTube IDs
- file names
- page numbers
- citation fragments
- generic document-navigation terms
- chapter
- section
- page
- question
- questions
- answer
- answers
- student
- students
- material
- materials
- guide
- reading
- readings
- book
- books
- prescribed
- course
- courses
- learning
- outcome
- outcomes
- explain
- discuss
- write
- following
- using
- based
- example
- examples

unless one of these words is genuinely part of a specific
subject concept.

==============================================================================
URL / WEBSITE RULE
==============================================================================

Never return:

https
http
www
www.gov.za
www.youtube.com
youtube
watch
YouTube IDs
domain names
URL fragments

==============================================================================
DUPLICATES
==============================================================================

Do not return duplicate concepts.

Use lowercase.

Prefer the canonical academic terminology used in the content.

==============================================================================
EXAMPLE
==============================================================================

CONTENT:

"Research methodology refers to the systematic approach used
by researchers to collect and analyse data. Researchers may use
qualitative, quantitative, or mixed-method approaches depending
on the research problem."

GOOD KEYWORDS:

research methodology
qualitative research
quantitative research
mixed methods
data collection
data analysis
research problem

BAD KEYWORDS:

research
researchers
using
data
approach
student
material
question

==============================================================================
ANOTHER EXAMPLE
==============================================================================

CONTENT:

"The research onion presents different layers of methodological
decision-making, including research philosophy, research approach,
research strategy, and research methods. Philosophical positions
include positivism, realism, interpretivism and pragmatism."

GOOD KEYWORDS:

research onion
research philosophy
research approach
research strategy
research methods
positivism
realism
interpretivism
pragmatism

Do NOT add:

qualitative research
quantitative research
data collection

unless those concepts are actually supported by the supplied
content.

==============================================================================
OUTPUT FORMAT
==============================================================================

Return valid JSON only.

Do not wrap JSON in markdown fences.

Use exactly this structure:

{{
    "keywords": [
        "keyword 1",
        "keyword 2",
        "keyword 3"
    ]
}}

==============================================================================
CONTENT
==============================================================================

{content}
"""

    try:
        print("CALLING QWEN FOR RELEVANT KEYWORDS")

        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0,
            max_tokens=300,
        )

        response_text = response.choices[0].message.content.strip()

        print(f"LLM RESPONSE : {response_text}")

        # ==================================================================
        # REMOVE MARKDOWN JSON FENCES
        # ==================================================================

        response_text = re.sub(
            r"^```json\s*",
            "",
            response_text,
            flags=re.IGNORECASE,
        )

        response_text = re.sub(
            r"^```\s*",
            "",
            response_text,
        )

        response_text = re.sub(
            r"\s*```$",
            "",
            response_text,
        )

        response_text = response_text.strip()

        # ==================================================================
        # PARSE JSON
        # ==================================================================

        result = json.loads(response_text)

        keywords = result.get(
            "keywords",
            [],
        )

        # ==================================================================
        # CLEAN KEYWORDS
        # ==================================================================

        cleaned_keywords = clean_llm_keywords(keywords)

        return cleaned_keywords

    except Exception as e:
        print("\n" + "=" * 100)

        print("LLM RELEVANT KEYWORD EXTRACTION FAILED")

        print(f"ERROR : {e}")

        print("=" * 100)

        return []


# ==============================================================================
# GENERATE RELEVANT KEYWORDS FOR DOCUMENT
# ==============================================================================


def generate_relevant_keywords(
    document_id: int,
    user_id: int,
):
    """
    Generate relevant content keywords for every chunk
    belonging to a document.

    Source:
        chunk_content.content

    Destination:
        document_chunks.relevant_keywords

    Only chunks where relevant_keywords IS NULL
    are processed.

    If the LLM fails for a chunk, regex-based extraction
    is used as a fallback.
    """

    conn = get_connection()
    cur = conn.cursor()

    processed = 0
    failed = 0

    print("\n" + "=" * 120)
    print("RELEVANT KEYWORD GENERATION")
    print("=" * 120)

    print(f"DOCUMENT ID : {document_id}")

    print(f"USER ID     : {user_id}")

    try:
        # ==================================================================
        # LOAD CHUNKS
        # ==================================================================

        cur.execute(
            """
            SELECT
                dc.id,
                cc.content
            FROM document_chunks dc
            JOIN chunk_content cc
                ON cc.document_chunk_id = dc.id
            JOIN documents d
                ON d.id = dc.document_id
            WHERE
                dc.document_id = %s
                AND d.user_id = %s
                AND d.is_active = TRUE
                AND dc.is_active = TRUE
                AND cc.is_active = TRUE
                AND dc.relevant_keywords IS NULL
                AND cc.content IS NOT NULL
                AND TRIM(cc.content) <> ''
            ORDER BY dc.id
            """,
            (
                document_id,
                user_id,
            ),
        )

        rows = cur.fetchall()

        total = len(rows)

        print(f"TOTAL CHUNKS : {total}")

        # ==================================================================
        # PROCESS EACH CHUNK
        # ==================================================================

        for index, (
            chunk_id,
            content,
        ) in enumerate(
            rows,
            start=1,
        ):
            try:
                print("\n" + "-" * 100)

                print(f"PROCESSING {index}/{total}")

                print(f"CHUNK ID : {chunk_id}")

                # ==========================================================
                # GENERATE KEYWORDS USING QWEN
                # ==========================================================

                keywords = extract_relevant_keywords(content)

                # ==========================================================
                # FALLBACK
                # ==========================================================

                if not keywords:
                    print("LLM DID NOT RETURN VALID KEYWORDS")

                    print("USING REGEX FALLBACK")

                    keywords = extract_search_terms(content)

                # ==========================================================
                # MAXIMUM 10 KEYWORDS
                # ==========================================================

                keywords = keywords[:10]

                relevant_keywords = ", ".join(keywords)

                print(f"RELEVANT KEYWORDS : {relevant_keywords}")

                # ==========================================================
                # UPDATE DATABASE
                # ==========================================================

                cur.execute(
                    """
                    UPDATE document_chunks
                    SET
                        relevant_keywords = %s,
                        updated_at = CURRENT_TIMESTAMP,
                        updated_by = %s
                    WHERE id = %s
                    """,
                    (
                        relevant_keywords,
                        "SYSTEM",
                        chunk_id,
                    ),
                )

                conn.commit()

                processed += 1

                print(f"CHUNK {chunk_id} UPDATED SUCCESSFULLY")

            except Exception as e:
                conn.rollback()

                failed += 1

                print(f"FAILED CHUNK : {chunk_id}")

                print(f"ERROR : {e}")

                continue

        # ==================================================================
        # COMPLETE
        # ==================================================================

        print("\n" + "=" * 120)

        print("RELEVANT KEYWORD GENERATION COMPLETED")

        print("=" * 120)

        print(f"DOCUMENT ID : {document_id}")

        print(f"TOTAL CHUNKS : {total}")

        print(f"PROCESSED : {processed}")

        print(f"FAILED : {failed}")

        print("=" * 120)

        return {
            "status": "success",
            "document_id": document_id,
            "total_chunks": total,
            "processed": processed,
            "failed": failed,
        }

    except Exception as e:
        conn.rollback()

        print("\nRELEVANT KEYWORD GENERATION FAILED")

        print(f"ERROR : {e}")

        return {
            "status": "failed",
            "document_id": document_id,
            "message": str(e),
        }

    finally:
        cur.close()
        conn.close()
