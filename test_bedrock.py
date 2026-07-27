import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env
load_dotenv()

# Read the bearer token
token = os.getenv("AWS_BEARER_TOKEN_BEDROCK")

if not token:
    raise ValueError(
        "AWS_BEARER_TOKEN_BEDROCK not found. "
        "Please set it in your .env file or export it in your terminal."
    )

# Configuration
MODEL_ID = "qwen.qwen3-coder-30b-a3b-instruct"

client = OpenAI(
    api_key=token,
    base_url="https://bedrock-mantle.ap-south-1.api.aws/v1",
)

print("✓ Token loaded successfully")
print(f"✓ Using model: {MODEL_ID}")

try:
    response = client.chat.completions.create(
        model=MODEL_ID,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant."
            },
            {
                "role": "user",
                "content": "Say hello in one sentence."
            },
        ],
        temperature=0,
    )

    print("\n========== RESPONSE ==========\n")
    print(response.choices[0].message.content)

except Exception as e:
    print("\n========== ERROR ==========\n")
    print(type(e).__name__)
    print(e)