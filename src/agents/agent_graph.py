"""
Agent graph configuration and factory functions for LangGraph.
"""

from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages

from .support_agent import SupportAgent
from ..models.agent import AgentState


def create_agent_graph(agent_type: str = "support") -> StateGraph:
    """
    Create an agent graph based on the specified type.

    Args:
        agent_type: Type of agent to create ("support", "escalation", "general")

    Returns:
        Configured StateGraph instance
    """

    if agent_type == "support":
        return _create_support_graph()
    elif agent_type == "escalation":
        return _create_escalation_graph()
    elif agent_type == "general":
        return _create_general_graph()
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")


def _create_support_graph() -> StateGraph:
    """Create the main support agent graph."""

    # Create the state graph
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("analyze_message", _analyze_message_node)
    workflow.add_node("generate_response", _generate_response_node)
    workflow.add_node("analyze_conversation", _analyze_conversation_node)
    workflow.add_node("handle_escalation", _handle_escalation_node)
    workflow.add_node("finalize_response", _finalize_response_node)

    # Define the workflow
    workflow.set_entry_point("analyze_message")

    # Add edges
    workflow.add_edge("analyze_message", "generate_response")
    workflow.add_edge("generate_response", "analyze_conversation")

    # Add conditional edges for escalation
    workflow.add_conditional_edges(
        "analyze_conversation",
        _should_escalate_router,
        {"escalate": "handle_escalation", "continue": "finalize_response"},
    )

    workflow.add_edge("handle_escalation", "finalize_response")
    workflow.add_edge("finalize_response", END)

    return workflow.compile()


def _create_escalation_graph() -> StateGraph:
    """Create an escalation-specific agent graph."""

    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("analyze_escalation", _analyze_escalation_node)
    workflow.add_node("create_ticket", _create_ticket_node)
    workflow.add_node("notify_agents", _notify_agents_node)
    workflow.add_node("finalize_escalation", _finalize_escalation_node)

    # Define workflow
    workflow.set_entry_point("analyze_escalation")
    workflow.add_edge("analyze_escalation", "create_ticket")
    workflow.add_edge("create_ticket", "notify_agents")
    workflow.add_edge("notify_agents", "finalize_escalation")
    workflow.add_edge("finalize_escalation", END)

    return workflow.compile()


def _create_general_graph() -> StateGraph:
    """Create a general-purpose agent graph."""

    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("process_input", _process_input_node)
    workflow.add_node("generate_response", _generate_response_node)
    workflow.add_node("finalize", _finalize_node)

    # Define workflow
    workflow.set_entry_point("process_input")
    workflow.add_edge("process_input", "generate_response")
    workflow.add_edge("generate_response", "finalize")
    workflow.add_edge("finalize", END)

    return workflow.compile()


# Node implementations for the graphs
async def _analyze_message_node(state: AgentState) -> AgentState:
    """Analyze the incoming message."""
    # This would be implemented by the SupportAgent class
    return state


async def _generate_response_node(state: AgentState) -> AgentState:
    """Generate a response."""
    # This would be implemented by the SupportAgent class
    return state


async def _analyze_conversation_node(state: AgentState) -> AgentState:
    """Analyze conversation context."""
    # This would be implemented by the SupportAgent class
    return state


async def _handle_escalation_node(state: AgentState) -> AgentState:
    """Handle escalation."""
    # This would be implemented by the SupportAgent class
    return state


async def _finalize_response_node(state: AgentState) -> AgentState:
    """Finalize the response."""
    # This would be implemented by the SupportAgent class
    return state


async def _analyze_escalation_node(state: AgentState) -> AgentState:
    """Analyze escalation case."""
    # Placeholder implementation
    return state


async def _create_ticket_node(state: AgentState) -> AgentState:
    """Create escalation ticket."""
    # Placeholder implementation
    return state


async def _notify_agents_node(state: AgentState) -> AgentState:
    """Notify human agents."""
    # Placeholder implementation
    return state


async def _finalize_escalation_node(state: AgentState) -> AgentState:
    """Finalize escalation."""
    # Placeholder implementation
    return state


async def _process_input_node(state: AgentState) -> AgentState:
    """Process general input."""
    # Placeholder implementation
    return state


async def _finalize_node(state: AgentState) -> AgentState:
    """Finalize general processing."""
    # Placeholder implementation
    return state


def _should_escalate_router(state: AgentState) -> str:
    """Route based on escalation decision."""
    if state.should_escalate:
        return "escalate"
    return "continue"


def create_agent_with_memory(agent_type: str = "support") -> StateGraph:
    """
    Create an agent graph with memory persistence.

    Args:
        agent_type: Type of agent to create

    Returns:
        Configured StateGraph with memory
    """

    graph = create_agent_graph(agent_type)
    memory = MemorySaver()

    return graph.compile(checkpointer=memory)


def get_agent_config(agent_type: str = "support") -> Dict[str, Any]:
    """
    Get configuration for a specific agent type.

    Args:
        agent_type: Type of agent

    Returns:
        Configuration dictionary
    """

    configs = {
        "support": {
            "max_tokens": 1000,
            "temperature": 0.7,
            "model": "gpt-4",
            "timeout": 30,
            "retry_attempts": 3,
        },
        "escalation": {
            "max_tokens": 800,
            "temperature": 0.2,
            "model": "gpt-4",
            "timeout": 45,
            "retry_attempts": 2,
        },
        "general": {
            "max_tokens": 500,
            "temperature": 0.5,
            "model": "gpt-3.5-turbo",
            "timeout": 20,
            "retry_attempts": 3,
        },
    }

    return configs.get(agent_type, configs["general"])
