# FastAPI Deployment - Two Approaches

**Date:** October 16, 2025  
**Purpose:** Compare deployment approaches for different API designs

---

## 🎯 Quick Comparison

| Aspect | Simplified Design | Full API Design |
|--------|------------------|-----------------|
| **Endpoints** | 4-5 | 35+ |
| **Primary Use** | AI-only operations | All operations |
| **Backend Query** | Direct to Neo4j | Through API |
| **Deployment Guide** | `EC2_DEPLOYMENT_GUIDE.md` | Same guide (appendices) |
| **Best For** | Teams querying Neo4j directly | Teams using API as abstraction layer |
| **Complexity** | Low | High |
| **Cost** | ~$34/month | ~$50-70/month |

---

## 📋 Approach 1: Simplified Design (Recommended ✅)

### **Architecture:**
```
Backend → Neo4j (queries directly) → Check if AI needed → Call API
```

### **Endpoints:**
1. `GET /health` - Health check
2. `POST /classification/classify` - Single AI classification
3. `POST /classification/batch` - Batch AI classification
4. `POST /cascade/predict` - AI cascade prediction
5. `GET /classification/status/{drug}/{target}` - Status check (optional)

### **When to Use:**
- ✅ Your backend can connect to Neo4j directly
- ✅ You want minimal API footprint
- ✅ You prefer backend control over data queries
- ✅ You want lower infrastructure costs
- ✅ Your team understands Neo4j/Cypher

### **Backend Flow:**
```python
# 1. Query Neo4j directly
result = neo4j.query("MATCH (d:Drug {name: $name}) RETURN d")
if result['classified'] is None:
    # 2. Call API if classification missing
    api_response = requests.post("/classification/classify", json={...})
    # 3. Query Neo4j again - now has data
    result = neo4j.query("MATCH (d:Drug {name: $name}) RETURN d")
```

### **Documentation:**
- `SIMPLIFIED_DESIGN.md` - Architecture
- `BACKEND_INTEGRATION_GUIDE.md` - Integration guide
- `EC2_DEPLOYMENT_GUIDE.md` - Deployment (Pages 1-50)

---

## 📋 Approach 2: Full API Design

### **Architecture:**
```
Backend → API Endpoints → Neo4j + Gemini
```

### **Endpoints (35+):**

**Drug Endpoints (8):**
- `GET /drugs` - Search drugs
- `GET /drugs/{name}` - Get details
- `GET /drugs/{name}/network` - Network graph
- `GET /drugs/{name}/targets` - Drug's targets
- `GET /drugs/{name}/similar` - Similar drugs
- `GET /drugs/{name}/comparison` - Compare drugs
- `GET /drugs/top/by-targets` - Top drugs
- `GET /drugs/{name}/pathways` - Therapeutic pathways

**Target Endpoints (5):**
- `GET /targets` - Search targets
- `GET /targets/{name}` - Get details
- `GET /targets/{name}/network` - Network graph
- `GET /targets/{name}/drugs` - Drugs targeting this
- `GET /targets/top/by-drugs` - Top targets

**Network Endpoints (4):**
- `GET /network/drug/{name}` - Drug network
- `GET /network/target/{name}` - Target network
- `GET /network/3d` - 3D network
- `GET /network/general` - General network

**Statistics Endpoints (5):**
- `GET /statistics/database` - DB stats
- `GET /statistics/graph` - Graph stats
- `GET /statistics/phase` - Phase stats
- `GET /statistics/moa` - MOA stats
- `GET /statistics/classification` - Classification stats

**AI Endpoints (5):**
- `POST /classification/classify` - Classify
- `GET /classification/{drug}/{target}` - Get classification
- `POST /classification/batch` - Batch classify
- `POST /cascade/predict` - Predict cascade
- `GET /cascade/{drug}/{target}` - Get cascade

**Repurposing Endpoints (3):**
- `GET /repurposing/candidates` - Candidates
- `GET /repurposing/insights` - Insights
- `GET /repurposing/common-targets` - Common targets

**Analysis Endpoints (3):**
- `GET /analysis/similarity/{drug}` - Similarity
- `GET /analysis/therapeutic-class` - Therapeutic class
- `GET /analysis/comparison` - Comparison

**Health Endpoints (3):**
- `GET /health` - API health
- `GET /health/database` - DB health
- `GET /health/ai` - AI health

### **When to Use:**
- ✅ Your backend cannot connect to Neo4j (different VPC, security policies)
- ✅ You need API as abstraction layer
- ✅ Multiple frontend apps share same backend API
- ✅ You want centralized query optimization
- ✅ Your team prefers REST APIs over direct DB access

### **Backend Flow:**
```python
# 1. Call API for everything
drug_info = requests.get(f"/drugs/{name}").json()
targets = requests.get(f"/drugs/{name}/targets").json()

# 2. API queries Neo4j internally
# 3. API returns results
```

### **Documentation:**
- `API_ENDPOINTS_DOCUMENTATION.md` - Full documentation
- `IMPLEMENTATION_PLAN.md` - Implementation details
- `EC2_DEPLOYMENT_GUIDE.md` - Deployment (Pages 51-100)

---

## 🔧 Deployment Infrastructure

### **Both Approaches Use Same Infrastructure:**

- **EC2 Instance:** t3.medium or t3.large
- **Nginx:** Reverse proxy
- **Gunicorn + Uvicorn:** ASGI server
- **Systemd:** Service management
- **SSL:** Let's Encrypt certificates
- **Monitoring:** CloudWatch / Custom logging

### **Differences:**

| Component | Simplified | Full API |
|-----------|-----------|----------|
| **Worker Processes** | 2-3 | 4-6 |
| **Memory (RAM)** | 2-4 GB | 4-8 GB |
| **Concurrent Requests** | ~50/min | ~200/min |
| **Response Time** | 100-200ms | 200-500ms |
| **Cost** | ~$34/month | ~$50-70/month |

---

## 🚀 Deployment Steps

### **For Simplified Design:**

Follow `EC2_DEPLOYMENT_GUIDE.md` directly (Pages 1-50).

Key files to deploy:
- `mechanism_classifier.py` - Classification logic
- `cascade_predictor.py` - Cascade prediction
- `config.py` - Database config
- `.env` - Environment variables

**Deploy command:**
```bash
# Clone repo
git clone https://github.com/your-org/drug-target-graph.git
cd drug-target-graph/api_endpoints

# Create FastAPI main.py (simple structure)
# Install dependencies
pip install -r requirements.txt

# Start with Gunicorn
gunicorn main:app -w 2 --worker-class uvicorn.workers.UvicornWorker
```

### **For Full API Design:**

Follow `EC2_DEPLOYMENT_GUIDE.md` (Pages 51-100).

Key files to deploy:
- All files from Simplified Design PLUS:
- Individual endpoint modules (drugs, targets, network, statistics, etc.)
- Query optimization layer
- Caching layer (Redis recommended)
- Rate limiting middleware

**Deploy command:**
```bash
# Clone repo
git clone https://github.com/your-org/drug-target-graph.git
cd drug-target-graph/api_endpoints

# Create comprehensive FastAPI main.py with all routes
# Install dependencies
pip install -r requirements.txt

# Install Redis for caching
sudo apt install redis-server

# Start with Gunicorn (more workers)
gunicorn main:app -w 4 --worker-class uvicorn.workers.UvicornWorker
```

---

## 💰 Cost Breakdown

### **Simplified Design (~$34/month):**
- EC2 t3.medium: $30
- EBS Storage (30GB): $3
- Data Transfer (10GB): $1

### **Full API Design (~$50-70/month):**
- EC2 t3.large: $60
- EBS Storage (50GB): $5
- Data Transfer (50GB): $5
- Redis (optional): $10

---

## 📊 Performance Comparison

### **Response Times (Average):**

| Operation | Simplified | Full API |
|-----------|-----------|----------|
| **Direct Neo4j Query** | 50-100ms | N/A |
| **API Data Query** | N/A | 200-300ms |
| **AI Classification** | 500-1000ms | 500-1000ms |
| **Network Graph** | 200-500ms | 500-1000ms |

### **Concurrent Requests:**

| Endpoint Type | Simplified | Full API |
|---------------|-----------|----------|
| **Health Check** | 1000/min | 2000/min |
| **Data Endpoints** | N/A | 100/min |
| **AI Endpoints** | 10/min | 10/min |

---

## ✅ Decision Matrix

**Choose Simplified Design if:**
- ✅ Backend has Neo4j access
- ✅ Want faster responses
- ✅ Prefer lower costs
- ✅ Team knows Cypher
- ✅ Want minimal API footprint

**Choose Full API Design if:**
- ✅ Backend cannot access Neo4j
- ✅ Multiple frontend apps
- ✅ Need API abstraction
- ✅ Want centralized optimization
- ✅ Prefer REST APIs

---

## 📚 Further Reading

1. **Simplified Design:**
   - `SIMPLIFIED_DESIGN.md` - Architecture
   - `BACKEND_INTEGRATION_GUIDE.md` - Integration guide
   - `SUMMARY.md` - Overview

2. **Full API Design:**
   - `API_ENDPOINTS_DOCUMENTATION.md` - Complete docs
   - `IMPLEMENTATION_PLAN.md` - Implementation
   - `QUICK_REFERENCE.md` - Quick lookup

3. **Deployment:**
   - `EC2_DEPLOYMENT_GUIDE.md` - Deployment guide
   - `MODULE_STRUCTURE.md` - Code structure

4. **General:**
   - `progress.md` - Development progress
   - `Queries.md` - Neo4j queries
   - `NEO4J_SCHEMA.md` - Database schema

---

**🎯 Recommendation:** Start with **Simplified Design**. Migrate to **Full API** only if architecture requirements demand it.

