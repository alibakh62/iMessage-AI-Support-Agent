"""
Main support agent using LangGraph for conversation management.
"""

from typing import Dict, Any, List, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
import uuid
import time
from datetime import datetime

from ..models.agent import AgentState, AgentResponse
from ..models.conversation import Message, Participant, ParticipantRole
from ..chains.support_chain import SupportChain
from ..chains.conversation_chain import ConversationChain
from ..chains.escalation_chain import EscalationChain


class SupportAgent:
    """Main support agent using LangGraph for conversation management."""

    def __init__(self):
        self.support_chain = SupportChain()
        self.conversation_chain = ConversationChain()
        self.escalation_chain = EscalationChain()
        self.graph = self._create_graph()
        self.memory = MemorySaver()

    def _create_graph(self) -> StateGraph:
        """Create the LangGraph state graph for the support agent."""

        # Create the state graph
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node("analyze_message", self._analyze_message)
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("analyze_conversation", self._analyze_conversation)
        workflow.add_node("handle_escalation", self._handle_escalation)
        workflow.add_node("finalize_response", self._finalize_response)

        # Define the workflow
        workflow.set_entry_point("analyze_message")

        # Add edges
        workflow.add_edge("analyze_message", "generate_response")
        workflow.add_edge("generate_response", "analyze_conversation")
        workflow.add_edge("analyze_conversation", "handle_escalation")
        workflow.add_edge("handle_escalation", "finalize_response")
        workflow.add_edge("finalize_response", END)

        # Add conditional edges for escalation
        workflow.add_conditional_edges(
            "analyze_conversation",
            self._should_escalate,
            {"escalate": "handle_escalation", "continue": "finalize_response"},
        )

        return workflow.compile(checkpointer=self.memory)

    async def _analyze_message(self, state: AgentState) -> AgentState:
        """Analyze the incoming message and prepare for processing."""
        try:
            # Mark as processing
            state.is_processing = True
            state.processing_start_time = time.time()

            # Extract current message
            if state.current_message:
                # Process the message content
                state.messages.append(state.current_message)

                # Update conversation history
                history_entry = {
                    "role": "user",
                    "content": state.current_message.content,
                    "timestamp": state.current_message.timestamp.isoformat(),
                }
                state.conversation_history.append(history_entry)

            return state

        except Exception as e:
            state.error_message = f"Error analyzing message: {str(e)}"
            state.is_processing = False
            return state

    async def _generate_response(self, state: AgentState) -> AgentState:
        """Generate a response using the support chain."""
        try:
            if not state.current_message:
                state.error_message = "No current message to process"
                return state

            # Generate response using support chain
            response = await self.support_chain.generate_response(
                customer_message=state.current_message.content,
                conversation_history=state.conversation_history,
            )

            # Update state with response
            state.generated_response = response.content
            state.response_metadata = response.metadata
            state.confidence_score = response.confidence_score
            state.response_time = response.response_time
            state.should_escalate = response.should_escalate
            state.escalation_reason = response.escalation_reason

            return state

        except Exception as e:
            state.error_message = f"Error generating response: {str(e)}"
            state.should_escalate = True
            state.escalation_reason = f"Error in response generation: {str(e)}"
            return state

    async def _analyze_conversation(self, state: AgentState) -> AgentState:
        """Analyze the overall conversation context."""
        try:
            # Create a mock conversation object for analysis
            # In a real implementation, this would come from the database
            mock_conversation = self._create_mock_conversation(state)

            # Analyze conversation
            analysis = await self.conversation_chain.analyze_conversation(
                mock_conversation
            )

            # Update state with analysis results
            state.conversation_tags = analysis.tags

            # Check if escalation is needed based on conversation analysis
            if self.conversation_chain.should_escalate_conversation(analysis):
                state.should_escalate = True
                state.escalation_reason = f"Conversation analysis indicates escalation needed: {analysis.next_best_action}"

            return state

        except Exception as e:
            state.error_message = f"Error analyzing conversation: {str(e)}"
            return state

    async def _handle_escalation(self, state: AgentState) -> AgentState:
        """Handle escalation if needed."""
        try:
            if not state.should_escalate:
                return state

            # Analyze escalation
            escalation_analysis = await self.escalation_chain.analyze_escalation(
                customer_message=(
                    state.current_message.content if state.current_message else ""
                ),
                conversation_history=state.messages,
                escalation_trigger=state.escalation_reason,
                customer_phone=self._get_customer_phone(state),
            )

            # Update state with escalation details
            state.escalation_reason = escalation_analysis.escalation_reason

            # Add escalation tags
            state.conversation_tags.extend(
                [
                    f"escalation_{escalation_analysis.escalation_level}",
                    f"priority_{escalation_analysis.priority_score}",
                ]
            )

            return state

        except Exception as e:
            state.error_message = f"Error handling escalation: {str(e)}"
            return state

    async def _finalize_response(self, state: AgentState) -> AgentState:
        """Finalize the response and prepare for delivery."""
        try:
            # Mark processing as complete
            state.is_processing = False

            # If escalation is needed, modify the response
            if state.should_escalate:
                escalation_note = f"\n\n[Note: This case has been escalated to human support. Reason: {state.escalation_reason}]"
                state.generated_response += escalation_note

            # Update conversation tags
            if state.conversation_tags:
                state.conversation_tags = list(
                    set(state.conversation_tags)
                )  # Remove duplicates

            return state

        except Exception as e:
            state.error_message = f"Error finalizing response: {str(e)}"
            state.is_processing = False
            return state

    def _should_escalate(self, state: AgentState) -> str:
        """Determine if escalation is needed."""
        if state.should_escalate:
            return "escalate"
        return "continue"

    def _create_mock_conversation(self, state: AgentState):
        """Create a mock conversation object for analysis."""
        # This is a simplified version - in production, you'd get this from the database
        from ..models.conversation import Conversation, Participant

        participants = [
            Participant(
                id="customer", phone_number="+1234567890", role=ParticipantRole.USER
            ),
            Participant(
                id="agent", phone_number="+0987654321", role=ParticipantRole.AGENT
            ),
        ]

        return Conversation(
            id=state.conversation_id,
            participants=participants,
            messages=state.messages,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

    def _get_customer_phone(self, state: AgentState) -> str:
        """Extract customer phone number from state."""
        # In a real implementation, this would come from the conversation participants
        return "+1234567890"  # Placeholder

    async def process_message(
        self,
        message_content: str,
        conversation_id: str,
        sender_phone: str,
        sender_name: str = None,
    ) -> AgentResponse:
        """Process an incoming message and generate a response."""

        # Create initial state
        initial_state = AgentState(
            conversation_id=conversation_id,
            current_message=Message(
                id=str(uuid.uuid4()),
                conversation_id=conversation_id,
                sender_id="customer",
                content=message_content,
                timestamp=datetime.now(),
            ),
        )

        # Run the graph
        try:
            final_state = await self.graph.ainvoke(initial_state)

            # Create response
            response = AgentResponse(
                content=final_state.generated_response
                or "I apologize, but I couldn't generate a response.",
                conversation_id=conversation_id,
                confidence_score=final_state.confidence_score or 0.0,
                response_time=final_state.response_time or 0.0,
                should_escalate=final_state.should_escalate,
                escalation_reason=final_state.escalation_reason,
                metadata={
                    "conversation_tags": final_state.conversation_tags,
                    "response_metadata": final_state.response_metadata,
                    "error_message": final_state.error_message,
                },
            )

            return response

        except Exception as e:
            # Handle errors
            return AgentResponse(
                content="I apologize, but I'm experiencing technical difficulties. Please try again or contact human support.",
                conversation_id=conversation_id,
                confidence_score=0.0,
                response_time=0.0,
                should_escalate=True,
                escalation_reason=f"Error in agent processing: {str(e)}",
                error_details=str(e),
            )
