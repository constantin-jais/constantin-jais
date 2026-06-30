CREATE TABLE public.sessions (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL
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
  content_json jsonb NOT NULL,
  CONSTRAINT responses_session_fk FOREIGN KEY (session_id) REFERENCES public.sessions(id)
);
ALTER TABLE public.responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.responses FORCE ROW LEVEL SECURITY;
CREATE POLICY responses_tenant_all ON public.responses TO rumble_lm_app
  USING (EXISTS (
    SELECT 1 FROM public.sessions s
    WHERE responses.session_id = s.id
      AND current_setting('app.workspace_id', true)::uuid = s.workspace_id
  ))
  WITH CHECK (EXISTS (
    SELECT 1 FROM public.sessions s
    WHERE responses.session_id = s.id
      AND current_setting('app.workspace_id', true)::uuid = s.workspace_id
  ));
GRANT SELECT, INSERT, UPDATE ON public.responses TO rumble_lm_app;
