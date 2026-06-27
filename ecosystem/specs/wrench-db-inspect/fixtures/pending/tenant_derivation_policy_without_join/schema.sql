-- Pending fixture: should fail once tenant_derivation validation is implemented.
-- Problem: public.responses has an FK to sessions, but its RLS policy does not constrain
-- access through sessions.workspace_id or current tenant context.

CREATE TABLE public.sessions (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL,
  title text NOT NULL
);
ALTER TABLE public.sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sessions FORCE ROW LEVEL SECURITY;
CREATE POLICY sessions_tenant_all ON public.sessions TO rumble_lm_app
  USING (workspace_id = current_setting('app.workspace_id', true)::uuid)
  WITH CHECK (workspace_id = current_setting('app.workspace_id', true)::uuid);
GRANT SELECT, INSERT, UPDATE ON public.sessions TO rumble_lm_app;

CREATE TABLE public.responses (
  id uuid PRIMARY KEY,
  session_id uuid NOT NULL REFERENCES public.sessions(id),
  content_json jsonb NOT NULL
);
ALTER TABLE public.responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.responses FORCE ROW LEVEL SECURITY;
-- Bad: policy is structurally present but does not enforce tenant derivation.
CREATE POLICY responses_unscoped ON public.responses TO rumble_lm_app
  USING (true)
  WITH CHECK (true);
GRANT SELECT, INSERT, UPDATE ON public.responses TO rumble_lm_app;
