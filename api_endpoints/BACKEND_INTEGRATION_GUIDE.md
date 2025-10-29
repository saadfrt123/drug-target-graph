# Backend Integration Guide

**For:** Backend Development Team  
**Purpose:** Guide for integrating with Drug-Target Graph API  
**Last Updated:** October 16, 2025

---

## 🎯 Architecture Overview

**Your Backend → Neo4j (Direct Queries) → API (Only for AI)**

### **Flow:**
1. Query Neo4j directly for all drug/target/network data
2. Check if classification exists in database
3. If missing → Call AI Classification API
4. Check if cascade predictions exist
5. If missing → Call AI Cascade Prediction API

---

## 📋 Neo4j Queries for Backend

### **1. Get Drug Details**

```cypher
MATCH (d:Drug {name: $drug_name})
RETURN d.name as name, d.moa as moa, d.phase as phase,
       d.smiles as smiles, d.disease_area as disease_area,
       d.indication as indication, d.vendor as vendor
```

### **2. Get Drug Targets (Check Classification Status)**

```cypher
MATCH (d:Drug {name: $drug_name})-[r:TARGETS]->(t:Target)
RETURN t.name as target,
       r.classified as is_classified,
       r.relationship_type as relationship_type,
       r.mechanism as mechanism,
       r.confidence as confidence,
       r.target_class as target_class
ORDER BY t.name
```

**Check if classification needed:**
- If `is_classified IS NULL` → Call API
- If `is_classified = false` → Call API
- If `is_classified = true` → Use existing data ✅

### **3. Get Unclassified Targets (For Batch Processing)**

```cypher
MATCH (d:Drug {name: $drug_name})-[r:TARGETS]->(t:Target)
WHERE r.classified IS NULL OR r.classified = false
RETURN t.name as target_name
LIMIT $limit
```

**Use this before calling:** `POST /classification/batch`

### **4. Get Target Details**

```cypher
MATCH (t:Target {name: $target_name})
OPTIONAL MATCH (d:Drug)-[r:TARGETS]->(t)
RETURN t.name as target,
       collect({
         drug: d.name,
         moa: d.moa,
         phase: d.phase,
         is_classified: r.classified,
         relationship_type: r.relationship_type,
         mechanism: r.mechanism
       }) as drugs
```

### **5. Check Cascade Predictions Exist**

```cypher
MATCH (t:Target {name: $target_name})-[r:AFFECTS_DOWNSTREAM]->(e)
WHERE r.drug_context = $drug_name AND r.predicted_by = "Gemini_API"
RETURN count(r) as cascade_count
```

**If `cascade_count = 0`:**
- Call `POST /cascade/predict`

**If `cascade_count > 0`:**
- Use existing predictions ✅

### **6. Get Cascade Effects (After Prediction)**

```cypher
MATCH (t:Target {name: $target_name})-[r:AFFECTS_DOWNSTREAM]->(e)
WHERE r.drug_context = $drug_name AND r.predicted_by = "Gemini_API"
RETURN e.name as entity_name,
       labels(e)[0] as entity_type,
       r.effect_type as effect_type,
       r.confidence as confidence,
       r.depth as depth,
       r.reasoning as reasoning
ORDER BY r.depth, r.confidence DESC
```

---

## 🔌 API Endpoints

### **Base URL:** `http://api-host:8000/api/v1`

### **1. Classify Single Drug-Target**

**Endpoint:** `POST /classification/classify`

**When to Call:** When `r.classified IS NULL OR r.classified = false`

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
    "reasoning": "...",
    "source": "Gemini_API",
    "timestamp": "2025-10-16T10:00:00Z",
    "stored_in_db": true
  }
}
```

**Note:** Result is automatically stored in Neo4j. No need to store manually.

---

### **2. Batch Classify Multiple Targets**

**Endpoint:** `POST /classification/batch`

**When to Call:** When multiple targets need classification

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

**Note:** All results automatically stored in Neo4j.

---

### **3. Predict Cascade Effects**

**Endpoint:** `POST /cascade/predict`

**When to Call:** When cascade predictions missing (`cascade_count = 0`)

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
    "direct_effects": [...],
    "secondary_effects": [...],
    "tertiary_effects": [...],
    "stored_in_db": true,
    "timestamp": "2025-10-16T10:00:00Z"
  }
}
```

**Note:** Cascade effects automatically stored in Neo4j.

---

## 💻 Code Example (Python)

```python
from neo4j import GraphDatabase
import requests

# Initialize Neo4j connection
driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "password")
)

# API endpoint
API_URL = "http://api-host:8000/api/v1"

def get_drug_targets_with_classification(drug_name: str):
    """Get drug targets, classify if needed"""
    
    with driver.session() as session:
        # Query Neo4j for targets
        result = session.run("""
            MATCH (d:Drug {name: $drug_name})-[r:TARGETS]->(t:Target)
            RETURN t.name as target, r.classified as is_classified
        """, drug_name=drug_name)
        
        targets = result.data()
        
        # Find unclassified targets
        unclassified = [
            t['target'] for t in targets 
            if not t.get('is_classified')
        ]
        
        # Call API if needed
        if unclassified:
            response = requests.post(
                f"{API_URL}/classification/batch",
                json={
                    "drug_name": drug_name,
                    "targets": unclassified
                }
            )
            
            if response.status_code == 200:
                print(f"✅ Classified {len(unclassified)} targets")
        
        # Query again - now with classification
        result = session.run("""
            MATCH (d:Drug {name: $drug_name})-[r:TARGETS]->(t:Target)
            WHERE r.classified = true
            RETURN t.name as target,
                   r.relationship_type as relationship_type,
                   r.mechanism as mechanism,
                   r.confidence as confidence
        """, drug_name=drug_name)
        
        return result.data()

def get_cascade_effects(drug_name: str, target_name: str):
    """Get cascade effects, predict if needed"""
    
    with driver.session() as session:
        # Check if cascade exists
        result = session.run("""
            MATCH (t:Target {name: $target_name})-[r:AFFECTS_DOWNSTREAM]->(e)
            WHERE r.drug_context = $drug_name AND r.predicted_by = "Gemini_API"
            RETURN count(r) as cascade_count
        """, drug_name=drug_name, target_name=target_name)
        
        cascade_count = result.single()['cascade_count']
        
        # Call API if missing
        if cascade_count == 0:
            response = requests.post(
                f"{API_URL}/cascade/predict",
                json={
                    "drug_name": drug_name,
                    "target_name": target_name,
                    "depth": 2
                }
            )
            
            if response.status_code == 200:
                print(f"✅ Predicted cascade effects")
        
        # Get cascade effects
        result = session.run("""
            MATCH (t:Target {name: $target_name})-[r:AFFECTS_DOWNSTREAM]->(e)
            WHERE r.drug_context = $drug_name AND r.predicted_by = "Gemini_API"
            RETURN e.name as entity_name,
                   labels(e)[0] as entity_type,
                   r.effect_type as effect_type,
                   r.confidence as confidence,
                   r.depth as depth
            ORDER BY r.depth, r.confidence DESC
        """, drug_name=drug_name, target_name=target_name)
        
        return result.data()

# Usage
targets = get_drug_targets_with_classification("aspirin")
cascade = get_cascade_effects("aspirin", "PTGS1")
```

---

## 🔐 Authentication

All API endpoints require API key authentication:

**Header:**
```
X-API-Key: your-api-key-here
```

**Error Response (401):**
```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or missing API key"
  }
}
```

---

## ⚡ Rate Limiting

- **Classification endpoints:** 10 requests/minute
- **Cascade endpoints:** 5 requests/minute

**Rate Limit Headers:**
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 9
X-RateLimit-Reset: 1634396400
```

**Error Response (429):**
```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded",
    "retry_after": 60
  }
}
```

---

## ✅ Checklist for Backend Integration

- [ ] Set up Neo4j connection
- [ ] Implement Neo4j queries for drug/target data
- [ ] Add classification check logic
- [ ] Integrate classification API endpoint
- [ ] Add cascade check logic
- [ ] Integrate cascade prediction API endpoint
- [ ] Add error handling
- [ ] Add authentication (API key)
- [ ] Handle rate limiting
- [ ] Test end-to-end flow

---

## 📚 Additional Resources

- **Neo4j Queries:** See `Queries.md` in project root
- **Schema:** See `NEO4J_SCHEMA.md`
- **API Design:** See `api_endpoints/SIMPLIFIED_DESIGN.md`
- **API Docs:** Available at `http://api-host:8000/docs` (Swagger UI)

---

**Questions?** Contact the development team or refer to documentation.

