-- Dev seed data — local testing only, never run in production
-- Applied automatically by: supabase db reset

INSERT INTO tenants (id, name, slug) VALUES
  ('00000000-0000-0000-0000-000000000001', 'Acme Corp (Test)', 'acme-test');

INSERT INTO agents (id, tenant_id, name) VALUES
  ('00000000-0000-0000-0000-000000000010', '00000000-0000-0000-0000-000000000001', 'PM Agent');

-- Default workflow configs (draft mode for all)
INSERT INTO workflow_configs (tenant_id, agent_id, workflow_name, mode, admin_max_mode) VALUES
  ('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000010', 'sprint_status', 'draft', 'draft'),
  ('00000000-0000-0000-0000-000000000001', '00000000-0000-0000-0000-000000000010', 'standup_summary', 'draft', 'draft');
