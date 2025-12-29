# Enterprise RAG Core

[![Hits](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fgithub.com%2Fshchae04%2Frag-vector&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false)](https://hits.seeyoufarm.com)
[![GitHub stars](https://img.shields.io/github/stars/shchae04/rag-vector?style=social)](https://github.com/shchae04/rag-vector)
[![GitHub forks](https://img.shields.io/github/forks/shchae04/rag-vector?style=social)](https://github.com/shchae04/rag-vector)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.2-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)

[한국어](README.md) | **English**

> **Core Engine for High-Performance Enterprise RAG (Retrieval-Augmented Generation)**
> Powered by Gemini 2.5 Flash Lite Hybrid Search Pipeline

## Overview

Enterprise RAG Core is an enterprise-grade system designed to securely manage internal documents and provide AI-driven Q&A capabilities. Built on a Docker Compose-based container architecture, it allows for immediate deployment without complex installation processes and guarantees high search accuracy through advanced RAG technology.

## Screenshots

| **Admin Dashboard (Document Management)** | **Chat Interface (Q&A)** |
|:---------------------------:|:--------------------------:|
| <img src="./assets/rag_admin.png" alt="Admin UI" width="400"> | <img src="./assets/rag_webui.png" alt="Chat UI" width="400"> |
| *Document Upload & Processing Monitoring* | *Accurate Answers with Citations* |

### Key Features

- **🔍 Next-Gen Hybrid Search Engine**
  - **Vector Search**: Semantic search using pgvector HNSW.
  - **Keyword Search**: Partial match search optimized for Korean (ILIKE Pattern Matching).
  - **RRF (Reciprocal Rank Fusion)**: Ensemble of both search results for optimal ranking.
  - **Enhanced Recall**: Expands candidates by 10x (`limit = top_k * 10`) to minimize search misses.

- **⚡️ Enterprise-Grade Performance & Architecture**
  - **Async Processing**: Celery + Redis based non-blocking document processing.
  - **Security**: JWT Authentication and RBAC.
  - **Scalability**: Modular monolith structure for easy feature expansion.

- **🧪 Quality Assurance**
  - **Ragas Evaluation**: Automated measurement pipeline for Faithfulness and Answer Relevancy.
  - **CI/CD Integration**: Automatic search quality verification on code changes.

- **Support for Various Document Formats**
  - HWP, PDF, DOCX, XLSX, TXT, MD, etc.

## Tech Stack

| Category | Technology | Usage |
|------|------|------|
| **Backend** | FastAPI 0.109.2 | Async API Server |
| **Database** | PostgreSQL 16 | pgvector (Vector) + ILIKE (Keyword) |
| **Broker/Queue** | Redis + Celery | Async Job Processing |
| **Search Algo** | RRF + KeywordReranker | Hybrid Search & Reranking |
| **Evaluation** | Ragas + LangSmith | RAG Quality Evaluation & Tracing |
| **Auth** | OAuth2 + JWT | Security & Authentication |
| **AI/LLM** | Google Gemini 2.5 Flash Lite | Embedding & Answer Generation (Enhanced Stability) |
| **DevOps** | Docker, GitHub Actions | Deployment & CI/CD |

## Quick Start

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running.
- [Google AI Studio](https://aistudio.google.com/) API Key (Free).

### Installation & Execution

1. **Environment Setup**
   ```bash
   cp .env.example .env
   # Open .env and enter your GOOGLE_API_KEY
   ```

2. **Run System with Docker Compose**
   ```bash
   docker-compose up --build -d
   ```
   On first run, migrations and **default admin account creation** (`admin@example.com / admin123`) are performed automatically.

3. **Access Services**

   | Service | URL | Usage |
   |--------|-----|------|
   | **Chat Interface** | [http://localhost:3000](http://localhost:3000) | AI Assistant Q&A (Select Rag-Model) |
   | **Document Admin** | [http://localhost:8501](http://localhost:8501) | Document Upload/Delete (Login required) |
   | **API Docs** | [http://localhost:8000/docs](http://localhost:8000/docs) | FastAPI Swagger UI |

4. **Check System Status**
   ```bash
   docker-compose ps
   docker-compose logs -f worker  # Check async worker logs
   ```

## Project Structure

```
rag-vector/
├── app/                    # Backend Application
│   ├── api/v1/            # API Routers (FastAPI)
│   ├── services/          # Business Logic (RAG Pipeline)
│   ├── models/            # SQLAlchemy Models (Document, User, etc.)
│   ├── core/              # Config, Logging, Exceptions, Security, Celery
│   ├── utils/             # File Parsers & Utilities
│   ├── worker.py          # Celery Async Task Definitions
│   └── initial_data.py    # Initial Data (Admin) Creation Script
├── docker/                # Docker Config (Entrypoint for migration & init)
├── tests/                 # Tests & Quality Evaluation Scripts
└── admin_app.py           # Streamlit Admin App
```

### Detailed Documentation

For more information, refer to the documents in the `/documentation` folder:

- [ARCHITECTURE.md](documentation/ARCHITECTURE.md) - System Architecture & Advanced RAG Pipeline
- [API.md](documentation/API.md) - REST API Endpoint Details
- [PROJECT_STRUCTURE.md](documentation/PROJECT_STRUCTURE.md) - Directory Structure Explanation
- [USER_GUIDE.md](documentation/USER_GUIDE.md) - Chat & Document Management Guide
- [SETUP.md](documentation/SETUP.md) - Local Development Environment Setup

## Key Features

### 1. Advanced RAG Pipeline

**Maximizing Accuracy with a 3-Step Search Strategy**

```
User Query
    ↓
[Step 1] Query Expansion
    - Add synonyms, related terms (Gemini 2.5 Flash Lite)
    - Solve vocabulary mismatch problems
    ↓
[Step 2] Wide Retrieval
    - Retrieve top k*10 candidates (e.g., 40~80)
    - Millisecond-level search with HNSW Index
    - Keyword inclusion with ILIKE pattern matching
    ↓
[Step 3] Hybrid Reranking (RRF & Reranking)
    - Combine vector similarity + keyword matching scores
    - Apply boost_weight=0.3
    ↓
Send final top k documents to LLM
```

### 2. Multi-Format Document Support

- **HWP**: Korean document parsing based on `olefile`
- **PDF**: High-speed parsing with `PyMuPDF`
- **Office**: Full support for DOCX, XLSX
- **Text**: TXT, MD, etc.

### 3. Multi-Model Support

This project uses **Google Gemini 2.5 Flash Lite** by default but can be easily switched to other models via configuration.

#### How to Change Models

1. Open `.env` file.
2. Modify `LLM_PROVIDER` and `LLM_MODEL`.

**Gemini (Default)**
```bash
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.5-flash-lite  # or gemini-1.5-pro
GOOGLE_API_KEY=your_google_key
```

**OpenAI (GPT-4o, etc.)**
```bash
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o
OPENAI_API_KEY=your_openai_key
```

**Anthropic (Claude 3.5 Sonnet)**
```bash
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-sonnet-20240620
ANTHROPIC_API_KEY=your_anthropic_key
```

> **Note**: After changing the model, run `docker-compose restart backend worker` to apply changes.

**⚠️ Warning: Embedding Model**
This project fixes the embedding model to **Google Gemini (`text-embedding-004`)** for search performance optimization.
If you change the embedding model in the code, existing vector data will be incompatible, requiring a **database reset and re-indexing of all documents**.

### 4. Enterprise Operations Features

- **Data Integrity**: Transaction-based atomic operations.
- **Auto Migration**: Automatic Alembic execution on container start.
- **Structured Logging**: JSON-formatted systematic logs.
- **Exception Handling**: Standardized error responses via global exception handler.

## Development Guide

### Local Development Environment

```bash
# 1. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment variables
cp .env.example .env
# Edit .env file

# 4. Start PostgreSQL (Run DB only with Docker Compose)
docker-compose up -d postgres

# 5. Database Migration
alembic upgrade head

# 6. Run Backend Server
uvicorn app.main:app --reload --port 8000

# 7. Run Admin UI (Separate Terminal)
streamlit run admin_app.py
```

### Testing

```bash
# Check API Server Health
curl http://localhost:8000/health

# Document Upload Test
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -F "file=@test.pdf"

# Chat Test
curl -X POST http://localhost:8000/api/v1/chat/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Test Question"}'

# Run RAG Quality Evaluation (Prerequisites: ragas, datasets, etc.)
# PYTHONPATH=. python tests/evaluation/evaluate_rag.py
```

## Environment Configuration

Major environment variables (`.env` file):

```bash
# LLM Settings
GOOGLE_API_KEY=your_google_api_key_here
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.5-flash-lite

# Database
DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/rag_db

# Server Settings
BACKEND_PORT=8000
ADMIN_PORT=8501
WEBUI_PORT=3000

# RAG Settings
CHUNK_SIZE=500
CHUNK_OVERLAP=100
SEARCH_K=4
RERANK_K=40  # k*10

# Web UI
WEBUI_NAME=Corp RAG Agent
ENABLE_WEB_SEARCH=False
```

## Troubleshooting

### Common Issues

**Q. "Quota exceeded" Error**
A. Gemini API free quota exceeded. Solved by changing `LLM_MODEL` to `gemini-2.5-flash-lite`.

**Q. Model not visible**
A. Check connection between Open WebUI and Backend. It is normal that only `rag-model` is displayed.

**Q. HWP file read failure**
A. Encrypted HWP files are not supported. Decrypt and upload.

**Q. Documents exist but search fails**
A. Keyword search (ILIKE) is applied, so if the exact word exists, it should be found. If synonyms are the issue, try asking more specifically.

### Check Logs

```bash
# All Logs
docker-compose logs -f

# Service Specific Logs
docker-compose logs -f backend
docker-compose logs -f postgres
docker-compose logs -f openwebui
```

## Contribution

Want to contribute?

1. Fork this repository.
2. Create a Feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Create a Pull Request.

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Roadmap

### ✅ Phase 1: Foundation (Completed)
- [x] **Core Architecture**: Modular Monolith design & Async processing implementation.
- [x] **Async Processing**: High-volume document processing via Redis/Celery.
- [x] **RAG Engine**: Query Expansion & Hybrid Reranking pipeline.
- [x] **Infrastructure**: Docker Compose container orchestration & CI/CD automation (GitHub Actions).
- [x] **Documentation**: Enterprise standard technical docs & operations guide.
- [x] **Search Optimization**: ILIKE search for Korean & candidate expansion.

### 🚧 Phase 2: Knowledge Integration (Planned)
- [ ] **Unified Ingestion Layer**: Scalable data connector architecture design based on `LangChain`.
  - **SaaS Connectors**: Confluence, Notion, Google Drive integration.
  - **Local Watcher**: Real-time file system change detection (Event-Driven) using `watchdog`.
- [ ] **Smart Sync Pipeline**: Incremental Sync for data efficiency.
  - **CDC (Change Data Capture)**: Deduplication via content hash comparison.
  - **Job Scheduling**: Periodic external source sync using `APScheduler`.

### 🔮 Phase 3: Advanced Intelligence
- [ ] **Frontend Modernization**: Build Enterprise Admin Console based on React (Next.js) replacing Streamlit.
- [ ] **Multi-modal RAG**: Advanced pipeline capable of analyzing images, charts, and graphs.

## License

This project is distributed under the MIT License. See [LICENSE](LICENSE) for details.

## Credits

- **FastAPI** - High-performance Python web framework
- **PostgreSQL + pgvector** - Vector search database
- **Google Gemini** - Free multi-modal AI model
- **Open WebUI** - Open source chat interface
- **Streamlit** - Rapid admin UI construction

---

**Made with precision by Enterprise RAG Team**
Contact: [GitHub Issues](https://github.com/shchae04/rag-vector/issues)
