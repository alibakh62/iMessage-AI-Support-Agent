"""
Main support chain for generating customer service responses.
"""

from typing import Dict, Any, List
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatAnthropic
from langchain.schema import BaseOutputParser
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import json
import time

from ..config import get_settings
from ..models.agent import AgentResponse


class SupportResponse(BaseModel):
    """Structured response from the support chain."""

    response: str = Field(..., description="The main response to the customer")
    confidence: float = Field(..., description="Confidence score (0-1)")
    should_escalate: bool = Field(False, description="Whether to escalate to human")
    escalation_reason: str = Field("", description="Reason for escalation if needed")
    suggested_actions: List[str] = Field(
        default_factory=list, description="Suggested next actions"
    )
    tags: List[str] = Field(
        default_factory=list, description="Tags for the conversation"
    )


class SupportChain:
    """Main support chain for customer service responses."""

    def __init__(self):
        self.settings = get_settings()
        self.llm = self._initialize_llm()
        self.output_parser = PydanticOutputParser(pydantic_object=SupportResponse)
        self.prompt = self._create_prompt()
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def _initialize_llm(self):
        """Initialize the language model based on available API keys."""
        if self.settings.anthropic_api_key:
            return ChatAnthropic(
                model="claude-3-sonnet-20240229", temperature=0.7, max_tokens=1000
            )
        else:
            return ChatOpenAI(model="gpt-4", temperature=0.7, max_tokens=1000)

    def _create_prompt(self):
        """Create the prompt template for support responses."""
        template = """You are an AI customer support agent for a technology company. Your role is to help customers with their inquiries in a helpful, professional, and empathetic manner.

Customer Message: {customer_message}

Conversation History:
{conversation_history}

Company Information:
- Company: TechCorp Solutions
- Products: Software solutions, cloud services, technical support
- Support Hours: 24/7
- Escalation Policy: Escalate complex technical issues, billing disputes, or complaints

Instructions:
1. Provide a helpful and accurate response to the customer
2. If the issue is complex or requires human intervention, set should_escalate to true
3. Suggest relevant next actions when appropriate
4. Add relevant tags to categorize the conversation
5. Be confident but honest about your limitations

{format_instructions}

Response:"""

        return PromptTemplate(
            template=template,
            input_variables=["customer_message", "conversation_history"],
            partial_variables={
                "format_instructions": self.output_parser.get_format_instructions()
            },
        )

    async def generate_response(
        self, customer_message: str, conversation_history: List[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Generate a support response for the customer message."""
        start_time = time.time()

        try:
            # Format conversation history
            history_text = self._format_conversation_history(conversation_history or [])

            # Generate response
            result = await self.chain.ainvoke(
                {
                    "customer_message": customer_message,
                    "conversation_history": history_text,
                }
            )

            # Parse the response
            parsed_response = self.output_parser.parse(result["text"])

            # Calculate response time
            response_time = time.time() - start_time

            # Create agent response
            agent_response = AgentResponse(
                content=parsed_response.response,
                conversation_id="",  # Will be set by caller
                confidence_score=parsed_response.confidence,
                response_time=response_time,
                should_escalate=parsed_response.should_escalate,
                escalation_reason=parsed_response.escalation_reason,
                metadata={
                    "suggested_actions": parsed_response.suggested_actions,
                    "tags": parsed_response.tags,
                    "ai_model": (
                        self.llm.model_name
                        if hasattr(self.llm, "model_name")
                        else "unknown"
                    ),
                },
            )

            return agent_response

        except Exception as e:
            # Handle errors gracefully
            response_time = time.time() - start_time
            return AgentResponse(
                content="I apologize, but I'm experiencing technical difficulties. Please try again or contact human support.",
                conversation_id="",
                confidence_score=0.0,
                response_time=response_time,
                should_escalate=True,
                escalation_reason=f"Error in AI response generation: {str(e)}",
                error_details=str(e),
            )

    def _format_conversation_history(self, history: List[Dict[str, Any]]) -> str:
        """Format conversation history for the prompt."""
        if not history:
            return "No previous messages in this conversation."

        formatted = []
        for msg in history[-5:]:  # Last 5 messages for context
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            formatted.append(f"{role}: {content}")

        return "\n".join(formatted)
