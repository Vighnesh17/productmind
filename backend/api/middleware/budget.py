"""
Per-tenant token budget enforcement.

Checks daily token usage against the tenant's budget limit before
allowing any LLM call. Uses Upstash Redis as the fast-path counter.

Fail-open: if Redis is unavailable, the request is allowed through
and a metric is logged. Revenue > budget enforcement during an outage.
"""

import datetime

import structlog
from fastapi import HTTPException, Request
from upstash_redis import Redis

from backend.config import settings

log = structlog.get_logger()


def _budget_key(tenant_id: str) -> str:
    today = datetime.date.today().isoformat()
    return f"budget:{tenant_id}:{today}"


async def check_token_budget(request: Request) -> None:
    """Raise 429 if the tenant has exceeded their daily token budget."""
    tenant_id = request.state.tenant_id

    try:
        redis = Redis(url=settings.upstash_redis_url, token=settings.upstash_redis_token)
        key = _budget_key(tenant_id)
        used = await redis.get(key)
        used = int(used) if used else 0

        # Default budget: 100,000 tokens/day. Configurable per tenant in DB.
        budget = 100_000

        if used >= budget:
            log.warning("budget.exceeded", tenant_id=tenant_id, used=used, budget=budget)
            raise HTTPException(
                status_code=429,
                detail=f"Daily AI budget reached ({used:,} / {budget:,} tokens). Resets at midnight.",
            )

        log.debug("budget.ok", tenant_id=tenant_id, used=used, budget=budget)

    except HTTPException:
        raise
    except Exception as e:
        # Fail open — log and allow the request through.
        log.error("budget.check_unavailable", tenant_id=tenant_id, error=str(e))
