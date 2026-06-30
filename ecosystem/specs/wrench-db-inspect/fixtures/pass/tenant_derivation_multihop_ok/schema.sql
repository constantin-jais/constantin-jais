CREATE TABLE public.activities (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL
);
ALTER TABLE public.activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.activities FORCE ROW LEVEL SECURITY;
CREATE POLICY activities_tenant_all ON public.activities TO rumble_lm_app
  USING (workspace_id = current_setting('app.workspace_id', true)::uuid)
  WITH CHECK (workspace_id = current_setting('app.workspace_id', true)::uuid);

CREATE TABLE public.activity_runs (
  id uuid PRIMARY KEY,
  activity_id uuid NOT NULL REFERENCES public.activities(id)
);
ALTER TABLE public.activity_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.activity_runs FORCE ROW LEVEL SECURITY;
CREATE POLICY activity_runs_tenant_all ON public.activity_runs TO rumble_lm_app
  USING (EXISTS (SELECT 1 FROM public.activities a WHERE a.id = activity_runs.activity_id AND a.workspace_id = current_setting('app.workspace_id', true)::uuid))
  WITH CHECK (EXISTS (SELECT 1 FROM public.activities a WHERE a.id = activity_runs.activity_id AND a.workspace_id = current_setting('app.workspace_id', true)::uuid));

CREATE TABLE public.responses (
  id uuid PRIMARY KEY,
  activity_run_id uuid NOT NULL REFERENCES public.activity_runs(id)
);
ALTER TABLE public.responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.responses FORCE ROW LEVEL SECURITY;
CREATE POLICY responses_tenant_all ON public.responses TO rumble_lm_app
  USING (EXISTS (
    SELECT 1 FROM public.activity_runs ar, public.activities a
    WHERE ar.id = responses.activity_run_id
      AND a.id = ar.activity_id
      AND a.workspace_id = current_setting('app.workspace_id', true)::uuid
  ))
  WITH CHECK (EXISTS (
    SELECT 1 FROM public.activity_runs ar, public.activities a
    WHERE ar.id = responses.activity_run_id
      AND a.id = ar.activity_id
      AND a.workspace_id = current_setting('app.workspace_id', true)::uuid
  ));
