"""
Conversation and message data models.
"""

from datetime import datetime
import time
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class MessageType(str, Enum):
    """Types of messages in a conversation."""

    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FILE = "file"
    LOCATION = "location"


class ParticipantRole(str, Enum):
    """Roles of participants in a conversation."""

    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"


class Participant(BaseModel):
    """A participant in a conversation."""

    id: str = Field(..., description="Unique identifier for the participant")
    phone_number: str = Field(..., description="Phone number of the participant")
    name: Optional[str] = Field(None, description="Display name of the participant")
    role: ParticipantRole = Field(..., description="Role of the participant")
    is_active: bool = Field(
        True, description="Whether the participant is active in the conversation"
    )


class Message(BaseModel):
    """A single message in a conversation."""

    id: str = Field(..., description="Unique identifier for the message")
    conversation_id: str = Field(
        ..., description="ID of the conversation this message belongs to"
    )
    sender_id: str = Field(..., description="ID of the message sender")
    content: str = Field(..., description="Content of the message")
    message_type: MessageType = Field(
        MessageType.TEXT, description="Type of the message"
    )
    timestamp: datetime = Field(
        default_factory=datetime.now, description="When the message was sent"
    )
    metadata: Optional[dict] = Field(
        None, description="Additional metadata for the message"
    )
    is_read: bool = Field(False, description="Whether the message has been read")
    is_delivered: bool = Field(
        False, description="Whether the message has been delivered"
    )


class ConversationStatus(str, Enum):
    """Status of a conversation."""

    ACTIVE = "active"
    PAUSED = "paused"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Conversation(BaseModel):
    """A conversation between participants."""

    id: str = Field(..., description="Unique identifier for the conversation")
    participants: List[Participant] = Field(
        ..., description="List of participants in the conversation"
    )
    messages: List[Message] = Field(
        default_factory=list, description="List of messages in the conversation"
    )
    status: ConversationStatus = Field(
        ConversationStatus.ACTIVE, description="Current status of the conversation"
    )
    created_at: datetime = Field(
        default_factory=datetime.now, description="When the conversation was created"
    )
    updated_at: datetime = Field(
        default_factory=datetime.now,
        description="When the conversation was last updated",
    )
    metadata: Optional[dict] = Field(
        None, description="Additional metadata for the conversation"
    )
    tags: List[str] = Field(
        default_factory=list, description="Tags associated with the conversation"
    )

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
