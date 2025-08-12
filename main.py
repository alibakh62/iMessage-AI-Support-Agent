"""
Main application entry point for the iMessage AI Support Agent.
"""

import asyncio
import logging
import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from src.config import get_settings
from src.agents import SupportAgent
from src.models.webhook import WebhookRequest, WebhookResponse
from src.models.agent import AgentResponse


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Global agent instance
support_agent: SupportAgent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global support_agent

    # Startup
    logger.info("Starting iMessage AI Support Agent...")

    try:
        # Initialize the support agent
        support_agent = SupportAgent()
        logger.info("Support agent initialized successfully")

        # Load configuration
        settings = get_settings()
        logger.info(f"Configuration loaded: {settings.environment} environment")

    except Exception as e:
        logger.error(f"Failed to initialize support agent: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down iMessage AI Support Agent...")


# Create FastAPI app
app = FastAPI(
    title="iMessage AI Support Agent",
    description="AI-powered customer support agent for iMessage integration",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "iMessage AI Support Agent",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "agent_initialized": support_agent is not None,
        "timestamp": asyncio.get_event_loop().time(),
    }


@app.post("/webhook/imessage", response_model=WebhookResponse)
async def imessage_webhook(request: WebhookRequest, settings=Depends(get_settings)):
    """
    Webhook endpoint for receiving iMessage messages.

    This endpoint receives messages from iMessage and processes them
    through the AI support agent.
    """

    if not support_agent:
        raise HTTPException(status_code=503, detail="Support agent not initialized")

    try:
        logger.info(f"Processing webhook for conversation {request.conversation_id}")

        # Process the message through the support agent
        response = await support_agent.process_message(
            message_content=request.content,
            conversation_id=request.conversation_id,
            sender_phone=request.sender_phone,
            sender_name=request.sender_name,
        )

        # Create webhook response
        webhook_response = WebhookResponse(
            success=True,
            message="Message processed successfully",
            conversation_id=request.conversation_id,
            response_content=response.content,
            response_timestamp=response.timestamp,
            processing_time=response.response_time,
            agent_used="support_agent",
        )

        logger.info(
            f"Webhook processed successfully for conversation {request.conversation_id}"
        )
        return webhook_response

    except Exception as e:
        logger.error(f"Error processing webhook: {e}")

        # Return error response
        return WebhookResponse(
            success=False,
            message="Failed to process message",
            conversation_id=request.conversation_id,
            error_code="PROCESSING_ERROR",
            error_details=str(e),
        )


@app.post("/chat/process")
async def process_chat_message(
    message: str, conversation_id: str, sender_phone: str = None
):
    """
    Direct chat processing endpoint for testing and direct API usage.

    This endpoint allows direct processing of chat messages without
    going through the iMessage webhook.
    """

    if not support_agent:
        raise HTTPException(status_code=503, detail="Support agent not initialized")

    try:
        logger.info(
            f"Processing direct chat message for conversation {conversation_id}"
        )

        # Process the message
        response = await support_agent.process_message(
            message_content=message,
            conversation_id=conversation_id,
            sender_phone=sender_phone or "unknown",
        )

        return {
            "success": True,
            "response": response.content,
            "conversation_id": conversation_id,
            "confidence_score": response.confidence_score,
            "response_time": response.response_time,
            "should_escalate": response.should_escalate,
            "escalation_reason": response.escalation_reason,
            "metadata": response.metadata,
        }

    except Exception as e:
        logger.error(f"Error processing chat message: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to process message: {str(e)}"
        )


@app.get("/conversations/{conversation_id}/status")
async def get_conversation_status(conversation_id: str):
    """
    Get the status of a specific conversation.

    This endpoint provides information about the current state
    of a conversation, including any pending escalations.
    """

    if not support_agent:
        raise HTTPException(status_code=503, detail="Support agent not initialized")

    try:
        # In a real implementation, this would query the database
        # For now, return a mock response
        return {
            "conversation_id": conversation_id,
            "status": "active",
            "last_message_time": asyncio.get_event_loop().time(),
            "escalation_status": "none",
            "agent_assigned": "ai_support_agent",
        }

    except Exception as e:
        logger.error(f"Error getting conversation status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@app.get("/metrics")
async def get_metrics():
    """
    Get system metrics and performance data.

    This endpoint provides insights into the agent's performance
    and system health.
    """

    if not support_agent:
        raise HTTPException(status_code=503, detail="Support agent not initialized")

    try:
        # In a real implementation, this would collect actual metrics
        # For now, return mock data
        return {
            "total_conversations": 0,
            "active_conversations": 0,
            "escalations_today": 0,
            "average_response_time": 0.0,
            "success_rate": 100.0,
            "system_uptime": asyncio.get_event_loop().time(),
            "agent_status": "healthy",
        }

    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


if __name__ == "__main__":
    # Get settings
    settings = get_settings()

    # Run the application
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
