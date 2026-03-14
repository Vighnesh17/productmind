"""
Row-Level Security context injection.

Every request sets the Postgres session variable `app.current_tenant_id`
before any query runs. Supabase RLS policies use this to scope all reads
and writes to the correct tenant automatically.

IMPORTANT: tenant_id is ALWAYS sourced from the validated JWT, never from
the request body or path parameters.

Usage:
    async with AsyncSessionLocal() as session:
        await set_tenant_context(session, request.state.tenant_id)
        # all queries in this session are now scoped to tenant_id
"""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def set_tenant_context(session: AsyncSession, tenant_id: str) -> None:
    """Set the Postgres RLS context for the current session."""
    await session.execute(
        text("SELECT set_config('app.current_tenant_id', :tid, true)"),
        {"tid": str(tenant_id)},
    )
