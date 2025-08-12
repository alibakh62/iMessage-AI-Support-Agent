"""
Conversation management chain for maintaining context and flow.
"""

from typing import Dict, Any, List
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatAnthropic
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import time

from ..config import get_settings
from ..models.conversation import Conversation, Message, ConversationStatus


class ConversationAnalysis(BaseModel):
    """Analysis of conversation context and flow."""

    sentiment: str = Field(..., description="Overall sentiment of the conversation")
    topic: str = Field(..., description="Main topic being discussed")
    urgency: str = Field(..., description="Urgency level: low, medium, high, critical")
    customer_satisfaction: str = Field(..., description="Customer satisfaction level")
    next_best_action: str = Field(..., description="Recommended next action")
    should_continue: bool = Field(
        True, description="Whether conversation should continue"
    )
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")


class ConversationChain:
    """Chain for managing conversation context and flow."""

    def __init__(self):
        self.settings = get_settings()
        self.llm = self._initialize_llm()
        self.output_parser = PydanticOutputParser(pydantic_object=ConversationAnalysis)
        self.prompt = self._create_prompt()
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def _initialize_llm(self):
        """Initialize the language model."""
        if self.settings.anthropic_api_key:
            return ChatAnthropic(
                model="claude-3-sonnet-20240229", temperature=0.3, max_tokens=500
            )
        else:
            return ChatOpenAI(model="gpt-4", temperature=0.3, max_tokens=500)

    def _create_prompt(self):
        """Create the prompt template for conversation analysis."""
        template = """Analyze the following conversation and provide insights about the context, sentiment, and recommended actions.

Conversation Messages:
{messages}

Customer Information:
- Phone: {customer_phone}
- Conversation Duration: {duration}
- Message Count: {message_count}

Instructions:
1. Analyze the sentiment and topic of the conversation
2. Assess urgency and customer satisfaction
3. Recommend the next best action
4. Determine if conversation should continue or be escalated
5. Add relevant tags for categorization

{format_instructions}

Analysis:"""

        return PromptTemplate(
            template=template,
            input_variables=["messages", "customer_phone", "duration", "message_count"],
            partial_variables={
                "format_instructions": self.output_parser.get_format_instructions()
            },
        )

    async def analyze_conversation(
        self, conversation: Conversation
    ) -> ConversationAnalysis:
        """Analyze a conversation to understand context and flow."""
        try:
            # Format messages for analysis
            messages_text = self._format_messages(conversation.messages)

            # Calculate conversation duration
            duration = self._calculate_duration(
                conversation.created_at, conversation.updated_at
            )

            # Get customer phone number
            customer_phone = self._get_customer_phone(conversation.participants)

            # Generate analysis
            result = await self.chain.ainvoke(
                {
                    "messages": messages_text,
                    "customer_phone": customer_phone,
                    "duration": duration,
                    "message_count": len(conversation.messages),
                }
            )

            # Parse the response
            analysis = self.output_parser.parse(result["text"])

            return analysis

        except Exception as e:
            # Return default analysis on error
            return ConversationAnalysis(
                sentiment="neutral",
                topic="general inquiry",
                urgency="medium",
                customer_satisfaction="unknown",
                next_best_action="continue conversation",
                should_continue=True,
                tags=["error", "fallback"],
            )

    def _format_messages(self, messages: List[Message]) -> str:
        """Format messages for analysis."""
        if not messages:
            return "No messages in conversation."

        formatted = []
        for msg in messages:
            role = "Customer" if msg.sender_id != "agent" else "Agent"
            formatted.append(f"{role}: {msg.content}")

        return "\n".join(formatted)

    def _calculate_duration(self, created_at, updated_at) -> str:
        """Calculate conversation duration."""
        try:
            duration = updated_at - created_at
            if duration.days > 0:
                return f"{duration.days} days"
            elif duration.seconds > 3600:
                hours = duration.seconds // 3600
                return f"{hours} hours"
            elif duration.seconds > 60:
                minutes = duration.seconds // 60
                return f"{minutes} minutes"
            else:
                return f"{duration.seconds} seconds"
        except:
            return "unknown"

    def _get_customer_phone(self, participants: List) -> str:
        """Extract customer phone number from participants."""
        for participant in participants:
            if participant.role.value == "user":
                return participant.phone_number
        return "unknown"

    def should_escalate_conversation(self, analysis: ConversationAnalysis) -> bool:
        """Determine if conversation should be escalated based on analysis."""
        escalation_triggers = [
            analysis.urgency == "critical",
            analysis.customer_satisfaction == "very_dissatisfied",
            analysis.sentiment == "very_negative",
            not analysis.should_continue,
        ]

        return any(escalation_triggers)

    def get_conversation_tags(self, analysis: ConversationAnalysis) -> List[str]:
        """Get tags for the conversation based on analysis."""
        tags = analysis.tags.copy()

        # Add sentiment-based tags
        if analysis.sentiment in ["positive", "very_positive"]:
            tags.append("satisfied_customer")
        elif analysis.sentiment in ["negative", "very_negative"]:
            tags.append("dissatisfied_customer")

        # Add urgency-based tags
        if analysis.urgency == "critical":
            tags.append("urgent")
        elif analysis.urgency == "high":
            tags.append("priority")

        # Add topic-based tags
        tags.append(f"topic_{analysis.topic.lower().replace(' ', '_')}")

        return list(set(tags))  # Remove duplicates
