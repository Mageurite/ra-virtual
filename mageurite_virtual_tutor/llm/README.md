# RAG AI Assistant

A sophisticated AI assistant system that combines Retrieval-Augmented Generation (RAG) with external search capabilities, built with LangGraph, Ollama, and Milvus.

## 🚀 Features

- **Intelligent Query Classification**: Automatically determines whether queries need RAG retrieval, web search, or can be answered directly
- **Multi-Source Retrieval**: Integrates with Milvus vector database for personal and public knowledge bases
- **External Web Search**: Uses Tavily Search API for real-time information
- **Content Safety**: Built-in guardrails to filter inappropriate content and homework requests
- **Streaming Responses**: Real-time streaming chat interface
- **Session Management**: Persistent conversation history with SQLite checkpointing
- **Model Management**: Dynamic model switching between different Ollama models

## 🏗️ Architecture

The system is built on a LangGraph workflow with the following components:

1. **Guardrail Check**: Content safety classification
2. **Query Rewrite**: Intelligent query reformulation for better retrieval
3. **Query Classification**: Determines retrieval strategy (RAG/Web/None)
4. **Document Retrieval**: Milvus API integration for knowledge base search
5. **Web Search**: External search via Tavily
6. **Response Generation**: LLM-powered response generation with streaming

## 📋 Prerequisites

- Python 3.8+
- Ollama (with models: `mistral-nemo:12b-instruct-2407-fp16`, `llama3.1:8b-instruct-q4_K_M`)
- Milvus API service running on `http://localhost:9090`
- Tavily API key

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd capstone-project-25t2-9900-h16c-bread1
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   export TAVILY_API_KEY="your_tavily_api_key"
   export MILVUS_API_BASE_URL="http://localhost:9090"
   ```

4. **Start Ollama and load models**
   ```bash
   ollama serve
   ollama pull mistral-nemo:12b-instruct-2407-fp16
   ollama pull llama3.1:8b-instruct-q4_K_M
   ```

## 🚀 Quick Start

1. **Start the API server**
   ```bash
   python rag/api_interface.py
   ```

2. **Test the API**
   ```bash
   python rag/test_simple_api.py
   ```

3. **Access the web interface**
   - Open `http://localhost:8100` in your browser
   - Use the streaming chat interface

## 📚 API Documentation

### Core Endpoints

#### POST `/chat/stream`
Streaming chat interface for real-time conversation.

**Request Body:**
```json
{
  "user_id": "string",
  "session_id": "string", 
  "input": "string"
}
```

**Response:** Server-Sent Events (SSE) stream with chunks:
```json
{
  "chunk": "response text",
  "status": "streaming",
  "timestamp": "2024-01-01T00:00:00"
}
```

#### GET `/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00"
}
```

#### POST `/activate_model`
Switch between different Ollama models.

**Request Body:**
```json
{
  "model": "mistral-nemo:12b-instruct-2407-fp16"
}
```

### Milvus API Integration

The system integrates with a Milvus vector database service for document retrieval:

- **Base URL**: `http://localhost:9090`
- **Query Endpoint**: `/retriever`
- **Health Endpoint**: `/retriever`

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TAVILY_API_KEY` | Required | Tavily Search API key |
| `MILVUS_API_BASE_URL` | `http://localhost:9090` | Milvus API service URL |
| `MILVUS_API_TIMEOUT` | `30` | API timeout in seconds |
| `DEFAULT_PERSONAL_K` | `5` | Default personal knowledge results |
| `DEFAULT_PUBLIC_K` | `5` | Default public knowledge results |
| `DEFAULT_FINAL_K` | `10` | Default final results count |

### Model Configuration

Supported Ollama models:
- `mistral-nemo:12b-instruct-2407-fp16` (default)
- `llama3.1:8b-instruct-q4_K_M`

## 🧪 Testing

Run the test suite:
```bash
python rag/test_simple_api.py
```

The test script includes:
- Streaming API functionality test
- Health check validation
- Error handling verification

## 📁 Project Structure

```
rag/
├── ai_assistant_final.py    # Main LangGraph workflow
├── api_interface.py         # Flask API server
├── milvus_api_client.py     # Milvus API client
├── milvus_config.py         # Configuration management
├── test_simple_api.py       # API testing script
└── static/                  # Web interface assets
```

## 🔒 Security Features

- **Content Safety**: Automatic classification of queries into normal/homework_request/harmful
- **Input Validation**: Required field validation for all API endpoints
- **Error Handling**: Comprehensive error handling and logging
- **Session Isolation**: Separate conversation contexts per session

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Review existing issues
3. Create a new issue with detailed information

## 🔄 Workflow Diagram

The system follows this workflow:
1. **Input** → Guardrail Check
2. **Safe** → Query Rewrite → Classification
3. **Classification** → Retrieval/Web Search/Generation
4. **Generation** → Streaming Response

See `langgraph_rag.png` for a visual representation of the workflow.
