CREATE TABLE public.items (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL
);
ALTER TABLE public.items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.items FORCE ROW LEVEL SECURITY;
CREATE POLICY items_tenant_all ON public.items TO app_role
  USING (workspace_id = current_setting('app.workspace_id', true)::uuid)
  WITH CHECK (workspace_id = current_setting('app.workspace_id', true)::uuid);
GRANT SELECT, INSERT, UPDATE ON public.items TO app_role;
ALTER TABLE public.items NO FORCE ROW LEVEL SECURITY;
