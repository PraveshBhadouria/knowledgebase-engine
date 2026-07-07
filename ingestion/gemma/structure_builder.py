import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"

MODEL = "qwen3:8b"


def load_blocks():

    with open(
        "outputs/blocks.json",
        "r"
    ) as f:

        return json.load(f)


def build_prompt(blocks):

    return f"""
You are an expert document parser.

Your task is to analyze PDF blocks and create a hierarchical document structure.

Detect:

1. Chapters
2. Sections
3. Subsections
4. Introductory text before sections

Attach all content to the correct heading.

Return ONLY valid JSON.

Schema:

{{
  "chapters":[
    {{
      "title":"",
      "intro":"",
      "sections":[
        {{
          "title":"",
          "content":"",
          "subsections":[]
        }}
      ]
    }}
  ]
}}

Blocks:

{json.dumps(blocks, indent=2)}
"""


def call_ollama(prompt):

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        }
    )

    response.raise_for_status()

    return response.json()["response"]


def save_structure(result):

    with open(
        "outputs/structure.json",
        "w"
    ) as f:

        f.write(result)


def main():

    print("Loading blocks...")

    blocks = load_blocks()

    print(
        f"Loaded {len(blocks)} blocks"
    )

    prompt = build_prompt(blocks)

    print(
        "Sending to Ollama..."
    )

    structure = call_ollama(
        prompt
    )

    save_structure(
        structure
    )

    print(
        "Saved structure.json"
    )


if __name__ == "__main__":
    main()