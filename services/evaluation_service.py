from retrieval.context_builder import get_context
from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def evaluate_answer(question, student_answer):

    context = get_context(question)

    # Protect Evaluation
    if not context.strip():

        return """
Marks: 0/10

Feedback:
No relevant information was found in the knowledge base.

Strengths:
None

Improvements:
The answer cannot be evaluated because the knowledge base does not contain information related to the question.
"""

    # Protect LLM
    prompt = f"""
You are an academic evaluator.

IMPORTANT RULES:

1. Evaluate ONLY using the provided context.
2. Do NOT use outside knowledge.
3. Do NOT guess.
4. Do NOT infer missing facts.
5. If the context does not contain enough information,
   return Marks = 0.

Reference Material:

{context}

Question:

{question}

Student Answer:

{student_answer}

Return exactly in this format:

Marks: X/10

Feedback:
...

Strengths:
- ...
- ...

Improvements:
- ...
- ...
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    return response.choices[0].message.content
