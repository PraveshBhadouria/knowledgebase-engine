-- ==========================================
-- DROP EXISTING TABLES
-- ==========================================

DROP TABLE IF EXISTS module_document_references CASCADE;
DROP TABLE IF EXISTS chunk_content CASCADE;
DROP TABLE IF EXISTS document_chunks CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- ==========================================
-- EXTENSION
-- ==========================================

CREATE EXTENSION IF NOT EXISTS vector;

-- ==========================================
-- USERS TABLE
-- ==========================================

CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,

    full_name VARCHAR(150) NOT NULL,

    email VARCHAR(255) NOT NULL UNIQUE,

    password_hash TEXT NOT NULL,

    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT NOW(),

    updated_at TIMESTAMP
);

CREATE INDEX idx_users_email
ON users(email);

-- ==========================================
-- DOCUMENTS TABLE
-- ==========================================

CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,

    is_active BOOLEAN DEFAULT TRUE,

    document_name VARCHAR NOT NULL,
    document_version VARCHAR,
    source_path TEXT,
    document_type VARCHAR,

    program_id BIGINT,
    module_id BIGINT,

    user_id BIGINT,

    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR,

    updated_at TIMESTAMP,
    updated_by VARCHAR,

    deleted_at TIMESTAMP,
    deleted_by VARCHAR,

    status VARCHAR(20) NOT NULL DEFAULT 'READY',

    CONSTRAINT fk_documents_user
        FOREIGN KEY (user_id)
        REFERENCES users(id)
);

CREATE INDEX idx_documents_is_active
ON documents(is_active);

CREATE INDEX idx_documents_program_module
ON documents(program_id, module_id);

-- ==========================================
-- DOCUMENT CHUNKS TABLE
-- ==========================================

CREATE TABLE document_chunks (
    id BIGSERIAL PRIMARY KEY,

    is_active BOOLEAN DEFAULT TRUE,

    document_id BIGINT NOT NULL,

    node_id INTEGER,

    section_name TEXT,
    chunk_type VARCHAR,

    keywords TSVECTOR,

    page_start INTEGER,
    page_end INTEGER,

    metadata JSONB,

    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR,

    updated_at TIMESTAMP,
    updated_by VARCHAR,

    deleted_at TIMESTAMP,
    deleted_by VARCHAR,

    CONSTRAINT document_chunks_document_id_fkey
        FOREIGN KEY (document_id)
        REFERENCES documents(id)
);

CREATE INDEX idx_document_chunks_document_id
ON document_chunks(document_id);

CREATE INDEX idx_document_chunks_is_active
ON document_chunks(is_active);

CREATE INDEX idx_document_chunks_keywords
ON document_chunks
USING GIN(keywords);

CREATE INDEX idx_document_chunks_metadata
ON document_chunks
USING GIN(metadata);

-- ==========================================
-- CHUNK CONTENT TABLE
-- ==========================================

CREATE TABLE chunk_content (
    id BIGSERIAL PRIMARY KEY,

    document_chunk_id BIGINT UNIQUE NOT NULL,

    content TEXT,

    -- BAAI/bge-base-en-v1.5 => 768 dimensions
    embedding VECTOR(768),

    is_active BOOLEAN DEFAULT TRUE,

    created_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR,

    updated_at TIMESTAMP,
    updated_by VARCHAR,

    deleted_at TIMESTAMP,
    deleted_by VARCHAR,

    CONSTRAINT chunk_content_document_chunk_id_fkey
        FOREIGN KEY (document_chunk_id)
        REFERENCES document_chunks(id)
);

CREATE INDEX idx_chunk_content_is_active
ON chunk_content(is_active);

CREATE INDEX idx_chunk_content_embedding_hnsw
ON chunk_content
USING hnsw (embedding vector_cosine_ops);

-- ==========================================
-- MODULE DOCUMENT REFERENCES TABLE
-- ==========================================

CREATE TABLE module_document_references (
    reference_id BIGSERIAL PRIMARY KEY,

    document_id BIGINT NOT NULL,

    is_active BOOLEAN DEFAULT TRUE,

    reference_text TEXT NOT NULL,

    reference_url TEXT,

    reference_order INTEGER,

    page_start INTEGER,
    page_end INTEGER,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100) DEFAULT 'system',

    updated_at TIMESTAMP,
    updated_by VARCHAR(100),

    CONSTRAINT fk_reference_document
        FOREIGN KEY (document_id)
        REFERENCES documents(id)
        ON DELETE CASCADE
);

-- These indexes are included even though they are currently missing in your DB.
-- They are useful for query performance.

CREATE INDEX idx_module_document_references_document_id
ON module_document_references(document_id);

CREATE INDEX idx_module_document_references_is_active
ON module_document_references(is_active);