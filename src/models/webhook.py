"""
Webhook models for iMessage integration.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import time


class WebhookRequest(BaseModel):
    """Incoming webhook request from iMessage."""

    # Message details
    message_id: str = Field(..., description="Unique identifier for the message")
    conversation_id: str = Field(..., description="ID of the conversation")
    sender_phone: str = Field(..., description="Phone number of the sender")
    sender_name: Optional[str] = Field(None, description="Name of the sender")
    content: str = Field(..., description="Content of the message")
    message_type: str = Field("text", description="Type of the message")
    timestamp: datetime = Field(..., description="When the message was sent")

    # iMessage specific fields
    imessage_id: Optional[str] = Field(None, description="iMessage specific identifier")
    group_id: Optional[str] = Field(
        None, description="Group chat identifier if applicable"
    )
    is_group_chat: bool = Field(False, description="Whether this is a group chat")

    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional message metadata"
    )
    attachments: Optional[list] = Field(None, description="List of attachments")

    # Security
    signature: Optional[str] = Field(
        None, description="Webhook signature for verification"
    )
    timestamp_header: Optional[str] = Field(
        None, description="Timestamp header for verification"
    )

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class WebhookResponse(BaseModel):
    """Response to webhook requests."""

    success: bool = Field(
        ..., description="Whether the webhook was processed successfully"
    )
    message: str = Field(..., description="Response message")
    conversation_id: str = Field(..., description="ID of the conversation")

    # Response details
    response_content: Optional[str] = Field(
        None, description="Content of the AI agent's response"
    )
    response_timestamp: Optional[float] = Field(
        None, description="When the response was generated (timestamp)"
    )

    # Processing metadata
    processing_time: Optional[float] = Field(
        None, description="Time taken to process the webhook"
    )
    agent_used: Optional[str] = Field(
        None, description="Which agent processed the request"
    )

    # Error handling
    error_code: Optional[str] = Field(
        None, description="Error code if processing failed"
    )
    error_details: Optional[str] = Field(None, description="Detailed error information")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
