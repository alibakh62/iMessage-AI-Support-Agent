"""
Escalation chain for handling complex cases that require human intervention.
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
from ..models.conversation import Conversation, Message


class EscalationAnalysis(BaseModel):
    """Analysis for escalation decisions."""

    escalation_level: str = Field(
        ..., description="Escalation level: low, medium, high, urgent"
    )
    escalation_reason: str = Field(..., description="Detailed reason for escalation")
    priority_score: int = Field(..., description="Priority score 1-10")
    required_skills: List[str] = Field(
        default_factory=list, description="Skills required to handle this case"
    )
    estimated_resolution_time: str = Field(..., description="Estimated time to resolve")
    customer_impact: str = Field(
        ..., description="Impact on customer: low, medium, high, critical"
    )
    suggested_agent: str = Field(
        ..., description="Suggested agent type to handle this case"
    )
    immediate_actions: List[str] = Field(
        default_factory=list, description="Immediate actions to take"
    )


class EscalationChain:
    """Chain for analyzing and managing escalations."""

    def __init__(self):
        self.settings = get_settings()
        self.llm = self._initialize_llm()
        self.output_parser = PydanticOutputParser(pydantic_object=EscalationAnalysis)
        self.prompt = self._create_prompt()
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def _initialize_llm(self):
        """Initialize the language model."""
        if self.settings.anthropic_api_key:
            return ChatAnthropic(
                model="claude-3-sonnet-20240229", temperature=0.2, max_tokens=800
            )
        else:
            return ChatOpenAI(model="gpt-4", temperature=0.2, max_tokens=800)

    def _create_prompt(self):
        """Create the prompt template for escalation analysis."""
        template = """You are an escalation specialist analyzing a customer support case that requires human intervention.

Case Information:
- Customer Message: {customer_message}
- Conversation History: {conversation_history}
- Escalation Trigger: {escalation_trigger}
- Customer Phone: {customer_phone}

Instructions:
1. Analyze the escalation reason and determine the appropriate level
2. Assess priority and customer impact
3. Identify required skills and suggest agent type
4. Estimate resolution time
5. Recommend immediate actions
6. Provide detailed escalation reasoning

{format_instructions}

Escalation Analysis:"""

        return PromptTemplate(
            template=template,
            input_variables=[
                "customer_message",
                "conversation_history",
                "escalation_trigger",
                "customer_phone",
            ],
            partial_variables={
                "format_instructions": self.output_parser.get_format_instructions()
            },
        )

    async def analyze_escalation(
        self,
        customer_message: str,
        conversation_history: List[Message],
        escalation_trigger: str,
        customer_phone: str,
    ) -> EscalationAnalysis:
        """Analyze an escalation case and provide recommendations."""
        try:
            # Format conversation history
            history_text = self._format_conversation_history(conversation_history)

            # Generate escalation analysis
            result = await self.chain.ainvoke(
                {
                    "customer_message": customer_message,
                    "conversation_history": history_text,
                    "escalation_trigger": escalation_trigger,
                    "customer_phone": customer_phone,
                }
            )

            # Parse the response
            analysis = self.output_parser.parse(result["text"])

            return analysis

        except Exception as e:
            # Return default escalation analysis on error
            return EscalationAnalysis(
                escalation_level="medium",
                escalation_reason=f"Error in escalation analysis: {str(e)}",
                priority_score=5,
                required_skills=["general_support"],
                estimated_resolution_time="1-2 hours",
                customer_impact="medium",
                suggested_agent="general_support_agent",
                immediate_actions=["acknowledge customer", "assign to human agent"],
            )

    def _format_conversation_history(self, messages: List[Message]) -> str:
        """Format conversation history for escalation analysis."""
        if not messages:
            return "No previous messages in this conversation."

        formatted = []
        for msg in messages[-10:]:  # Last 10 messages for context
            role = "Customer" if msg.sender_id != "agent" else "Agent"
            timestamp = (
                msg.timestamp.strftime("%H:%M")
                if hasattr(msg.timestamp, "strftime")
                else "unknown"
            )
            formatted.append(f"[{timestamp}] {role}: {msg.content}")

        return "\n".join(formatted)

    def get_escalation_priority(self, analysis: EscalationAnalysis) -> str:
        """Get priority level based on escalation analysis."""
        if analysis.priority_score >= 8:
            return "urgent"
        elif analysis.priority_score >= 6:
            return "high"
        elif analysis.priority_score >= 4:
            return "medium"
        else:
            return "low"

    def should_escalate_immediately(self, analysis: EscalationAnalysis) -> bool:
        """Determine if escalation should happen immediately."""
        immediate_triggers = [
            analysis.escalation_level == "urgent",
            analysis.priority_score >= 9,
            analysis.customer_impact == "critical",
            "billing_dispute" in analysis.escalation_reason.lower(),
            "complaint" in analysis.escalation_reason.lower(),
        ]

        return any(immediate_triggers)

    def get_escalation_summary(self, analysis: EscalationAnalysis) -> Dict[str, Any]:
        """Get a summary of the escalation for reporting."""
        return {
            "level": analysis.escalation_level,
            "priority": analysis.priority_score,
            "reason": analysis.escalation_reason,
            "impact": analysis.customer_impact,
            "estimated_time": analysis.estimated_resolution_time,
            "required_skills": analysis.required_skills,
            "suggested_agent": analysis.suggested_agent,
            "immediate_actions": analysis.immediate_actions,
            "timestamp": time.time(),
        }

    def create_escalation_ticket(
        self, analysis: EscalationAnalysis, conversation_id: str
    ) -> Dict[str, Any]:
        """Create an escalation ticket for human agents."""
        return {
            "ticket_id": f"ESC-{conversation_id}-{int(time.time())}",
            "conversation_id": conversation_id,
            "escalation_level": analysis.escalation_level,
            "priority_score": analysis.priority_score,
            "reason": analysis.escalation_reason,
            "customer_impact": analysis.customer_impact,
            "required_skills": analysis.required_skills,
            "suggested_agent": analysis.suggested_agent,
            "estimated_resolution_time": analysis.estimated_resolution_time,
            "immediate_actions": analysis.immediate_actions,
            "created_at": time.time(),
            "status": "open",
        }
