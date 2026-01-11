# 🔍 AI Code Archaeologist

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.128-green)](https://fastapi.tiangolo.com/)
[![Tests](https://img.shields.io/badge/Tests-32%20Passing-success)](https://github.com/NidaKhaan/ai-code-archaeologist)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

**[🌐 Live Demo](https://web-production-af110.up.railway.app)** | **[📖 API Docs](https://web-production-af110.up.railway.app/docs)** | **[🐛 Report Issue](https://github.com/NidaKhaan/ai-code-archaeologist/issues)**

> An intelligent code analysis platform that combines AI insights with advanced static analysis to evaluate code quality, security, and architecture.

---

## 🎬 Screenshots

<div align="center">
  <img src="docs/images/screenshot1_hero.png" alt="Hero Section" width="800"/>
  <p><em>Clean, cinematic interface</em></p>
  
  <img src="docs/images/screenshot2_progress.png" alt="Analysis Progress" width="800"/>
  <p><em>Real-time analysis tracking</em></p>
  
  <img src="docs/images/screenshot3_results.png" alt="Results Dashboard" width="800"/>
  <p><em>Comprehensive quality insights</em></p>
</div>

---

## ✨ Key Features

- **🤖 Dual AI Support** - Local models (Ollama) + Cloud API (Groq)
- **🔍 Deep Code Analysis** - AST parsing, complexity metrics, security scanning
- **🏗️ Architecture Detection** - Identifies design patterns (Singleton, Factory, Observer)
- **📊 Quality Scoring** - A-F grades based on maintainability, complexity, and security
- **🔒 Security Scanning** - Detects vulnerabilities with Bandit
- **📦 GitHub Integration** - Analyze any public repository instantly
- **📄 Export Reports** - Download Markdown or JSON reports
- **🎨 Modern UI** - Dark theme with smooth animations

---

## 🚀 Quick Start

### Try the Live Demo

Visit **[web-production-af110.up.railway.app](https://web-production-af110.up.railway.app)**

- API Key: `dev_key_123`
- Try: `https://github.com/psf/requests`

### Run Locally
```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/ai-code-archaeologist.git
cd ai-code-archaeologist

# Setup environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run server
uvicorn src.main:app --reload
```

Visit `http://localhost:8000`

---

## 🏗️ Architecture
```
┌─────────────────┐
│   Web UI        │  ← React-like vanilla JS + Dark theme
├─────────────────┤
│   FastAPI       │  ← RESTful API with auth & rate limiting
├─────────────────┤
│  Analysis Core  │  ← AST, Radon, Bandit, Custom detectors
├─────────────────┤
│  LLM Providers  │  ← Ollama (local) / Groq (cloud)
├─────────────────┤
│  Database       │  ← SQLAlchemy + SQLite
└─────────────────┘
```

### Tech Stack

**Backend:**
- FastAPI - Modern Python web framework
- SQLAlchemy - ORM with async support
- Pydantic - Data validation

**Analysis:**
- AST - Python's Abstract Syntax Tree
- Radon - Complexity metrics
- Bandit - Security scanning
- Custom algorithms - Architecture & pattern detection

**AI/ML:**
- Ollama - Local LLM runtime
- Groq - Cloud inference API
- CodeLlama - Meta's code model

**Frontend:**
- HTML
- Vanilla JavaScript
- CSS3 
- Font: Inter + JetBrains Mono
---

## 📖 API Usage

### Analyze Code Snippet
```bash
curl -X POST "https://web-production-af110.up.railway.app/analyze/complete" \
  -H "X-API-Key: dev_key_123" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def example(): pass",
    "filename": "test.py"
  }'
```

### Analyze GitHub Repository
```bash
curl -X POST "https://web-production-af110.up.railway.app/github/analyze-full?repo_url=https://github.com/psf/requests" \
  -H "X-API-Key: dev_key_123"
```

### Download Report
```bash
curl "https://web-production-af110.up.railway.app/reports/markdown/1" \
  -H "X-API-Key: dev_key_123" \
  -o report.md
```

**[Full API Documentation →](https://web-production-af110.up.railway.app/docs)**

---

## 🧪 Testing
```bash
# Run all tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=term-missing
```

**Test Coverage:** 32+ tests across all modules

---

## 🛠️ What I Built

This project demonstrates:

✅ **Full-stack development** - Backend API + Frontend + Database  
✅ **Advanced Python** - AST manipulation, async programming, OOP  
✅ **API design** - RESTful, authentication, rate limiting  
✅ **Static analysis** - Custom algorithms for pattern detection  
✅ **AI integration** - Multi-provider LLM support  
✅ **DevOps** - CI/CD, Docker-ready, cloud deployment  
✅ **Clean code** - Type hints, docstrings, tested  

**Not just API calls** - The core analysis engine is 100% custom code.

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file

---

## 👨‍💻 Author

**Nida**

Building AI-powered tools for developers.

[GitHub](https://github.com/NidaKhaan)

---
<div align="center">
  <sub>Built with ❤️ as part of my AI Engineering journey</sub>
</div>