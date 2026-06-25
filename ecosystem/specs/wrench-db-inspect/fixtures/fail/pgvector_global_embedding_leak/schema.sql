CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE public.source_embeddings (
  id uuid PRIMARY KEY,
  source_ref_id uuid NOT NULL,
  embedding vector(3) NOT NULL
);

CREATE FUNCTION public.match_sources(query_embedding vector(3), match_count int)
RETURNS TABLE (source_ref_id uuid, distance float)
LANGUAGE sql
STABLE
AS $$
  SELECT source_ref_id, embedding <-> query_embedding AS distance
  FROM public.source_embeddings
  ORDER BY embedding <-> query_embedding
  LIMIT match_count
$$;

GRANT EXECUTE ON FUNCTION public.match_sources(vector, int) TO rumble_app;
