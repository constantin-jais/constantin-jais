-- Pending fixture: should fail once tenant_derivation validation is implemented.
-- Problem: public.responses declares tenant derivation through session_id -> sessions.workspace_id,
-- but the schema does not define an FK or any enforceable relationship from responses.session_id to sessions.id.

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
  session_id uuid NOT NULL,
  content_json jsonb NOT NULL
);
ALTER TABLE public.responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.responses FORCE ROW LEVEL SECURITY;
-- This policy references the parent table but the declared derivation path is not backed by an FK.
CREATE POLICY responses_tenant_all ON public.responses TO rumble_lm_app
  USING (EXISTS (
    SELECT 1 FROM public.sessions s
    WHERE s.id = responses.session_id
      AND s.workspace_id = current_setting('app.workspace_id', true)::uuid
  ))
  WITH CHECK (EXISTS (
    SELECT 1 FROM public.sessions s
    WHERE s.id = responses.session_id
      AND s.workspace_id = current_setting('app.workspace_id', true)::uuid
  ));
GRANT SELECT, INSERT, UPDATE ON public.responses TO rumble_lm_app;
