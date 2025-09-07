# Horo RAG MVP

A Retrieval-Augmented Generation (RAG) system for business document Q&A with proper citations and knowledge gap detection. Built as a demonstration of AI-powered document assistance for business founders.

## Features

- **Document Upload & Processing**: Upload text files to create a private knowledge base
- **Intelligent Q&A**: Ask questions about your documents and get accurate answers
- **Source Citations**: Every answer includes references to specific documents and pages
- **Knowledge Gap Detection**: System identifies when information is missing and suggests relevant document types
- **Document Type Classification**: Automatically categorizes uploads (Policy, Handbook, Finance, etc.)
- **Tenant Isolation**: Each user's documents are completely private and isolated
- **Confidence Scoring**: Visual indicators show answer reliability

## Architecture

- **Backend**: FastAPI + LlamaIndex + Ollama
- **Frontend**: Alpine.js + Tailwind CSS
- **LLM**: Gemma3 via Ollama
- **Embeddings**: BGE-M3 via Ollama
- **Storage**: In-memory (MVP scope)

## Prerequisites

1. **Python 3.12+**
2. **Ollama** installed and running locally
3. Required Ollama models:
   ```bash
   ollama pull gemma3
   ollama pull bge-m3
   ```

## Quick Start

### 1. Install Ollama and Models

**Install Ollama:**

```bash
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows: Download from ollama.ai
```

**Pull required models:**

```bash
ollama pull gemma3
ollama pull bge-m3
```

### 2. Clone and Setup

```bash
git clone <repository-url>
cd horo-rag-mvp

# Install Python dependencies
cd backend
pip install -r requirements.txt
```

### 3. Start the Application

**Terminal 1 - Backend:**

```bash
cd backend
python main.py
```

**Terminal 2 - Frontend:**

```bash
cd frontend
python -m http.server 3000
```

**Access the application:**

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Usage

### Upload Documents

1. Click the upload area or drag & drop text files
2. Supported formats: `.txt` (MVP limitation)
3. Documents are automatically categorized by type

### Ask Questions

1. Type questions in the chat interface
2. Examples:
   - "What is our loan policy?"
   - "What are the onboarding steps?"
   - "What was TechFlow's revenue in 2024?"

### Citations & Sources

- Answers include clickable source references
- Format: `Document Name (p. X)`
- Confidence scores show answer reliability

### Knowledge Gaps

- When information is missing, system suggests relevant document types
- Example: "Upload financial reports, budget documents"

## API Endpoints

### POST /upload

Upload and process documents

```bash
curl -X POST "http://localhost:8000/upload" \
  -H "X-Tenant-ID: demo" \
  -F "file=@document.txt"
```

### POST /query

Query documents with citations

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: demo" \
  -d '{
    "tenant_id": "demo",
    "question": "What is our revenue model?"
  }'
```

### GET /documents

List tenant's documents

```bash
curl -H "X-Tenant-ID: demo" http://localhost:8000/documents
```

## Example Interactions

**With Relevant Documents:**

```
Q: "What's our maximum loan amount?"
A: "For first-time borrowers, the maximum loan size is $50,000..."
Citations: Loan Policy (p. 3), Credit Guidelines (p. 7)
```

**Knowledge Gap Scenario:**

```
Q: "What's our customer acquisition cost?"
A: "I don't have information about CAC in your documents."
Suggestions: Upload financial reports, growth metrics, marketing analytics
```

## Project Structure

```
horo-rag-mvp/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic data models
│   ├── chat_service.py      # Core RAG logic with LlamaIndex
│   └── requirements.txt     # Python dependencies
├── frontend/
│   └── index.html          # Alpine.js chat interface
└── README.md
```

## Configuration

### Environment Variables

Create `.env` file in backend directory:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=gemma2:9b
OLLAMA_EMBED_MODEL=bge-m3
```

### Tenant Isolation

Documents are isolated by tenant ID passed in `X-Tenant-ID` header. Each tenant has completely separate document storage and retrieval scope.

## Limitations (MVP Scope)

- **File Types**: Text files (.txt) only
- **Storage**: In-memory (data lost on restart)
- **Page Estimation**: Simple content length calculation
- **Authentication**: None (uses header-based tenant identification)
- **Scalability**: Single-server deployment

## Troubleshooting

**Upload Issues:**

- Ensure backend is running on port 8000
- Check browser console for detailed error logs
- Verify file is .txt format

**Model Issues:**

- Confirm Ollama is running: `ollama list`
- Restart Ollama service if needed: `ollama serve`

**Performance:**

- First query may be slow (model loading)
- Subsequent queries should be faster

## Development

**Backend Development:**

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend Development:**

- Edit `frontend/index.html` directly
- No build process required (vanilla Alpine.js)

## Production Considerations

For production deployment, consider:

- PostgreSQL for persistent storage
- Redis for caching
- Authentication system
- File upload security validation
- Rate limiting and API quotas
- Docker containerization
- Load balancing for multiple instances

## License

MIT License - See LICENSE file for details
