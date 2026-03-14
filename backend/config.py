from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Anthropic
    anthropic_api_key: str

    # Supabase
    supabase_url: str
    supabase_service_role_key: str  # backend only — never expose to browser

    # Database (direct Postgres for SQLAlchemy)
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"

    # Pinecone
    pinecone_api_key: str
    pinecone_index: str = "productmind-memory"

    # Upstash Redis
    upstash_redis_url: str
    upstash_redis_token: str

    # Auth0
    auth0_domain: str
    auth0_client_id: str
    auth0_client_secret: str
    auth0_audience: str

    # Inngest
    inngest_event_key: str = ""
    inngest_signing_key: str = ""

    # Jira OAuth
    jira_client_id: str = ""
    jira_client_secret: str = ""
    jira_redirect_uri: str = "http://localhost:8000/api/v1/integrations/jira/callback"

    # Slack OAuth
    slack_client_id: str = ""
    slack_client_secret: str = ""
    slack_redirect_uri: str = "http://localhost:8000/api/v1/integrations/slack/callback"

    # App
    app_env: str = "local"
    app_port: int = 8000
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()  # type: ignore[call-arg]
