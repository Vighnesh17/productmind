"""
Auth0 JWT validation middleware.

Extracts and validates the JWT from the Authorization header.
Sets request.state.tenant_id and request.state.user_id from JWT claims.

tenant_id is ALWAYS sourced from the JWT — never from the request body.
"""

import structlog
from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from backend.config import settings

log = structlog.get_logger()
security = HTTPBearer()

ALGORITHMS = ["RS256"]


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = security,
) -> dict:
    """Validate JWT and return claims. Raises 401 on failure."""
    token = credentials.credentials
    try:
        # In production: fetch JWKS from Auth0 and verify signature.
        # For local dev with a test token, you can set APP_ENV=test to skip.
        if settings.app_env == "test":
            # Accept unsigned test tokens in local/test mode only.
            payload = jwt.get_unverified_claims(token)
        else:
            jwks_url = f"https://{settings.auth0_domain}/.well-known/jwks.json"
            payload = jwt.decode(
                token,
                jwks_url,
                algorithms=ALGORITHMS,
                audience=settings.auth0_audience,
            )

        tenant_id = payload.get("https://productmind.ai/tenant_id")
        user_id = payload.get("sub")

        if not tenant_id:
            raise HTTPException(status_code=401, detail="Missing tenant_id in token")

        request.state.tenant_id = tenant_id
        request.state.user_id = user_id

        log.debug("auth.validated", user_id=user_id, tenant_id=tenant_id)
        return payload

    except JWTError as e:
        log.warning("auth.invalid_token", error=str(e))
        raise HTTPException(status_code=401, detail="Invalid token") from e
