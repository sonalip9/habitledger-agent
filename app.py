"""
FastAPI server for HabitLedger agent deployment.

Provides REST API endpoints for chat interactions with the behavioral money coach.
Designed for deployment on Google Cloud Run or similar container platforms.
"""

import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from src.config import load_env, setup_logging
from src.habitledger_adk.agent import habitledger_coach_tool
from src.habitledger_adk.runner import (
    create_runner,
    load_memory_from_session,
    save_memory_to_session,
)

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

# Load environment variables
load_env()

# Create FastAPI app
app = FastAPI(
    title="HabitLedger Agent API",
    description="AI-powered behavioral money coach using Google ADK",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    user_id: str = Field(..., description="Unique user identifier")
    message: str = Field(..., description="User's message about financial habits")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    user_id: str
    response: str
    session_id: str
    status: str = "success"


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "HabitLedger Agent API",
        "version": "0.1.0",
        "status": "running",
        "endpoints": {
            "chat": "/chat",
            "health": "/health",
            "docs": "/docs",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run."""
    return {
        "status": "healthy",
        "service": "habitledger-agent",
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process user message and return coaching response.

    This endpoint:
    1. Creates or loads user session
    2. Processes message through HabitLedger agent
    3. Returns personalized coaching response
    4. Updates session state
    """
    try:
        logger.info(
            "Chat request received",
            extra={
                "user_id": request.user_id,
                "message_length": len(request.message),
            },
        )

        # Create runner with user session
        _client, _session_service, session, behaviour_db = await create_runner(
            user_id=request.user_id
        )

        # Load user memory from session
        memory = load_memory_from_session(session)
        if not memory:
            raise HTTPException(status_code=500, detail="Failed to load user memory")

        # Process message through coaching tool
        result = habitledger_coach_tool(
            user_input=request.message,
            memory=memory,
            behaviour_db=behaviour_db,
        )

        # Save updated memory back to session
        save_memory_to_session(session, memory)

        logger.info(
            "Chat request processed",
            extra={
                "user_id": request.user_id,
                "session_id": session.id,
                "response_length": len(result.get("response", "")),
            },
        )

        return ChatResponse(
            user_id=request.user_id,
            response=result.get("response", "Error generating response"),
            session_id=session.id,
            status=result.get("status", "success"),
        )

    except Exception as e:
        logger.error(
            "Chat request failed",
            extra={
                "user_id": request.user_id,
                "error": str(e),
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=500, detail=f"Error processing request: {str(e)}"
        ) from e


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8080"))
    uvicorn.run(app, host="0.0.0.0", port=port)
