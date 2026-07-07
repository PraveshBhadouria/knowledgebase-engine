from services.evaluation_service import evaluate_answer

result = evaluate_answer(
    question="What is retail banking?",
    student_answer="""
Retail banking serves individual customers.
It accepts deposits and provides loans.
"""
)

print(result)