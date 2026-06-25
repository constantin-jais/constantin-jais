CREATE TABLE public.session_responses (
  id uuid PRIMARY KEY,
  organization_id uuid NOT NULL,
  session_id uuid NOT NULL,
  response_summary text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE public.session_responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.session_responses FORCE ROW LEVEL SECURITY;

CREATE POLICY session_responses_tenant_select
  ON public.session_responses
  FOR SELECT
  TO rumble_app
  USING (organization_id = current_setting('app.organization_id', true)::uuid);

CREATE POLICY session_responses_tenant_insert
  ON public.session_responses
  FOR INSERT
  TO rumble_app
  WITH CHECK (organization_id = current_setting('app.organization_id', true)::uuid);

GRANT SELECT, INSERT, UPDATE ON public.session_responses TO rumble_app;
GRANT SELECT ON public.session_responses TO rumble_readonly;
