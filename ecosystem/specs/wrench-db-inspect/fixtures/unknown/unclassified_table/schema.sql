CREATE TABLE public.canvas_comments (
  id uuid PRIMARY KEY,
  organization_id uuid NOT NULL,
  body text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE public.canvas_comments ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.canvas_comments FORCE ROW LEVEL SECURITY;
