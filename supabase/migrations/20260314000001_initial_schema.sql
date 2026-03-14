-- ProductMind AI — Initial Schema
-- Phase 1: Walking Skeleton
--
-- Run via: supabase db push
-- Or locally: supabase db reset (applies all migrations + seed.sql)

-- ── Extensions ────────────────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── Tenants ───────────────────────────────────────────────────────────────
CREATE TABLE tenants (
  id          uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  name        text NOT NULL,
  slug        text NOT NULL UNIQUE,
  created_at  timestamptz NOT NULL DEFAULT now()
);

-- ── Users ─────────────────────────────────────────────────────────────────
CREATE TABLE users (
  id          uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id   uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  auth0_id    text NOT NULL UNIQUE,
  role        text NOT NULL DEFAULT 'member' CHECK (role IN ('admin', 'member')),
  created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_users_tenant_id ON users(tenant_id);

-- ── Agents ────────────────────────────────────────────────────────────────
CREATE TABLE agents (
  id            uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  name          text NOT NULL DEFAULT 'PM Agent',
  team_profile  jsonb NOT NULL DEFAULT '{}',  -- learned team context from onboarding
  created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_agents_tenant_id ON agents(tenant_id);

-- ── Workflow Configs ──────────────────────────────────────────────────────
-- Per-workflow autonomy mode (watch | draft | act).
-- Replaces the old global L1/L2/L3 trust level model.
-- The permission check is workflow_configs.mode, not a global trust_level.
CREATE TABLE workflow_configs (
  id              uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id       uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  agent_id        uuid NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
  workflow_name   text NOT NULL,  -- sprint_status | standup_summary | stakeholder_update | ...
  mode            text NOT NULL DEFAULT 'draft' CHECK (mode IN ('watch', 'draft', 'act')),
  admin_max_mode  text NOT NULL DEFAULT 'draft' CHECK (admin_max_mode IN ('watch', 'draft', 'act')),
  config          jsonb NOT NULL DEFAULT '{}',  -- schedule, target_channel, template_id, etc.
  updated_by      uuid REFERENCES users(id),
  updated_at      timestamptz NOT NULL DEFAULT now(),
  UNIQUE (agent_id, workflow_name)
);

CREATE INDEX idx_workflow_configs_tenant_id ON workflow_configs(tenant_id);
CREATE INDEX idx_workflow_configs_agent_id ON workflow_configs(agent_id);

-- ── Conversations ─────────────────────────────────────────────────────────
CREATE TABLE conversations (
  id          uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id   uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  agent_id    uuid NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
  created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_conversations_tenant_id ON conversations(tenant_id);
CREATE INDEX idx_conversations_agent_id ON conversations(agent_id);

-- ── Messages ──────────────────────────────────────────────────────────────
CREATE TABLE messages (
  id                uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id         uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,  -- denormalized for RLS
  conversation_id   uuid NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
  role              text NOT NULL CHECK (role IN ('user', 'assistant')),
  content           text NOT NULL,
  sources           jsonb NOT NULL DEFAULT '[]',  -- [{tool, id, url, timestamp}]
  token_usage       jsonb NOT NULL DEFAULT '{}',  -- {input, output, model}
  accuracy_flag     text CHECK (accuracy_flag IN ('wrong_status', 'missing_context', 'wrong_interpretation', 'outdated_info', 'other')),
  created_at        timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX idx_messages_tenant_id ON messages(tenant_id);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);

-- ── Integration Configs ───────────────────────────────────────────────────
CREATE TABLE integration_configs (
  id            uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  provider      text NOT NULL CHECK (provider IN ('jira', 'slack', 'notion', 'github')),
  workspace_id  text,
  config        jsonb NOT NULL DEFAULT '{}',  -- {base_url, channel_ids, project_keys, ...}
  secret_ref    text,  -- Doppler/Secret Manager path — tokens are NEVER stored here
  status        text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'active', 'expired', 'error')),
  created_at    timestamptz NOT NULL DEFAULT now(),
  UNIQUE (tenant_id, provider)
);

CREATE INDEX idx_integration_configs_tenant_id ON integration_configs(tenant_id);

-- ── Token Usage ───────────────────────────────────────────────────────────
CREATE TABLE token_usage_daily (
  id            uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  tenant_id     uuid NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
  date          date NOT NULL DEFAULT CURRENT_DATE,
  tokens_used   int NOT NULL DEFAULT 0,
  budget_limit  int NOT NULL DEFAULT 100000,
  UNIQUE (tenant_id, date)
);

CREATE INDEX idx_token_usage_daily_tenant_date ON token_usage_daily(tenant_id, date);

-- ── Row-Level Security ────────────────────────────────────────────────────
-- Every tenant-scoped table enforces RLS using the JWT-derived tenant_id
-- set by the FastAPI middleware via set_config('app.current_tenant_id', ...).
-- tenant_id is NEVER accepted from the request body.

ALTER TABLE tenants             ENABLE ROW LEVEL SECURITY;
ALTER TABLE users               ENABLE ROW LEVEL SECURITY;
ALTER TABLE agents              ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflow_configs    ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations       ENABLE ROW LEVEL SECURITY;
ALTER TABLE messages            ENABLE ROW LEVEL SECURITY;
ALTER TABLE integration_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE token_usage_daily   ENABLE ROW LEVEL SECURITY;

-- Tenant isolation policy (applied to all tenant-scoped tables)
CREATE POLICY tenant_isolation ON tenants
  USING (id = (current_setting('app.current_tenant_id', true))::uuid);

CREATE POLICY tenant_isolation ON users
  USING (tenant_id = (current_setting('app.current_tenant_id', true))::uuid);

CREATE POLICY tenant_isolation ON agents
  USING (tenant_id = (current_setting('app.current_tenant_id', true))::uuid);

CREATE POLICY tenant_isolation ON workflow_configs
  USING (tenant_id = (current_setting('app.current_tenant_id', true))::uuid);

CREATE POLICY tenant_isolation ON conversations
  USING (tenant_id = (current_setting('app.current_tenant_id', true))::uuid);

CREATE POLICY tenant_isolation ON messages
  USING (tenant_id = (current_setting('app.current_tenant_id', true))::uuid);

CREATE POLICY tenant_isolation ON integration_configs
  USING (tenant_id = (current_setting('app.current_tenant_id', true))::uuid);

CREATE POLICY tenant_isolation ON token_usage_daily
  USING (tenant_id = (current_setting('app.current_tenant_id', true))::uuid);
