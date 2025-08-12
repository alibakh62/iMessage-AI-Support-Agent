"""
Demo script for the iMessage AI Support Agent.
"""

import asyncio
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our modules
from src.models.conversation import Message, Participant, ParticipantRole
from src.models.agent import AgentState, AgentResponse
from src.utils.helpers import generate_conversation_id, format_timestamp
from src.utils.validators import validate_phone_number, validate_email


async def demo_basic_functionality():
    """Demonstrate basic functionality of the agent."""

    logger.info("🚀 Starting iMessage AI Support Agent Demo")

    # Generate a conversation ID
    conversation_id = generate_conversation_id()
    logger.info(f"📱 Generated conversation ID: {conversation_id}")

    # Create a participant
    customer = Participant(
        id="customer-001",
        phone_number="+1234567890",
        name="John Doe",
        role=ParticipantRole.USER,
    )
    logger.info(f"👤 Created customer: {customer.name} ({customer.phone_number})")

    # Create a message
    message = Message(
        id="msg-001",
        conversation_id=conversation_id,
        sender_id=customer.id,
        content="Hi, I'm having trouble with my account. Can you help me?",
    )
    logger.info(f"💬 Created message: {message.content}")

    # Create agent state
    agent_state = AgentState(
        conversation_id=conversation_id,
        agent_name="support_agent",
        agent_role="customer_support",
    )
    logger.info(f"🤖 Created agent state for: {agent_state.agent_name}")

    # Validate some data
    phone_valid, phone_error = validate_phone_number(customer.phone_number)
    email_valid, email_error = validate_email("john.doe@example.com")

    logger.info(f"📞 Phone validation: {'✅ Valid' if phone_valid else '❌ Invalid'}")
    if not phone_valid:
        logger.error(f"   Error: {phone_error}")

    logger.info(f"📧 Email validation: {'✅ Valid' if email_valid else '❌ Invalid'}")
    if not email_valid:
        logger.error(f"   Error: {email_error}")

    # Format timestamp
    current_time = format_timestamp()
    logger.info(f"⏰ Current time: {current_time}")

    # Create a mock response
    response = AgentResponse(
        content="Hello! I'd be happy to help you with your account. What specific issue are you experiencing?",
        conversation_id=conversation_id,
        confidence_score=0.9,
        response_time=1.2,
    )
    logger.info(f"💭 Generated response: {response.content}")
    logger.info(f"   Confidence: {response.confidence_score}")
    logger.info(f"   Response time: {response.response_time}s")

    logger.info("✅ Demo completed successfully!")


async def demo_conversation_flow():
    """Demonstrate a simple conversation flow."""

    logger.info("🔄 Starting conversation flow demo")

    # Create conversation
    conversation_id = generate_conversation_id("demo")

    # Simulate a conversation
    messages = [
        "Hi, I need help with my subscription",
        "I'm being charged twice this month",
        "Yes, I've tried contacting billing but no response",
        "Thank you for escalating this",
    ]

    logger.info(f"💬 Simulating conversation: {conversation_id}")

    for i, content in enumerate(messages, 1):
        message = Message(
            id=f"msg-{i:03d}",
            conversation_id=conversation_id,
            sender_id="customer",
            content=content,
        )

        logger.info(f"   {i}. Customer: {content}")

        # Simulate processing delay
        await asyncio.sleep(0.1)

        # Generate mock response
        if "escalating" in content.lower() or "escalate" in content.lower():
            response_content = "I understand your frustration. I'm escalating this to our billing specialist who will contact you within 2 hours."
            should_escalate = True
        else:
            response_content = f"Thank you for that information. Let me help you with {content.lower().split()[0]}."
            should_escalate = False

        response = AgentResponse(
            content=response_content,
            conversation_id=conversation_id,
            confidence_score=0.85,
            response_time=0.8,
            should_escalate=should_escalate,
        )

        logger.info(f"   🤖 Agent: {response.content}")
        if response.should_escalate:
            logger.info("   ⚠️  Escalation triggered!")

    logger.info("✅ Conversation flow demo completed!")


async def main():
    """Main demo function."""

    try:
        # Run basic functionality demo
        await demo_basic_functionality()
        print("\n" + "=" * 50 + "\n")

        # Run conversation flow demo
        await demo_conversation_flow()

    except Exception as e:
        logger.error(f"❌ Demo failed: {e}")
        raise


if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())
