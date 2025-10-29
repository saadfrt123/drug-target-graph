# FastAPI Endpoints - Quick Reference

**Project:** Drug-Target Graph Database Explorer API  
**Base URL:** `http://localhost:8000/api/v1`  
**Status:** Planning Phase - Ready for Implementation

---

## 📊 Endpoint Summary

### **Total Endpoints:** 35+

### **By Category:**

| Category | Count | Endpoints |
|----------|-------|-----------|
| Health & Status | 3 | Health check, DB status, AI status |
| Drugs | 8 | Search, details, network, targets, similar, top, MOA search, pathways |
| Targets | 5 | Search, details, network, drugs, top |
| Network | 3 | Drug network, target network, 3D network |
| Statistics | 5 | DB stats, graph stats, phase, MOA, classification |
| AI Classification | 3 | Classify, get, batch classify |
| AI Cascade | 2 | Predict, get cascade |
| Repurposing | 3 | Candidates, insights, common targets |
| Analysis | 3 | Similarity, therapeutic class, comparison |

---

## 🔑 Key Endpoints

### **Most Used:**

1. **Search Drugs**
   ```
   GET /drugs?q=aspirin&limit=10
   ```

2. **Get Drug Details**
   ```
   GET /drugs/aspirin
   ```

3. **Get Drug Network**
   ```
   GET /drugs/aspirin/network
   ```

4. **Classify Relationship**
   ```
   POST /classification/classify
   Body: {"drug_name": "aspirin", "target_name": "PTGS1"}
   ```

5. **Search Targets**
   ```
   GET /targets?q=PTGS1&limit=10
   ```

---

## 📁 Folder Structure

```
api_endpoints/
├── main.py                    # FastAPI app
├── config.py                  # Configuration
├── dependencies.py            # Shared dependencies
├── routers/                   # Endpoint routes
│   ├── health.py
│   ├── drugs.py
│   ├── targets.py
│   ├── network.py
│   ├── statistics.py
│   ├── classification.py
│   ├── cascade.py
│   ├── repurposing.py
│   └── analysis.py
├── services/                  # Business logic
│   ├── database.py
│   ├── drug_service.py
│   └── ...
├── models/                    # Pydantic models
│   ├── requests.py
│   └── responses.py
└── utils/                     # Utilities
    ├── errors.py
    └── auth.py
```

---

## 🚀 Quick Start

```bash
# Install
pip install -r api_endpoints/requirements.txt

# Run
uvicorn api_endpoints.main:app --reload --port 8000

# Access docs
# Swagger: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

---

## 📚 Documentation Files

1. **API_ENDPOINTS_DOCUMENTATION.md** - Complete endpoint reference
2. **IMPLEMENTATION_PLAN.md** - Implementation guide
3. **MODULE_STRUCTURE.md** - Code organization
4. **README.md** - Quick start guide

---

**Status:** ✅ Planning Complete - Ready for Implementation

