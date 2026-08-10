import os 
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from app.platform.router import router
from app.api.v1.opportunities import router as opportunities_router
from app.api.v1.auth import router as auth_router
from app.api.v1.claims import router as claims_router
from app.api.v1.organizations import router as org_router
from app.core.config import settings
from app.core.db import init_db

from fastapi.middleware.cors import CORSMiddleware

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
    )
    
    # Configure CORS for frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)
    app.include_router(opportunities_router)
    app.include_router(auth_router)
    app.include_router(claims_router)
    app.include_router(org_router)
    
    @app.on_event("startup")
    async def startup():
        await init_db()
    
    @app.get("/")
    def fallback():
        return RedirectResponse(url="/docs")
    
    return app

app = create_app()