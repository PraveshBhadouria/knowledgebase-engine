CREATE TABLE IF NOT EXISTS knowledge_chunks (
    id SERIAL PRIMARY KEY,

    source_file TEXT,
    course_name TEXT,
    section_name TEXT,
    chunk_type TEXT,

    content TEXT NOT NULL,

    search_vector tsvector,

    embedding vector(1536),

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_search_vector
ON knowledge_chunks
USING GIN(search_vector);