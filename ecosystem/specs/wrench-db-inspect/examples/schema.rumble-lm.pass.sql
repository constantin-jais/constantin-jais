-- Minimal sanitized rumble-lm schema expected to pass current P0/P1 prototype checks.
-- Tenant canonical mapping: organization -> workspace_id.

CREATE TABLE public.sessions (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL,
  title text NOT NULL,
  objective text,
  status text NOT NULL,
  facilitator_actor_id text,
  active_source_set_id uuid,
  settings_json jsonb,
  created_at timestamptz NOT NULL
);
ALTER TABLE public.sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sessions FORCE ROW LEVEL SECURITY;
CREATE POLICY sessions_tenant_all ON public.sessions TO rumble_lm_app
  USING (workspace_id = current_setting('app.workspace_id', true)::uuid)
  WITH CHECK (workspace_id = current_setting('app.workspace_id', true)::uuid);
GRANT SELECT, INSERT, UPDATE ON public.sessions TO rumble_lm_app;

CREATE TABLE public.source_sets (
  id uuid PRIMARY KEY,
  session_id uuid NOT NULL REFERENCES public.sessions(id),
  revision integer NOT NULL,
  status text NOT NULL,
  created_by text,
  created_at timestamptz NOT NULL
);
ALTER TABLE public.source_sets ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.source_sets FORCE ROW LEVEL SECURITY;
CREATE POLICY source_sets_tenant_all ON public.source_sets TO rumble_lm_app
  USING (EXISTS (
    SELECT 1 FROM public.sessions s
    WHERE s.id = source_sets.session_id
      AND s.workspace_id = current_setting('app.workspace_id', true)::uuid
  ))
  WITH CHECK (EXISTS (
    SELECT 1 FROM public.sessions s
    WHERE s.id = source_sets.session_id
      AND s.workspace_id = current_setting('app.workspace_id', true)::uuid
  ));
GRANT SELECT, INSERT, UPDATE ON public.source_sets TO rumble_lm_app;

CREATE TABLE public.source_set_items (
  id uuid PRIMARY KEY,
  source_set_id uuid NOT NULL REFERENCES public.source_sets(id),
  source_ref text NOT NULL,
  title_snapshot text,
  provenance_snapshot jsonb,
  added_at timestamptz NOT NULL
);
ALTER TABLE public.source_set_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.source_set_items FORCE ROW LEVEL SECURITY;
CREATE POLICY source_set_items_tenant_all ON public.source_set_items TO rumble_lm_app
  USING (EXISTS (
    SELECT 1 FROM public.source_sets ss, public.sessions s
    WHERE ss.id = source_set_items.source_set_id
      AND s.id = ss.session_id
      AND s.workspace_id = current_setting('app.workspace_id', true)::uuid
  ))
  WITH CHECK (EXISTS (
    SELECT 1 FROM public.source_sets ss, public.sessions s
    WHERE ss.id = source_set_items.source_set_id
      AND s.id = ss.session_id
      AND s.workspace_id = current_setting('app.workspace_id', true)::uuid
  ));
GRANT SELECT, INSERT, UPDATE ON public.source_set_items TO rumble_lm_app;

CREATE TABLE public.activities (
  id uuid PRIMARY KEY,
  session_id uuid NOT NULL REFERENCES public.sessions(id),
  type text NOT NULL,
  title text NOT NULL,
  prompt text,
  status text NOT NULL,
  agenda_order integer NOT NULL,
  response_mode jsonb,
  visibility jsonb,
  grounding_mode text,
  source_set_revision integer,
  generated_metadata jsonb,
  created_by text,
  created_at timestamptz NOT NULL
);
ALTER TABLE public.activities ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.activities FORCE ROW LEVEL SECURITY;
CREATE POLICY activities_tenant_all ON public.activities TO rumble_lm_app
  USING (EXISTS (
    SELECT 1 FROM public.sessions s
    WHERE s.id = activities.session_id
      AND s.workspace_id = current_setting('app.workspace_id', true)::uuid
  ))
  WITH CHECK (EXISTS (
    SELECT 1 FROM public.sessions s
    WHERE s.id = activities.session_id
      AND s.workspace_id = current_setting('app.workspace_id', true)::uuid
  ));
GRANT SELECT, INSERT, UPDATE ON public.activities TO rumble_lm_app;

CREATE TABLE public.activity_options (
  id uuid PRIMARY KEY,
  activity_id uuid NOT NULL REFERENCES public.activities(id),
  label text NOT NULL,
  value text NOT NULL,
  is_correct boolean,
  agenda_order integer NOT NULL,
  metadata_json jsonb
);
ALTER TABLE public.activity_options ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.activity_options FORCE ROW LEVEL SECURITY;
CREATE POLICY activity_options_tenant_all ON public.activity_options TO rumble_lm_app
  USING (EXISTS (
    SELECT 1 FROM public.activities a, public.sessions s
    WHERE a.id = activity_options.activity_id
      AND s.id = a.session_id
      AND s.workspace_id = current_setting('app.workspace_id', true)::uuid
  ))
  WITH CHECK (EXISTS (
    SELECT 1 FROM public.activities a, public.sessions s
    WHERE a.id = activity_options.activity_id
      AND s.id = a.session_id
      AND s.workspace_id = current_setting('app.workspace_id', true)::uuid
  ));
GRANT SELECT, INSERT, UPDATE ON public.activity_options TO rumble_lm_app;

CREATE TABLE public.activity_runs (
  id uuid PRIMARY KEY,
  session_id uuid NOT NULL REFERENCES public.sessions(id),
  activity_id uuid NOT NULL,
  status text NOT NULL,
  started_by text,
  started_at timestamptz NOT NULL
);
ALTER TABLE public.activity_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.activity_runs FORCE ROW LEVEL SECURITY;
CREATE POLICY activity_runs_tenant_all ON public.activity_runs TO rumble_lm_app
  USING (EXISTS (
    SELECT 1 FROM public.sessions s
    WHERE s.id = activity_runs.session_id
      AND s.workspace_id = current_setting('app.workspace_id', true)::uuid
  ))
  WITH CHECK (EXISTS (
    SELECT 1 FROM public.sessions s
    WHERE s.id = activity_runs.session_id
      AND s.workspace_id = current_setting('app.workspace_id', true)::uuid
  ));
GRANT SELECT, INSERT, UPDATE ON public.activity_runs TO rumble_lm_app;

CREATE TABLE public.participants (
  id uuid PRIMARY KEY,
  session_id uuid NOT NULL REFERENCES public.sessions(id),
  actor_ref text,
  display_name text,
  join_mode text NOT NULL,
  joined_at timestamptz NOT NULL,
  anonymized_at timestamptz
);
ALTER TABLE public.participants ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.participants FORCE ROW LEVEL SECURITY;
CREATE POLICY participants_tenant_all ON public.participants TO rumble_lm_app
  USING (EXISTS (
    SELECT 1 FROM public.sessions s
    WHERE s.id = participants.session_id
      AND s.workspace_id = current_setting('app.workspace_id', true)::uuid
  ))
  WITH CHECK (EXISTS (
    SELECT 1 FROM public.sessions s
    WHERE s.id = participants.session_id
      AND s.workspace_id = current_setting('app.workspace_id', true)::uuid
  ));
GRANT SELECT, INSERT, UPDATE ON public.participants TO rumble_lm_app;

CREATE TABLE public.responses (
  id uuid PRIMARY KEY,
  session_id uuid NOT NULL REFERENCES public.sessions(id),
  activity_id uuid NOT NULL,
  activity_run_id uuid NOT NULL,
  participant_id uuid NOT NULL,
  content_json jsonb NOT NULL,
  response_type text NOT NULL,
  visibility_snapshot jsonb NOT NULL,
  submitted_at timestamptz NOT NULL,
  anonymized_at timestamptz
);
ALTER TABLE public.responses ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.responses FORCE ROW LEVEL SECURITY;
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

CREATE TABLE public.citations (
  id uuid PRIMARY KEY,
  session_id uuid NOT NULL REFERENCES public.sessions(id),
  target_type text NOT NULL,
  target_id uuid NOT NULL,
  source_ref text NOT NULL,
  source_chunk_ref text,
  quote text,
  location_json jsonb,
  support_level text,
  status text NOT NULL,
  created_at timestamptz NOT NULL
);
ALTER TABLE public.citations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.citations FORCE ROW LEVEL SECURITY;
CREATE POLICY citations_tenant_all ON public.citations TO rumble_lm_app
  USING (EXISTS (
    SELECT 1 FROM public.sessions s
    WHERE s.id = citations.session_id
      AND s.workspace_id = current_setting('app.workspace_id', true)::uuid
  ))
  WITH CHECK (EXISTS (
    SELECT 1 FROM public.sessions s
    WHERE s.id = citations.session_id
      AND s.workspace_id = current_setting('app.workspace_id', true)::uuid
  ));
GRANT SELECT, INSERT, UPDATE ON public.citations TO rumble_lm_app;

CREATE TABLE public.summaries (
  id uuid PRIMARY KEY,
  session_id uuid NOT NULL REFERENCES public.sessions(id),
  audience text NOT NULL,
  status text NOT NULL,
  revision integer NOT NULL,
  content_json jsonb NOT NULL,
  generated_metadata jsonb,
  generated_at timestamptz
);
ALTER TABLE public.summaries ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.summaries FORCE ROW LEVEL SECURITY;
CREATE POLICY summaries_tenant_all ON public.summaries TO rumble_lm_app
  USING (EXISTS (
    SELECT 1 FROM public.sessions s
    WHERE s.id = summaries.session_id
      AND s.workspace_id = current_setting('app.workspace_id', true)::uuid
  ))
  WITH CHECK (EXISTS (
    SELECT 1 FROM public.sessions s
    WHERE s.id = summaries.session_id
      AND s.workspace_id = current_setting('app.workspace_id', true)::uuid
  ));
GRANT SELECT, INSERT, UPDATE ON public.summaries TO rumble_lm_app;

CREATE TABLE public.exports (
  id uuid PRIMARY KEY,
  session_id uuid NOT NULL REFERENCES public.sessions(id),
  format text NOT NULL,
  audience text NOT NULL,
  included_data_json jsonb NOT NULL,
  artifact_ref text,
  checksum text,
  generated_by text,
  generated_at timestamptz NOT NULL,
  revoked_at timestamptz
);
ALTER TABLE public.exports ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.exports FORCE ROW LEVEL SECURITY;
CREATE POLICY exports_tenant_all ON public.exports TO rumble_lm_app
  USING (EXISTS (
    SELECT 1 FROM public.sessions s
    WHERE s.id = exports.session_id
      AND s.workspace_id = current_setting('app.workspace_id', true)::uuid
  ))
  WITH CHECK (EXISTS (
    SELECT 1 FROM public.sessions s
    WHERE s.id = exports.session_id
      AND s.workspace_id = current_setting('app.workspace_id', true)::uuid
  ));
GRANT SELECT, INSERT, UPDATE ON public.exports TO rumble_lm_app;

CREATE TABLE public.audit_events (
  id uuid PRIMARY KEY,
  workspace_id uuid NOT NULL,
  session_id uuid,
  actor_ref jsonb,
  event_name text NOT NULL,
  target_type text,
  target_id text,
  metadata_json jsonb,
  created_at timestamptz NOT NULL
);
GRANT SELECT, INSERT ON public.audit_events TO rumble_lm_app;
