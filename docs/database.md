# Document table creation
```sql
DROP TABLE IF EXISTS checkpoint_blobs CASCADE;
DROP TABLE IF EXISTS checkpoint_migrations CASCADE;
DROP TABLE IF EXISTS checkpoint_writes CASCADE;
DROP TABLE IF EXISTS checkpoints CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS langchain_pg_embedding CASCADE;
DROP TABLE IF EXISTS langchain_pg_collection CASCADE;
DROP TABLE IF EXISTS public.documents CASCADE;

-- Same PDF → different users → allowed
-- Same PDF → same user → prevented duplication
CREATE TABLE public.documents (
    id serial PRIMARY KEY,
    -- Every document chunk MUST belong to exactly one user and that user must exist in Supabase Auth.
    -- REFERENCES auth.users(id) --> documents.user_id must match a real user in auth.users
    -- ON DELETE CASCADE --> If a user is deleted → all their documents are automatically deleted
     -- auth.user is a system table managed by Supabase Authentication.
     -- This table stores every authenticated user in your app.
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,  
    doc_id text NOT NULL,
    chunk_index int NOT NULL,
    file_name text,
    page int,
    content text,
    uploaded_at timestamp default now(),
    UNIQUE (user_id, doc_id, chunk_index)
);


-- RLS
CREATE POLICY "Users access own documents"
ON documents
FOR ALL
USING (auth.uid() = user_id);




-- What is auth.users.id?
-- This is the user’s unique ID.
-- Type: uuid
-- Generated automatically by Supabase
-- Never changes
-- Same across frontend & backend


```









# Embedding column Check
```sql
-- verify embedding column then apply indexing on that
SELECT 
  attname,
  atttypid::regtype
FROM pg_attribute
WHERE attrelid = 'langchain_pg_embedding'::regclass
  AND attname = 'embedding';


-- cehck if thier is any bad row
SELECT COUNT(*) AS bad_rows
FROM langchain_pg_embedding
WHERE vector_dims(embedding) != 1536;
```









---

# Create thread table
```sql

-- table for storing chat history(persistance)
DROP TABLE IF EXISTS threads CASCADE;

-- Threads must belong to a user
-- Threads must be isolated by tenant
CREATE TABLE threads (
    thread_id text PRIMARY KEY,

    -- Every document chunk MUST belong to exactly one user and that user must exist in Supabase Auth.
    -- REFERENCES auth.users(id) --> documents.user_id must match a real user in auth.users
    -- ON DELETE CASCADE --> If a user is deleted → all their documents are automatically deleted
    -- auth.user is a system table managed by Supabase Authentication.
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    --doc_id text NOT NULL, -- store single doc id per thread
    doc_ids text[] DEFAULT '{}',  -- for storing multple doc id in array
    messages jsonb,
    summary text DEFAULT '',
    created_at timestamp default now()
);


-- RLS
CREATE POLICY "Users access own threads"
ON threads
FOR ALL
USING (auth.uid() = user_id);

```

---

# imporve index performance
```sql


-- HNSW REQUIRES fixed dimensions
-- Without this, Postgres literally cannot index vectors


-- Add a new fixed-dimension column
ALTER TABLE langchain_pg_embedding
ADD COLUMN embedding_1536 vector(1536);

-- Copy existing embeddings
UPDATE langchain_pg_embedding
SET embedding_1536 = embedding;

-- Replace the old column
ALTER TABLE langchain_pg_embedding
DROP COLUMN embedding;

ALTER TABLE langchain_pg_embedding
RENAME COLUMN embedding_1536 TO embedding;


-- We are adding HNSW indexing algorithm
-- as our embeddings are controlled by langchian PGVector we add this to the table

CREATE INDEX langchain_pg_embedding_hnsw
ON langchain_pg_embedding
-- using HNSW(use embedding column for HNSW , and use cosine similarity as the metric )
USING hnsw (embedding vector_cosine_ops)
-- m → number of neighbors per node in the HNSW graph
-- Higher m → more accurate but uses more memory
-- Lower m → faster insert, slightly lower recall
-- ef_construction → search accuracy during index construction
-- Higher → slower build, better graph quality, higher recall
-- Lower → faster build, slightly worse recall
WITH (m = 16, ef_construction = 200);




-- Metadata filtering it imporve speed
CREATE INDEX langchain_pg_embedding_metadata_idx
ON langchain_pg_embedding
USING gin (cmetadata);



-- cmetadata is a jsonb column storing metadata for each chunk, e.g.,:
-- {
--   "doc_id": "1234",
--   "user_id": "abcd-efgh",
--   "file_name": "mydoc.pdf",
--   "page": 5
-- }
-- GIN (Generalized Inverted Index) is perfect for JSONB lookups
-- Makes queries like WHERE cmetadata @> '{"user_id":"abcd"}' fast
-- Without this, filtering by user or doc_id in JSONB is slow for millions of rows



```





# TOken Usage
```sql
DROP TABLE IF EXISTS usage CASCADE;

-- Table for token usage 
CREATE TABLE IF NOT EXISTS usage(
  id BIGSERIAL PRIMARY KEY,
  user_id UUID NOT NULL,
  doc_id TEXT,
  thread_id TEXT,
  total_tokens INT NOT NULL DEFAULT 0,
  prompt_tokens INT NOT NULL DEFAULT 0,
  completion_tokens INT NOT NULL DEFAULT 0,
  query TEXT,
  answer TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);


-- Indexes help if you query token usage per user or per document frequently.


-- Index on user_id for faster queries per user
CREATE INDEX IF NOT EXISTS idx_usage_user_id ON usage(user_id);


--  Index on doc_id for queries per document
CREATE INDEX IF NOT EXISTS idx_usage_doc_id ON usage(doc_id)
```








# Table for User Settings
```sql
CREATE TABLE IF NOT EXISTS user_settings (
  user_id UUID PRIMARY KEY REFERENCES auth.users(id),
  custom_prompt TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;

-- Users can only access their own settings
CREATE POLICY "Users can view own settings" ON user_settings FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own settings" ON user_settings FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own settings" ON user_settings FOR UPDATE USING (auth.uid() = user_id);
```
