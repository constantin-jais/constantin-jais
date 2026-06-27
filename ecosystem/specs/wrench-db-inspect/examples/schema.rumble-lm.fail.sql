-- Minimal sanitized rumble-lm schema expected to fail current P0 prototype checks.
-- Intentional issues:
-- 1. public.responses is tenant-scoped but RLS is not enabled/forced.
-- 2. public.responses grants ALL to the application role.

CREATE TABLE public.sessions (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL,
  title text NOT NULL,
  status text NOT NULL,
  created_at timestamptz NOT NULL
);
ALTER TABLE public.sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sessions FORCE ROW LEVEL SECURITY;
GRANT SELECT, INSERT, UPDATE ON public.sessions TO rumble_lm_app;

CREATE TABLE public.source_sets (id uuid PRIMARY KEY, session_id uuid NOT NULL);
ALTER TABLE public.source_sets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.source_sets FORCE ROW LEVEL SECURITY;
GRANT SELECT, INSERT, UPDATE ON public.source_sets TO rumble_lm_app;

CREATE TABLE public.source_set_items (id uuid PRIMARY KEY, source_set_id uuid NOT NULL, source_ref text NOT NULL);
ALTER TABLE public.source_set_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.source_set_items FORCE ROW LEVEL SECURITY;
GRANT SELECT, INSERT, UPDATE ON public.source_set_items TO rumble_lm_app;

CREATE TABLE public.activities (id uuid PRIMARY KEY, session_id uuid NOT NULL, title text NOT NULL);
ALTER TABLE public.activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.activities FORCE ROW LEVEL SECURITY;
GRANT SELECT, INSERT, UPDATE ON public.activities TO rumble_lm_app;

CREATE TABLE public.activity_options (id uuid PRIMARY KEY, activity_id uuid NOT NULL, label text NOT NULL, value text NOT NULL);
ALTER TABLE public.activity_options ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.activity_options FORCE ROW LEVEL SECURITY;
GRANT SELECT, INSERT, UPDATE ON public.activity_options TO rumble_lm_app;

CREATE TABLE public.activity_runs (id uuid PRIMARY KEY, session_id uuid NOT NULL, activity_id uuid NOT NULL, status text NOT NULL);
ALTER TABLE public.activity_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.activity_runs FORCE ROW LEVEL SECURITY;
GRANT SELECT, INSERT, UPDATE ON public.activity_runs TO rumble_lm_app;

CREATE TABLE public.participants (id uuid PRIMARY KEY, session_id uuid NOT NULL, display_name text);
ALTER TABLE public.participants ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.participants FORCE ROW LEVEL SECURITY;
GRANT SELECT, INSERT, UPDATE ON public.participants TO rumble_lm_app;

CREATE TABLE public.responses (
  id uuid PRIMARY KEY,
  session_id uuid NOT NULL,
  activity_id uuid NOT NULL,
  participant_id uuid NOT NULL,
  content_json jsonb NOT NULL,
  submitted_at timestamptz NOT NULL
);
GRANT ALL ON public.responses TO rumble_lm_app;

CREATE TABLE public.citations (id uuid PRIMARY KEY, session_id uuid NOT NULL, source_ref text NOT NULL);
ALTER TABLE public.citations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.citations FORCE ROW LEVEL SECURITY;
GRANT SELECT, INSERT, UPDATE ON public.citations TO rumble_lm_app;

CREATE TABLE public.summaries (id uuid PRIMARY KEY, session_id uuid NOT NULL, content_json jsonb NOT NULL);
ALTER TABLE public.summaries ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.summaries FORCE ROW LEVEL SECURITY;
GRANT SELECT, INSERT, UPDATE ON public.summaries TO rumble_lm_app;

CREATE TABLE public.exports (id uuid PRIMARY KEY, session_id uuid NOT NULL, included_data_json jsonb NOT NULL);
ALTER TABLE public.exports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.exports FORCE ROW LEVEL SECURITY;
GRANT SELECT, INSERT, UPDATE ON public.exports TO rumble_lm_app;

CREATE TABLE public.audit_events (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL,
  session_id uuid,
  event_name text NOT NULL,
  metadata_json jsonb,
  created_at timestamptz NOT NULL
);
GRANT SELECT, INSERT ON public.audit_events TO rumble_lm_app;
