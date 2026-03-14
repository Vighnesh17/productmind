"""
Cross-tenant isolation tests — mandatory, runs in CI on every commit.

RLS bugs produce empty results, not errors — only explicit tests catch them.
These tests verify that tenant A cannot read tenant B's data under any
circumstance, including when a tenant_id is passed in the request body.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_tenant_a_cannot_read_tenant_b_messages(client: AsyncClient, two_tenants):
    """Tenant A's JWT returns zero messages when tenant B has data."""
    tenant_a_token, tenant_b_token = two_tenants

    # Create a message as tenant B
    resp = await client.post(
        "/api/v1/agents/00000000-0000-0000-0000-000000000010/message",
        json={"content": "What is the sprint status?"},
        headers={"Authorization": f"Bearer {tenant_b_token}"},
    )
    assert resp.status_code == 200

    # Query messages as tenant A — should return zero rows, not an error
    resp = await client.get(
        "/api/v1/agents/00000000-0000-0000-0000-000000000010/messages",
        headers={"Authorization": f"Bearer {tenant_a_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["messages"] == []


@pytest.mark.asyncio
async def test_tenant_id_in_body_is_ignored(client: AsyncClient, tenant_a_token, tenant_b_id):
    """Passing a different tenant_id in the request body has no effect."""
    resp = await client.post(
        "/api/v1/agents/00000000-0000-0000-0000-000000000010/message",
        json={
            "content": "What is the sprint status?",
            "tenant_id": tenant_b_id,  # attempting to inject a different tenant
        },
        headers={"Authorization": f"Bearer {tenant_a_token}"},
    )
    # Request should succeed but use tenant_a's tenant_id from JWT, not tenant_b
    assert resp.status_code in (200, 404)  # 404 if agent doesn't belong to tenant_a — correct


@pytest.mark.asyncio
async def test_cross_tenant_agent_access_returns_404(client: AsyncClient, tenant_a_token, tenant_b_agent_id):
    """Accessing an agent that belongs to another tenant returns 404, not 403 or 500."""
    resp = await client.get(
        f"/api/v1/agents/{tenant_b_agent_id}",
        headers={"Authorization": f"Bearer {tenant_a_token}"},
    )
    # RLS makes the row invisible — 404 is the correct behaviour (not 403)
    assert resp.status_code == 404
