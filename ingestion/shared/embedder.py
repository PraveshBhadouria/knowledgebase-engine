import os

from sentence_transformers import SentenceTransformer

MODEL_NAME = os.getenv(
    "EMBED_MODEL_NAME",
    "models/bge-base-en-v1.5",
)

print(f"Loading embedding model: {MODEL_NAME}")

model = SentenceTransformer(MODEL_NAME)


def create_embedding(text: str):
    if not text or not text.strip():
        return []

    return model.encode(
        text,
        normalize_embeddings=True,
    ).tolist()