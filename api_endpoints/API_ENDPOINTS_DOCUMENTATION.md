# FastAPI Endpoints Documentation

**Project:** Drug-Target Graph Database Explorer  
**API Framework:** FastAPI  
**Design:** Simplified - AI endpoints only (backend queries Neo4j directly)  
**Last Updated:** October 16, 2025  
**Base URL:** `http://localhost:8000/api/v1`

> **⚠️ IMPORTANT:** This design has been simplified. See `SIMPLIFIED_DESIGN.md` for the current architecture.
> 
> **Backend Flow:** Backend queries Neo4j directly for all data. API endpoints are ONLY called when AI classification/prediction is needed.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Simplified Endpoints](#simplified-endpoints)
4. [How Backend Uses API](#how-backend-uses-api)
5. [Legacy Documentation](#legacy-documentation)

---

## Overview

This FastAPI wrapper provides **AI-only endpoints** that are called conditionally by the backend:
- Backend queries Neo4j directly for all drug/target/network data
- API is called ONLY when classification/cascade prediction is needed
- Minimal API surface: 4-5 endpoints total

**See `SIMPLIFIED_DESIGN.md` for complete details.**

### Key Features:
- ✅ **RESTful Design** - Standard HTTP methods and status codes
- ✅ **OpenAPI Documentation** - Auto-generated Swagger/ReDoc docs
- ✅ **Request Validation** - Pydantic models for input validation
- ✅ **Error Handling** - Standardized error responses
- ✅ **Response Models** - Consistent JSON response formats
- ✅ **Type Safety** - Full type hints throughout

---

## API Structure

```
/api/v1/
├── /health              # Health check endpoints
├── /drugs               # Drug-related endpoints
├── /targets             # Target-related endpoints
├── /network             # Network visualization endpoints
├── /statistics          # Statistics & analytics endpoints
├── /classification      # AI mechanism classification endpoints
├── /cascade             # AI cascade prediction endpoints
├── /repurposing         # Drug repurposing endpoints
└── /analysis            # Analysis & comparison endpoints
```

---

## Endpoint Categories

### 1. Health & Status Endpoints
- `GET /health` - API health check
- `GET /health/database` - Database connection status
- `GET /health/ai` - AI service status (Gemini API)

### 2. Drug Endpoints (`/drugs`)
- `GET /drugs` - Search drugs
- `GET /drugs/{drug_name}` - Get drug details
- `GET /drugs/{drug_name}/network` - Get drug network graph
- `GET /drugs/{drug_name}/targets` - Get drug's targets
- `GET /drugs/{drug_name}/similar` - Find similar drugs
- `GET /drugs/{drug_name}/comparison` - Compare two drugs
- `GET /drugs/top/by-targets` - Top drugs by target count
- `GET /drugs/search/moa` - Search drugs by MOA
- `GET /drugs/{drug_name}/pathways` - Get therapeutic pathways

### 3. Target Endpoints (`/targets`)
- `GET /targets` - Search targets
- `GET /targets/{target_name}` - Get target details
- `GET /targets/{target_name}/network` - Get target network graph
- `GET /targets/{target_name}/drugs` - Get drugs targeting this target
- `GET /targets/top/by-drugs` - Top targets by drug count

### 4. Network Visualization Endpoints (`/network`)
- `GET /network/drug/{drug_name}` - Get drug network data
- `GET /network/target/{target_name}` - Get target network data
- `GET /network/3d` - Get 3D network data
- `GET /network/general` - Get general network data

### 5. Statistics Endpoints (`/statistics`)
- `GET /statistics/database` - Database statistics
- `GET /statistics/graph` - Graph statistics
- `GET /statistics/phase` - Drug phase statistics
- `GET /statistics/moa` - MOA statistics
- `GET /statistics/classification` - Classification statistics

### 6. AI Classification Endpoints (`/classification`)
- `POST /classification/classify` - Classify drug-target relationship
- `GET /classification/{drug_name}/{target_name}` - Get existing classification
- `POST /classification/batch` - Batch classify multiple relationships

### 7. AI Cascade Prediction Endpoints (`/cascade`)
- `POST /cascade/predict` - Predict cascade effects
- `GET /cascade/{drug_name}/{target_name}` - Get cascade predictions

### 8. Repurposing Endpoints (`/repurposing`)
- `GET /repurposing/candidates` - Get repurposing candidates
- `GET /repurposing/insights` - Get repurposing insights
- `GET /repurposing/common-targets` - Find common targets between drugs

### 9. Analysis Endpoints (`/analysis`)
- `GET /analysis/similarity/{drug_name}` - Drug similarity analysis
- `GET /analysis/therapeutic-class` - Therapeutic class analysis
- `GET /analysis/comparison` - Compare two drugs

---

## Endpoint Details

### Health & Status

#### `GET /health`
**Description:** Check API health status  
**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-16T10:00:00Z",
  "version": "1.0.0"
}
```

#### `GET /health/database`
**Description:** Check Neo4j database connection  
**Response:**
```json
{
  "status": "connected",
  "database": "neo4j",
  "node_count": 1234,
  "relationship_count": 5678
}
```

#### `GET /health/ai`
**Description:** Check AI service status (Gemini API)  
**Response:**
```json
{
  "status": "available",
  "classifier": "ready",
  "cascade_predictor": "ready",
  "gemini_model": "gemini-1.5-flash"
}
```

---

### Drug Endpoints

#### `GET /drugs`
**Description:** Search drugs by name  
**Query Parameters:**
- `q` (string, required): Search term
- `limit` (int, optional, default=20): Maximum results

**Response:**
```json
{
  "results": [
    {
      "drug": "aspirin",
      "moa": "COX inhibitor",
      "phase": "Approved"
    }
  ],
  "total": 1,
  "limit": 20
}
```

#### `GET /drugs/{drug_name}`
**Description:** Get comprehensive drug details  
**Path Parameters:**
- `drug_name` (string, required): Drug name

**Response:**
```json
{
  "drug_info": {
    "name": "aspirin",
    "moa": "COX inhibitor",
    "phase": "Approved",
    "smiles": "CC(=O)Oc1ccccc1C(=O)O",
    "disease_area": "Cardiovascular",
    "indication": "Pain relief",
    "vendor": "PharmaCorp",
    "purity": 99.5
  },
  "targets": ["PTGS1", "PTGS2"],
  "disease_areas": ["Cardiovascular"],
  "indications": ["Pain relief"],
  "vendors": ["PharmaCorp"]
}
```

#### `GET /drugs/{drug_name}/network`
**Description:** Get drug-target network graph data  
**Path Parameters:**
- `drug_name` (string, required): Drug name

**Query Parameters:**
- `depth` (int, optional, default=1): Network depth

**Response:**
```json
{
  "nodes": [
    {
      "id": 1,
      "label": "aspirin",
      "type": "central_drug",
      "moa": "COX inhibitor",
      "phase": "Approved"
    },
    {
      "id": 2,
      "label": "PTGS1",
      "type": "primary_target",
      "relationship_type": "Primary/On-Target"
    }
  ],
  "edges": [
    {
      "source": 1,
      "target": 2,
      "type": "TARGETS",
      "mechanism": "Inhibitor"
    }
  ]
}
```

#### `GET /drugs/{drug_name}/targets`
**Description:** Get all targets for a drug  
**Path Parameters:**
- `drug_name` (string, required): Drug name

**Response:**
```json
{
  "drug": "aspirin",
  "targets": [
    {
      "target": "PTGS1",
      "relationship_type": "Primary/On-Target",
      "mechanism": "Inhibitor",
      "target_class": "Enzyme",
      "confidence": 0.95
    }
  ],
  "total": 19
}
```

#### `GET /drugs/{drug_name}/similar`
**Description:** Find similar drugs by MOA  
**Path Parameters:**
- `drug_name` (string, required): Drug name

**Query Parameters:**
- `limit` (int, optional, default=10): Maximum results

**Response:**
```json
{
  "drug": "aspirin",
  "similar_drugs": [
    {
      "drug": "ibuprofen",
      "moa": "COX inhibitor",
      "phase": "Approved",
      "similarity_score": 0.95
    }
  ]
}
```

#### `GET /drugs/top/by-targets`
**Description:** Get top drugs by target count  
**Query Parameters:**
- `limit` (int, optional, default=10): Maximum results

**Response:**
```json
{
  "results": [
    {
      "drug": "aspirin",
      "moa": "COX inhibitor",
      "phase": "Approved",
      "target_count": 19
    }
  ]
}
```

#### `GET /drugs/search/moa`
**Description:** Search drugs by mechanism of action  
**Query Parameters:**
- `moa` (string, required): MOA search term
- `limit` (int, optional, default=20): Maximum results

**Response:**
```json
{
  "results": [
    {
      "drug": "aspirin",
      "moa": "COX inhibitor",
      "phase": "Approved"
    }
  ],
  "total": 1
}
```

---

### Target Endpoints

#### `GET /targets`
**Description:** Search targets by name  
**Query Parameters:**
- `q` (string, required): Search term
- `limit` (int, optional, default=20): Maximum results

**Response:**
```json
{
  "results": [
    {
      "target": "PTGS1"
    }
  ],
  "total": 1
}
```

#### `GET /targets/{target_name}`
**Description:** Get comprehensive target details  
**Path Parameters:**
- `target_name` (string, required): Target name

**Response:**
```json
{
  "target_info": {
    "name": "PTGS1"
  },
  "drugs": [
    {
      "drug": "aspirin",
      "moa": "COX inhibitor",
      "phase": "Approved",
      "relationship_type": "Primary/On-Target"
    }
  ],
  "total_drugs": 15
}
```

#### `GET /targets/{target_name}/network`
**Description:** Get target network graph data  
**Path Parameters:**
- `target_name` (string, required): Target name

**Query Parameters:**
- `depth` (int, optional, default=1): Network depth

**Response:**
```json
{
  "nodes": [...],
  "edges": [...],
  "central_target": "PTGS1"
}
```

#### `GET /targets/{target_name}/drugs`
**Description:** Get all drugs targeting this target  
**Path Parameters:**
- `target_name` (string, required): Target name

**Response:**
```json
{
  "target": "PTGS1",
  "drugs": [
    {
      "drug": "aspirin",
      "moa": "COX inhibitor",
      "phase": "Approved"
    }
  ],
  "total": 15
}
```

#### `GET /targets/top/by-drugs`
**Description:** Get top targets by drug count  
**Query Parameters:**
- `limit` (int, optional, default=10): Maximum results

**Response:**
```json
{
  "results": [
    {
      "target": "PTGS1",
      "drug_count": 15,
      "moa": "COX inhibitor",
      "unique_moas": 3
    }
  ]
}
```

---

### Network Visualization Endpoints

#### `GET /network/drug/{drug_name}`
**Description:** Get drug network data for visualization  
**Path Parameters:**
- `drug_name` (string, required): Drug name

**Query Parameters:**
- `depth` (int, optional, default=1): Network depth

**Response:**
```json
{
  "nodes": [...],
  "edges": [...],
  "network_type": "drug_centered"
}
```

#### `GET /network/target/{target_name}`
**Description:** Get target network data for visualization  
**Path Parameters:**
- `target_name` (string, required): Target name

**Response:**
```json
{
  "nodes": [...],
  "edges": [...],
  "network_type": "target_centered"
}
```

#### `GET /network/3d`
**Description:** Get 3D network visualization data  
**Query Parameters:**
- `limit` (int, optional, default=30): Maximum nodes

**Response:**
```json
{
  "nodes": [...],
  "edges": [...],
  "total_nodes": 30
}
```

---

### Statistics Endpoints

#### `GET /statistics/database`
**Description:** Get database statistics  
**Response:**
```json
{
  "drug_count": 1234,
  "target_count": 567,
  "relationship_count": 3456,
  "disease_area_count": 12,
  "indication_count": 89
}
```

#### `GET /statistics/graph`
**Description:** Get graph statistics  
**Response:**
```json
{
  "drug_count": 1234,
  "target_count": 567,
  "relationship_count": 3456,
  "top_drugs": [...],
  "top_targets": [...]
}
```

#### `GET /statistics/phase`
**Description:** Get drug phase distribution  
**Response:**
```json
{
  "results": [
    {
      "phase": "Approved",
      "count": 500
    },
    {
      "phase": "Phase III",
      "count": 200
    }
  ]
}
```

#### `GET /statistics/moa`
**Description:** Get MOA distribution  
**Response:**
```json
{
  "results": [
    {
      "moa": "COX inhibitor",
      "count": 50
    }
  ]
}
```

#### `GET /statistics/classification`
**Description:** Get classification statistics  
**Response:**
```json
{
  "total_relationships": 3456,
  "classified_relationships": 1234,
  "unclassified_relationships": 2222,
  "classification_progress": 0.36
}
```

---

### AI Classification Endpoints

#### `POST /classification/classify`
**Description:** Classify drug-target relationship using AI  
**Request Body:**
```json
{
  "drug_name": "aspirin",
  "target_name": "PTGS1",
  "force_reclassify": false,
  "additional_context": "Optional context"
}
```

**Response:**
```json
{
  "drug_name": "aspirin",
  "target_name": "PTGS1",
  "relationship_type": "Primary/On-Target",
  "target_class": "Enzyme",
  "target_subclass": "Oxidoreductase",
  "mechanism": "Inhibitor",
  "confidence": 0.95,
  "reasoning": "Aspirin is a cyclooxygenase inhibitor...",
  "source": "Gemini_API",
  "timestamp": "2025-10-16T10:00:00Z"
}
```

#### `GET /classification/{drug_name}/{target_name}`
**Description:** Get existing classification  
**Path Parameters:**
- `drug_name` (string, required): Drug name
- `target_name` (string, required): Target name

**Response:**
```json
{
  "drug_name": "aspirin",
  "target_name": "PTGS1",
  "relationship_type": "Primary/On-Target",
  "mechanism": "Inhibitor",
  "confidence": 0.95,
  "timestamp": "2025-10-16T10:00:00Z"
}
```

#### `POST /classification/batch`
**Description:** Batch classify multiple drug-target relationships  
**Request Body:**
```json
{
  "relationships": [
    {
      "drug_name": "aspirin",
      "target_name": "PTGS1"
    },
    {
      "drug_name": "aspirin",
      "target_name": "PTGS2"
    }
  ]
}
```

**Response:**
```json
{
  "results": [
    {
      "drug_name": "aspirin",
      "target_name": "PTGS1",
      "status": "success",
      "classification": {...}
    }
  ],
  "total": 2,
  "successful": 2,
  "failed": 0
}
```

---

### AI Cascade Prediction Endpoints

#### `POST /cascade/predict`
**Description:** Predict biological cascade effects  
**Request Body:**
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
  "prediction_timestamp": "2025-10-16T10:00:00Z",
  "total_confidence": 0.88
}
```

#### `GET /cascade/{drug_name}/{target_name}`
**Description:** Get existing cascade predictions  
**Path Parameters:**
- `drug_name` (string, required): Drug name
- `target_name` (string, required): Target name

**Response:**
```json
{
  "drug_name": "aspirin",
  "target_name": "PTGS1",
  "predictions": {...},
  "timestamp": "2025-10-16T10:00:00Z"
}
```

---

### Repurposing Endpoints

#### `GET /repurposing/candidates`
**Description:** Get drug repurposing candidates  
**Query Parameters:**
- `drug_name` (string, optional): Specific drug name
- `limit` (int, optional, default=15): Maximum results

**Response:**
```json
{
  "results": [
    {
      "drug": "aspirin",
      "targets": ["PTGS1", "PTGS2"],
      "repurposing_score": 0.85,
      "potential_indications": ["Cardiovascular", "Cancer"]
    }
  ]
}
```

#### `GET /repurposing/insights`
**Description:** Get repurposing insights  
**Response:**
```json
{
  "target_based_candidates": [...],
  "moa_based_candidates": [...],
  "pathway_based_candidates": [...]
}
```

#### `GET /repurposing/common-targets`
**Description:** Find common targets between drugs  
**Query Parameters:**
- `drug1` (string, required): First drug name
- `drug2` (string, required): Second drug name

**Response:**
```json
{
  "drug1": "aspirin",
  "drug2": "ibuprofen",
  "common_targets": [
    {
      "target": "PTGS1",
      "drug1_relationship": "Primary/On-Target",
      "drug2_relationship": "Primary/On-Target"
    }
  ],
  "common_count": 2
}
```

---

### Analysis Endpoints

#### `GET /analysis/similarity/{drug_name}`
**Description:** Get drug similarity analysis  
**Path Parameters:**
- `drug_name` (string, required): Drug name

**Response:**
```json
{
  "drug": "aspirin",
  "similar_drugs": [...],
  "similarity_factors": {
    "moa_similarity": 0.95,
    "target_overlap": 0.80
  }
}
```

#### `GET /analysis/therapeutic-class`
**Description:** Get therapeutic class analysis  
**Query Parameters:**
- `class_name` (string, optional): Specific class name

**Response:**
```json
{
  "class_name": "COX inhibitors",
  "drugs": [...],
  "common_targets": [...],
  "analysis": {...}
}
```

#### `GET /analysis/comparison`
**Description:** Compare two drugs  
**Query Parameters:**
- `drug1` (string, required): First drug name
- `drug2` (string, required): Second drug name

**Response:**
```json
{
  "drug1": "aspirin",
  "drug2": "ibuprofen",
  "common_targets": [...],
  "unique_targets_drug1": [...],
  "unique_targets_drug2": [...],
  "similarity_score": 0.85
}
```

---

## Request/Response Models

### Standard Response Format

All endpoints follow a consistent response format:

**Success Response:**
```json
{
  "success": true,
  "data": {...},
  "message": "Operation completed successfully"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description",
    "details": {...}
  }
}
```

### Pagination

Endpoints returning lists support pagination:

**Query Parameters:**
- `page` (int, optional, default=1): Page number
- `limit` (int, optional, default=20): Items per page

**Response:**
```json
{
  "results": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "pages": 5
  }
}
```

---

## Error Handling

### HTTP Status Codes

- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Invalid request
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Service unavailable

### Error Codes

- `DRUG_NOT_FOUND` - Drug doesn't exist
- `TARGET_NOT_FOUND` - Target doesn't exist
- `DATABASE_ERROR` - Database operation failed
- `AI_SERVICE_ERROR` - AI service unavailable
- `VALIDATION_ERROR` - Request validation failed
- `RATE_LIMIT_EXCEEDED` - Rate limit exceeded

---

## Authentication

### API Key Authentication

All endpoints require API key authentication:

**Header:**
```
X-API-Key: your-api-key-here
```

**Response (401 Unauthorized):**
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

## Rate Limiting

### Limits

- **Standard Endpoints:** 100 requests/minute
- **AI Endpoints:** 10 requests/minute
- **Statistics Endpoints:** 50 requests/minute

### Rate Limit Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1634396400
```

### Rate Limit Exceeded Response

**Status:** `429 Too Many Requests`

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please try again later.",
    "retry_after": 60
  }
}
```

---

## Example Usage

### Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"
API_KEY = "your-api-key"

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

# Search drugs
response = requests.get(
    f"{BASE_URL}/drugs?q=aspirin&limit=10",
    headers=headers
)
drugs = response.json()

# Get drug details
response = requests.get(
    f"{BASE_URL}/drugs/aspirin",
    headers=headers
)
drug_details = response.json()

# Classify relationship
response = requests.post(
    f"{BASE_URL}/classification/classify",
    headers=headers,
    json={
        "drug_name": "aspirin",
        "target_name": "PTGS1"
    }
)
classification = response.json()
```

### cURL Example

```bash
# Search drugs
curl -X GET "http://localhost:8000/api/v1/drugs?q=aspirin&limit=10" \
  -H "X-API-Key: your-api-key"

# Get drug details
curl -X GET "http://localhost:8000/api/v1/drugs/aspirin" \
  -H "X-API-Key: your-api-key"

# Classify relationship
curl -X POST "http://localhost:8000/api/v1/classification/classify" \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "drug_name": "aspirin",
    "target_name": "PTGS1"
  }'
```

---

## Endpoint Summary Table

| Method | Endpoint | Description | Category |
|--------|----------|-------------|----------|
| GET | `/health` | API health check | Health |
| GET | `/health/database` | Database status | Health |
| GET | `/health/ai` | AI service status | Health |
| GET | `/drugs` | Search drugs | Drugs |
| GET | `/drugs/{drug_name}` | Get drug details | Drugs |
| GET | `/drugs/{drug_name}/network` | Get drug network | Drugs |
| GET | `/drugs/{drug_name}/targets` | Get drug targets | Drugs |
| GET | `/drugs/{drug_name}/similar` | Find similar drugs | Drugs |
| GET | `/drugs/top/by-targets` | Top drugs by targets | Drugs |
| GET | `/drugs/search/moa` | Search by MOA | Drugs |
| GET | `/targets` | Search targets | Targets |
| GET | `/targets/{target_name}` | Get target details | Targets |
| GET | `/targets/{target_name}/network` | Get target network | Targets |
| GET | `/targets/{target_name}/drugs` | Get target drugs | Targets |
| GET | `/targets/top/by-drugs` | Top targets by drugs | Targets |
| GET | `/network/drug/{drug_name}` | Drug network data | Network |
| GET | `/network/target/{target_name}` | Target network data | Network |
| GET | `/network/3d` | 3D network data | Network |
| GET | `/statistics/database` | Database stats | Statistics |
| GET | `/statistics/graph` | Graph stats | Statistics |
| GET | `/statistics/phase` | Phase stats | Statistics |
| GET | `/statistics/moa` | MOA stats | Statistics |
| POST | `/classification/classify` | Classify relationship | AI |
| GET | `/classification/{drug}/{target}` | Get classification | AI |
| POST | `/classification/batch` | Batch classify | AI |
| POST | `/cascade/predict` | Predict cascade | AI |
| GET | `/cascade/{drug}/{target}` | Get cascade | AI |
| GET | `/repurposing/candidates` | Repurposing candidates | Repurposing |
| GET | `/repurposing/insights` | Repurposing insights | Repurposing |
| GET | `/repurposing/common-targets` | Common targets | Repurposing |
| GET | `/analysis/similarity/{drug}` | Similarity analysis | Analysis |
| GET | `/analysis/comparison` | Drug comparison | Analysis |

**Total Endpoints:** 35+

---

## Implementation Notes

1. **Database Connection:** All endpoints use the same Neo4j connection pool
2. **Caching:** Classification and network data are cached for performance
3. **Background Processing:** Batch operations run in background threads
4. **Error Recovery:** Graceful error handling with fallbacks
5. **Logging:** All API calls are logged for debugging

---

**Last Updated:** October 16, 2025  
**API Version:** 1.0.0  
**Status:** Planning Phase

