# tests/test_embedding.py

from ingestion.shared.embedder import create_embedding

embedding = create_embedding(
    "Hello World"
)

print(len(embedding))