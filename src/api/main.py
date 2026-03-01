"""
Main API Server for Personal AI Employee System
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Database imports for dependency injection
from sqlalchemy.orm import Session
from src.services.database import SessionLocal, init_db

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="ELYX - Personal AI Employee",
    description="API for autonomous AI employee system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["system"])
async def health_check():
    """Health check endpoint for the API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "ELYX - Personal AI Employee",
        "version": "1.0.0"
    }


@app.get("/", tags=["system"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to ELYX - Personal AI Employee API",
        "description": "Autonomous AI employee system with Gmail, WhatsApp, Social Media, and Odoo integration",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


# Include routers for different modules
from .routes.dashboard import dashboard_router
from .routes.tasks import task_router
from .routes.approval import approval_router
from .routes.ai import ai_router
from .routes.enterprise import enterprise_router
from .routes.communication import communication_router

app.include_router(dashboard_router, prefix="/api", tags=["dashboard"])
app.include_router(task_router, prefix="/api", tags=["tasks"])
app.include_router(approval_router, prefix="/api", tags=["approvals"])
app.include_router(ai_router, prefix="/api", tags=["ai"])
app.include_router(enterprise_router, prefix="/api", tags=["enterprise"])
app.include_router(communication_router, prefix="/api", tags=["communication"])

try:
    from .routes.users import router as users_router
    app.include_router(users_router, prefix="/api", tags=["users"])
except ImportError as e:
    print(f"Warning: Could not import Users routes: {e}")

try:
    from .routes.settings import router as settings_router
    app.include_router(settings_router, prefix="/api", tags=["settings"])
except ImportError as e:
    print(f"Warning: Could not import Settings routes: {e}")

# Error handling
@app.exception_handler(404)
async def custom_http_exception_handler(request, exc):
    """Custom 404 handler"""
    return {
        "detail": "Endpoint not found",
        "status_code": 404,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.exception_handler(500)
async def custom_server_error_exception_handler(request, exc):
    """Custom 500 handler"""
    return {
        "detail": "Internal server error",
        "status_code": 500,
        "timestamp": datetime.utcnow().isoformat()
    }

# Utility functions
def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_task_service(db: Session = Depends(get_db)):
    """Get task service instance"""
    return TaskService(db)

def get_preference_service(db: Session = Depends(get_db)):
    """Get preference service instance"""
    return UserPreferenceService(db)

def get_interaction_service(db: Session = Depends(get_db)):
    """Get interaction service instance"""
    return InteractionService(db)

# Initialize the database when the module is loaded
if __name__ == "__main__":
    import uvicorn

    # Get port from environment or default to 8000
    port = int(os.getenv("PORT", 8000))

    logger.info(f"Starting ELYX Personal AI Employee API on port {port}")

    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,  # Disable in production
        log_level="info"
    )
