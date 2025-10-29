# FastAPI Endpoints Implementation Plan

**Project:** Drug-Target Graph Database Explorer API  
**Framework:** FastAPI  
**Status:** Planning Phase  
**Last Updated:** October 16, 2025

---

## 📁 Folder Structure

```
api_endpoints/
├── __init__.py
├── main.py                    # FastAPI app entry point
├── config.py                  # API configuration
├── dependencies.py            # Shared dependencies (DB, auth)
├── models/
│   ├── __init__.py
│   ├── requests.py           # Pydantic request models
│   ├── responses.py           # Pydantic response models
│   └── common.py              # Common models
├── routers/
│   ├── __init__.py
│   ├── health.py             # Health check endpoints
│   ├── drugs.py              # Drug endpoints
│   ├── targets.py            # Target endpoints
│   ├── network.py            # Network visualization endpoints
│   ├── statistics.py         # Statistics endpoints
│   ├── classification.py     # AI classification endpoints
│   ├── cascade.py            # AI cascade prediction endpoints
│   ├── repurposing.py        # Repurposing endpoints
│   └── analysis.py           # Analysis endpoints
├── services/
│   ├── __init__.py
│   ├── database.py           # Database service wrapper
│   ├── drug_service.py       # Drug-related business logic
│   ├── target_service.py     # Target-related business logic
│   ├── classification_service.py  # Classification logic
│   └── cascade_service.py    # Cascade prediction logic
├── utils/
│   ├── __init__.py
│   ├── errors.py             # Error handling utilities
│   ├── auth.py               # Authentication utilities
│   └── rate_limit.py         # Rate limiting utilities
├── tests/
│   ├── __init__.py
│   ├── test_drugs.py
│   ├── test_targets.py
│   └── test_classification.py
├── requirements.txt
└── README.md
```

---

## 🔧 Implementation Details

### 1. Main Application (`main.py`)

```python
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from api_endpoints.routers import (
    health, drugs, targets, network, statistics,
    classification, cascade, repurposing, analysis
)

app = FastAPI(
    title="Drug-Target Graph Database API",
    description="RESTful API for Drug-Target Graph Database Explorer",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(drugs.router, prefix="/api/v1/drugs", tags=["Drugs"])
app.include_router(targets.router, prefix="/api/v1/targets", tags=["Targets"])
app.include_router(network.router, prefix="/api/v1/network", tags=["Network"])
app.include_router(statistics.router, prefix="/api/v1/statistics", tags=["Statistics"])
app.include_router(classification.router, prefix="/api/v1/classification", tags=["AI Classification"])
app.include_router(cascade.router, prefix="/api/v1/cascade", tags=["AI Cascade"])
app.include_router(repurposing.router, prefix="/api/v1/repurposing", tags=["Repurposing"])
app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["Analysis"])
```

### 2. Database Service (`services/database.py`)

Wraps the existing `DrugTargetGraphApp` class for API use:

```python
from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE
from streamlit_app import DrugTargetGraphApp
from mechanism_classifier import DrugTargetMechanismClassifier
from cascade_predictor import BiologicalCascadePredictor

class DatabaseService:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            NEO4J_URI, 
            auth=(NEO4J_USER, NEO4J_PASSWORD)
        )
        self.database = NEO4J_DATABASE
        
        # Initialize app instance (without Streamlit dependencies)
        self.app = DrugTargetGraphApp()
        self.app.driver = self.driver
        self.app.database = self.database
        
        # Initialize AI services
        self.classifier = DrugTargetMechanismClassifier(...)
        self.cascade_predictor = BiologicalCascadePredictor(...)
```

### 3. Request/Response Models (`models/requests.py`, `models/responses.py`)

```python
from pydantic import BaseModel, Field
from typing import Optional, List, Dict

# Request Models
class DrugSearchRequest(BaseModel):
    q: str = Field(..., description="Search term")
    limit: int = Field(20, ge=1, le=100)

class ClassificationRequest(BaseModel):
    drug_name: str
    target_name: str
    force_reclassify: bool = False
    additional_context: Optional[str] = None

# Response Models
class DrugResponse(BaseModel):
    drug: str
    moa: Optional[str]
    phase: Optional[str]

class DrugDetailsResponse(BaseModel):
    drug_info: Dict
    targets: List[str]
    disease_areas: List[str]
    indications: List[str]
```

### 4. Error Handling (`utils/errors.py`)

```python
from fastapi import HTTPException

class APIError(HTTPException):
    def __init__(self, status_code: int, error_code: str, message: str):
        super().__init__(
            status_code=status_code,
            detail={
                "success": False,
                "error": {
                    "code": error_code,
                    "message": message
                }
            }
        )

class DrugNotFoundError(APIError):
    def __init__(self, drug_name: str):
        super().__init__(
            status_code=404,
            error_code="DRUG_NOT_FOUND",
            message=f"Drug '{drug_name}' not found"
        )
```

---

## 📝 Endpoint Mapping

### Current Streamlit Methods → API Endpoints

| Streamlit Method | API Endpoint | HTTP Method |
|------------------|--------------|-------------|
| `search_drugs()` | `/drugs?q={term}` | GET |
| `get_drug_details()` | `/drugs/{drug_name}` | GET |
| `get_drug_network()` | `/drugs/{drug_name}/network` | GET |
| `get_top_drugs_by_targets()` | `/drugs/top/by-targets` | GET |
| `search_drugs_by_moa()` | `/drugs/search/moa?moa={moa}` | GET |
| `get_similar_drugs_by_moa()` | `/drugs/{drug_name}/similar` | GET |
| `search_targets()` | `/targets?q={term}` | GET |
| `get_target_details()` | `/targets/{target_name}` | GET |
| `get_target_network()` | `/targets/{target_name}/network` | GET |
| `find_drugs_by_target()` | `/targets/{target_name}/drugs` | GET |
| `get_top_targets_by_drugs()` | `/targets/top/by-drugs` | GET |
| `get_graph_statistics()` | `/statistics/graph` | GET |
| `get_phase_statistics()` | `/statistics/phase` | GET |
| `get_moa_statistics()` | `/statistics/moa` | GET |
| `get_drug_target_classification()` | `/classification/classify` | POST |
| `classifier.get_existing_classification()` | `/classification/{drug}/{target}` | GET |
| `predict_cascade_effects()` | `/cascade/predict` | POST |
| `get_repurposing_candidates()` | `/repurposing/candidates` | GET |
| `find_common_targets()` | `/repurposing/common-targets` | GET |
| `get_drug_comparison()` | `/analysis/comparison` | GET |

---

## 🚀 Next Steps

1. **Phase 1:** Create folder structure and basic FastAPI app
2. **Phase 2:** Implement database service wrapper
3. **Phase 3:** Implement request/response models
4. **Phase 4:** Implement all routers
5. **Phase 5:** Add authentication and rate limiting
6. **Phase 6:** Add tests
7. **Phase 7:** Documentation and deployment

---

**Status:** Ready for Implementation

