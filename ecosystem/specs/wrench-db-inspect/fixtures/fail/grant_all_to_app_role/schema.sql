CREATE TABLE public.tasks (
  id uuid PRIMARY KEY,
  organization_id uuid NOT NULL,
  title text NOT NULL
);

ALTER TABLE public.tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tasks FORCE ROW LEVEL SECURITY;

CREATE POLICY tasks_tenant_all
  ON public.tasks
  TO rumble_app
  USING (organization_id = current_setting('app.organization_id', true)::uuid)
  WITH CHECK (organization_id = current_setting('app.organization_id', true)::uuid);

GRANT ALL ON public.tasks TO rumble_app;
