# API Endpoints - README

**FastAPI Wrapper for Drug-Target Graph Database Explorer**

**⚠️ IMPORTANT:** This API has been simplified. Backend queries Neo4j directly. API is only for AI operations.

## 🎯 Architecture

**Backend → Neo4j (Direct) → API (AI Only)**

- Backend queries Neo4j directly for all drug/target/network data
- API endpoints called ONLY when AI classification/prediction needed
- Minimal API surface: 4-5 endpoints total

## 📚 Documentation

**Start Here:**
- **`SIMPLIFIED_DESIGN.md`** - Complete architecture and design ⭐
- **`BACKEND_INTEGRATION_GUIDE.md`** - For backend developers ⭐

**Reference:**
- `API_ENDPOINTS_DOCUMENTATION.md` - Full endpoint docs (legacy)
- `IMPLEMENTATION_PLAN.md` - Implementation details

## 🔌 Simplified Endpoints

**Total: 4-5 endpoints**

1. `POST /classification/classify` - Single classification
2. `POST /classification/batch` - Batch classification
3. `POST /cascade/predict` - Cascade prediction
4. `GET /health` - Health check (optional)
5. `GET /classification/status/{drug}/{target}` - Status check (optional)

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r api_endpoints/requirements.txt

# Run the API server
uvicorn api_endpoints.main:app --reload --port 8000

# Access API docs
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

## 📖 For Backend Developers

See **`BACKEND_INTEGRATION_GUIDE.md`** for:
- Neo4j queries to check if classification/cascade exists
- When to call API endpoints
- Complete code examples
- Integration checklist

## 🔐 Authentication

All endpoints require API key authentication:

```
X-API-Key: your-api-key-here
```

## 📊 Rate Limiting

- Standard endpoints: 100 requests/minute
- AI endpoints: 10 requests/minute
- Statistics endpoints: 50 requests/minute

## 📝 Example Usage

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
headers = {"X-API-Key": "your-api-key"}

# Search drugs
response = requests.get(f"{BASE_URL}/drugs?q=aspirin", headers=headers)
print(response.json())

# Get drug details
response = requests.get(f"{BASE_URL}/drugs/aspirin", headers=headers)
print(response.json())
```

## 🧪 Testing

```bash
# Run tests
pytest api_endpoints/tests/

# Run with coverage
pytest api_endpoints/tests/ --cov=api_endpoints
```

## 📦 Dependencies

See `requirements.txt` for full list.

Key dependencies:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `pydantic` - Data validation
- `neo4j` - Database driver
- `google-generativeai` - AI services

---

**Status:** Planning Phase - Ready for Implementation

