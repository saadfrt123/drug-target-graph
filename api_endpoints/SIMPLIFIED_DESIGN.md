# FastAPI Endpoints - Simplified Design

**Project:** Drug-Target Graph Database Explorer API  
**Design Philosophy:** Backend queries Neo4j directly; API only for AI operations  
**Last Updated:** October 16, 2025

---

## 🎯 Architecture Overview

### **Backend Flow:**

```
Backend (Your Application)
    ↓
1. Query Neo4j directly for all data
    ↓
2. Check if classification exists: r.classified = true?
    ↓
3. If NO → Call AI Classification Endpoint
    ↓
4. Check if cascade exists: AFFECTS_DOWNSTREAM relationships?
    ↓
5. If NO → Call AI Cascade Prediction Endpoint
```

### **Key Principle:**
- **Backend queries Neo4j directly** for all drug/target/network data
- **API endpoints are ONLY called** when AI classification/prediction is needed
- **Minimal API surface** - only AI operations

---

## 📋 Endpoint List (Simplified)

### **Total Endpoints: 4-5**

1. **Health Check** (Optional)
   - `GET /health` - API health status

2. **AI Classification** (Required)
   - `POST /classification/classify` - Classify single drug-target relationship
   - `POST /classification/batch` - Batch classify multiple relationships

3. **AI Cascade Prediction** (Required)
   - `POST /cascade/predict` - Predict cascade effects

4. **Utility** (Optional)
   - `GET /classification/status/{drug}/{target}` - Check if classification exists

---

## 🔍 How Backend Checks if Classification is Needed

### **Neo4j Query to Check:**

```cypher
MATCH (d:Drug {name: $drug_name})-[r:TARGETS]->(t:Target {name: $target_name})
RETURN r.classified as is_classified
```

**If `is_classified IS NULL OR is_classified = false`:**
- Call `POST /classification/classify`

**If `is_classified = true`:**
- Use existing classification from Neo4j (no API call needed)

### **Check Multiple Targets:**

```cypher
MATCH (d:Drug {name: $drug_name})-[r:TARGETS]->(t:Target)
WHERE r.classified IS NULL OR r.classified = false
RETURN t.name as target_name
LIMIT 10
```

**Then call:** `POST /classification/batch` with list of targets

---

## 🔍 How Backend Checks if Cascade is Needed

### **Neo4j Query to Check:**

```cypher
MATCH (t:Target {name: $target_name})-[r:AFFECTS_DOWNSTREAM]->(e)
WHERE r.drug_context = $drug_name AND r.predicted_by = "Gemini_API"
RETURN count(r) as cascade_count
```

**If `cascade_count = 0`:**
- Call `POST /cascade/predict`

**If `cascade_count > 0`:**
- Use existing cascade data from Neo4j (no API call needed)

---

## 📝 Endpoint Details

### 1. `POST /classification/classify`

**Purpose:** Classify a single drug-target relationship using AI

**When Called:** When `r.classified IS NULL OR r.classified = false`

**Request:**
```json
{
  "drug_name": "aspirin",
  "target_name": "PTGS1",
  "additional_context": "Optional context"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "drug_name": "aspirin",
    "target_name": "PTGS1",
    "relationship_type": "Primary/On-Target",
    "target_class": "Protein",
    "target_subclass": "Enzyme",
    "mechanism": "Irreversible Inhibitor",
    "confidence": 0.95,
    "reasoning": "Aspirin irreversibly acetylates COX-1...",
    "source": "Gemini_API",
    "timestamp": "2025-10-16T10:00:00Z",
    "stored_in_db": true
  }
}
```

**What API Does:**
1. Calls Gemini API to classify relationship
2. Stores result in Neo4j (`r.classified = true`)
3. Returns classification data

---

### 2. `POST /classification/batch`

**Purpose:** Batch classify multiple drug-target relationships

**When Called:** When multiple targets need classification

**Request:**
```json
{
  "drug_name": "aspirin",
  "targets": ["PTGS1", "PTGS2", "NFKBIA"],
  "additional_context": "Optional context"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "drug_name": "aspirin",
    "total": 3,
    "successful": 3,
    "failed": 0,
    "results": [
      {
        "target_name": "PTGS1",
        "status": "success",
        "classification": {...}
      }
    ]
  }
}
```

---

### 3. `POST /cascade/predict`

**Purpose:** Predict biological cascade effects

**When Called:** When `AFFECTS_DOWNSTREAM` relationships missing for drug-target pair

**Request:**
```json
{
  "drug_name": "aspirin",
  "target_name": "PTGS1",
  "depth": 2,
  "additional_context": "Optional context"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "drug_name": "aspirin",
    "target_name": "PTGS1",
    "direct_effects": [
      {
        "entity_name": "Prostaglandin synthesis",
        "entity_type": "Pathway",
        "effect_type": "inhibits",
        "confidence": 0.92,
        "reasoning": "...",
        "depth": 1
      }
    ],
    "secondary_effects": [...],
    "tertiary_effects": [...],
    "stored_in_db": true,
    "timestamp": "2025-10-16T10:00:00Z"
  }
}
```

**What API Does:**
1. Calls Gemini API to predict cascade
2. Creates nodes: `Pathway`, `Gene`, `Metabolite`, etc.
3. Creates `AFFECTS_DOWNSTREAM` relationships
4. Stores `drug_context` and `predicted_by = "Gemini_API"`

---

### 4. `GET /health` (Optional)

**Purpose:** Check API health

**Response:**
```json
{
  "status": "healthy",
  "gemini_api": "available",
  "neo4j": "connected",
  "timestamp": "2025-10-16T10:00:00Z"
}
```

---

### 5. `GET /classification/status/{drug}/{target}` (Optional)

**Purpose:** Check if classification exists (alternative to querying Neo4j)

**Response:**
```json
{
  "drug_name": "aspirin",
  "target_name": "PTGS1",
  "exists": true,
  "classification": {...}
}
```

---

## 🔄 Backend Implementation Example

### **Python Example:**

```python
from neo4j import GraphDatabase
import requests

# Backend queries Neo4j directly
driver = GraphDatabase.driver(uri, auth=(user, password))

# Get drug targets
with driver.session() as session:
    result = session.run("""
        MATCH (d:Drug {name: $drug_name})-[r:TARGETS]->(t:Target)
        RETURN t.name as target, r.classified as is_classified
    """, drug_name="aspirin")
    
    targets = result.data()

# Check which need classification
unclassified = [t for t in targets if not t.get('is_classified')]

# Call API only if needed
if unclassified:
    response = requests.post(
        "http://api:8000/classification/batch",
        json={
            "drug_name": "aspirin",
            "targets": [t['target'] for t in unclassified]
        }
    )
    # API stores results in Neo4j automatically
    
# Now query Neo4j again - classification will be there
with driver.session() as session:
    result = session.run("""
        MATCH (d:Drug {name: $drug_name})-[r:TARGETS]->(t:Target)
        WHERE r.classified = true
        RETURN t.name, r.mechanism, r.confidence
    """, drug_name="aspirin")
    
    classified_targets = result.data()
```

---

## 📊 Endpoint Summary

| Endpoint | Method | Purpose | When Called |
|----------|--------|---------|-------------|
| `/health` | GET | Health check | Optional |
| `/classification/classify` | POST | Single classification | When `r.classified = false` |
| `/classification/batch` | POST | Batch classification | When multiple need classification |
| `/cascade/predict` | POST | Predict cascade | When cascade missing |
| `/classification/status/{drug}/{target}` | GET | Check status | Optional |

**Total:** 4-5 endpoints (vs 35+ in original design)

---

## 🎯 Key Benefits

1. **Minimal API Surface** - Only AI operations
2. **Backend Controls Flow** - Queries Neo4j directly
3. **On-Demand AI** - Only called when needed
4. **Simple Integration** - Backend just needs to check Neo4j, then call API if needed
5. **Efficient** - No redundant data fetching

---

## 📋 Implementation Checklist

- [ ] Create FastAPI app with minimal structure
- [ ] Implement `/classification/classify` endpoint
- [ ] Implement `/classification/batch` endpoint
- [ ] Implement `/cascade/predict` endpoint
- [ ] Add health check endpoint
- [ ] Add error handling
- [ ] Add authentication (API key)
- [ ] Add rate limiting (for AI endpoints)
- [ ] Write tests
- [ ] Document Neo4j queries for backend team

---

**Status:** ✅ Design Complete - Ready for Implementation

