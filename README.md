# 🤖 AI Code Archaeologist

An intelligent code analysis platform powered by AI that understands, explains, and improves code like a senior developer.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.128-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🎯 What It Does

AI Code Archaeologist analyzes codebases using multiple AI models and static analysis tools to provide:

- 🧠 **AI-Powered Code Explanation** - Understands what your code does in plain English
- 🔍 **Deep Structure Analysis** - AST parsing reveals code architecture
- 📊 **Complexity Metrics** - Cyclomatic complexity, maintainability index, Halstead metrics
- 🔒 **Security Scanning** - Detects vulnerabilities using Bandit
- 💡 **Improvement Suggestions** - AI recommends optimizations and best practices
- 📈 **Quality Scoring** - Get an A-F grade for code maintainability

## ✨ Features

### Multi-LLM Support
- **Local AI** (Ollama with CodeLlama) - Free, private, unlimited
- **Cloud AI** (Groq) - Fast API responses
- Easily extensible to OpenAI, Anthropic Claude

### Code Analysis Engine
- Abstract Syntax Tree (AST) parsing
- Function and class extraction
- Import dependency tracking
- Cyclomatic complexity calculation
- Maintainability index scoring
- Security vulnerability detection

### Production-Ready API
- RESTful API with FastAPI
- API key authentication
- Rate limiting (prevents abuse)
- Auto-generated Swagger documentation
- Async database operations
- Comprehensive error handling

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Ollama (for local AI)

### Installation
```bash
# Clone the repository
git clone https://github.com/NidaKhaan/ai-code-archaeologist
cd ai-code-archaeologist

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys (optional for Groq)

# Install Ollama and download model
# Visit: https://ollama.com/download
ollama pull codellama:7b

# Run the server
uvicorn src.main:app --reload
```

Visit `http://127.0.0.1:8000/docs` for interactive API documentation!

## 📖 API Usage

### Analyze Code with AI
```bash
curl -X POST "http://127.0.0.1:8000/ai/explain-code" \
  -H "X-API-Key: dev_key_123" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def fibonacci(n): return n if n <= 1 else fibonacci(n-1) + fibonacci(n-2)",
    "language": "python"
  }'
```

### Deep Code Scan
```bash
curl -X POST "http://127.0.0.1:8000/analyze/deep-scan" \
  -H "X-API-Key: dev_key_123" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "your_code_here",
    "include_ast": true,
    "include_complexity": true,
    "include_security": true
  }'
```

## 🏗️ Tech Stack

**Backend:**
- FastAPI - Modern Python web framework
- SQLAlchemy - Database ORM
- Pydantic - Data validation

**AI/ML:**
- Ollama - Local LLM runtime
- Groq - Fast cloud inference
- CodeLlama - Meta's code-specialized model

**Code Analysis:**
- AST (Abstract Syntax Trees) - Python built-in
- Radon - Complexity metrics
- Bandit - Security scanning

**DevOps:**
- GitHub Actions - CI/CD
- Pytest - Testing framework
- Black & Flake8 - Code quality

## 📊 Project Status
**Current Phase:** Week 2 - Days 11-12 Complete ✅

**Completed Features:**
- ✅ Development environment & CI/CD
- ✅ FastAPI with authentication & rate limiting
- ✅ Database integration (SQLAlchemy)
- ✅ Multi-LLM support (Ollama + Groq)
- ✅ AST code structure analysis
- ✅ Complexity metrics (Radon)
- ✅ Security scanning (Bandit)
- ✅ Dependency graph analysis
- ✅ Architecture pattern detection
- ✅ Complete analysis endpoint with scoring
- ✅ 25+ comprehensive tests

**Next Steps:**
- 📅 Week 3: GitHub repository integration
- 📅 Week 3: Batch analysis & report generation
- 📅 Week 4: Web UI & cloud deployment


## 🧪 Testing
```bash
# Run all tests (25+ tests)
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_api.py -v
pytest tests/test_analyzers.py -v
```

**Current Test Coverage:** 25+ tests covering:
- API endpoints (auth, rate limiting)
- Database operations
- Code analysis (AST, complexity, security)
- Architecture detection
- Dependency analysis

## 🤝 Contributing

This is a learning project, but feedback is welcome! Feel free to open issues or suggest improvements.

## 📄 License

MIT License - See LICENSE file for details

## 👨‍💻 Author
Built this as part of my AI Engineering journey.

**Connect with me:**
- GitHub: https://github.com/NidaKhaan
- Portfolio: [Coming Soon]

---

⭐ Star this repo if you find it useful!