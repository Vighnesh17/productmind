import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import agents, integrations, stream

log = structlog.get_logger()


def create_app() -> FastAPI:
    app = FastAPI(
        title="ProductMind AI",
        version="0.1.0",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],  # frontend dev server
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(agents.router, prefix="/api/v1")
    app.include_router(integrations.router, prefix="/api/v1")
    app.include_router(stream.router, prefix="/api/v1")

    @app.get("/api/v1/health")
    async def health() -> dict:
        return {"status": "ok", "version": "0.1.0"}

    return app


app = create_app()
