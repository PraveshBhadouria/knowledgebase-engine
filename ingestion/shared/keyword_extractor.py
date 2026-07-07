from ollama import Client
import json

# Remote Ollama configuration
OLLAMA_HOST = "http://10.192.10.109:11434"
OLLAMA_MODEL = "qwen2.5:14b"

# Create client
client = Client(host=OLLAMA_HOST)


def extract_keywords(content):

    prompt = f"""
Extract the 10 most important business keywords or key phrases.

Rules:
- Return ONLY a valid JSON array
- Maximum 10 keywords
- Prefer business concepts
- Prefer noun phrases
- No explanations
- No markdown

Text:

{content}
"""

    try:

        response = client.chat(
            model=OLLAMA_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            options={
                "temperature": 0,
            },
        )

        result = response["message"]["content"].strip()

        print("\nRAW MODEL OUTPUT:")
        print(result)

        start = result.find("[")
        end = result.rfind("]") + 1

        if start == -1 or end == 0:
            raise ValueError(
                "No valid JSON array found in model response."
            )

        keywords = json.loads(
            result[start:end]
        )

        return keywords

    except Exception as e:

        print(
            f"KEYWORD EXTRACTION FAILED: {e}"
        )

        return []