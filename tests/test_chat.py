from retrieval.context_builder import get_context
from services.llm_service import generate_answer

question = "What is retail banking?"

context = get_context(question)

answer = generate_answer(
    question,
    context,
)

print(answer)