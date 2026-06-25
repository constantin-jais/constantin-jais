CREATE TABLE public.session_responses (
  id uuid PRIMARY KEY,
  organization_id uuid NOT NULL,
  session_id uuid NOT NULL,
  response_summary text NOT NULL
);
