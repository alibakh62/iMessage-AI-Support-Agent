# iMessage AI Support Agent

An intelligent AI-powered support agent that integrates with iMessage to provide automated customer support, intelligent responses, and seamless conversation management.

## 🚀 Features

- **AI-Powered Responses**: Uses advanced LLMs for intelligent, context-aware responses
- **iMessage Integration**: Seamless integration with Apple's iMessage platform
- **Multi-Agent Architecture**: Built with LangGraph for complex conversation flows
- **Context Management**: Maintains conversation history and context across sessions
- **Customizable Responses**: Configurable response templates and business logic
- **Analytics & Monitoring**: Track conversation metrics and agent performance

## 🏗️ Architecture

- **LangChain**: LLM orchestration and prompt management
- **LangGraph**: Multi-agent conversation flows and state management
- **Python**: Core application logic and API endpoints
- **FastAPI**: RESTful API for external integrations
- **SQLite**: Local conversation storage and context management


## 🛠️ Installation

```bash
# Clone the repository
git clone <your-github-url>
cd imessage-ai-support-agent

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run the application
python main.py
```

## 📁 Project Structure

```
imessage-ai-support-agent/
├── src/
│   ├── agents/           # LangGraph agent definitions
│   ├── chains/           # LangChain chains and prompts
│   ├── integrations/     # External service integrations
│   ├── models/           # Data models and schemas
│   ├── services/         # Business logic services
│   └── utils/            # Utility functions
├── tests/                # Test suite
├── config/               # Configuration files
├── docs/                 # Documentation
├── requirements.txt      # Python dependencies
├── main.py              # Application entry point
└── README.md            # This file
```

## 🔧 Configuration

Create a `.env` file with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
IMESSAGE_API_KEY=your_imessage_api_key
DATABASE_URL=sqlite:///conversations.db
LOG_LEVEL=INFO
```

## 🧪 Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=src
```

## 📊 Usage

The agent can be used in several ways:

1. **Direct API calls** to the FastAPI endpoints
2. **iMessage integration** for automated responses
3. **Web dashboard** for monitoring and management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details
