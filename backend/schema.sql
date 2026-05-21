-- Migraciones DDL iniciales para MVP Asistente Penal
-- Habilitar extensión pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Tabla de Fuentes Legales (Leyes)
CREATE TABLE IF NOT EXISTS legal_sources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    jurisdiction TEXT NOT NULL,
    type TEXT NOT NULL,
    version TEXT,
    status TEXT NOT NULL DEFAULT 'active',
    published_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de Chunks Legales
CREATE TABLE IF NOT EXISTS legal_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id UUID REFERENCES legal_sources(id) ON DELETE CASCADE,
    article_number TEXT NOT NULL,
    fraction TEXT,
    content TEXT NOT NULL,
    hierarchical_path TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de Vectores
CREATE TABLE IF NOT EXISTS chunk_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chunk_id UUID REFERENCES legal_chunks(id) ON DELETE CASCADE,
    embedding VECTOR(1536) -- Tamaño de text-embedding-3-small
);

-- Índices para búsqueda
CREATE INDEX ON chunk_embeddings USING hnsw (embedding vector_cosine_ops);

-- (El resto de tablas de negocio se añaden iterativamente)
