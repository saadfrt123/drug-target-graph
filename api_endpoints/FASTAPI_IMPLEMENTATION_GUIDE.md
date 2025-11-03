# FastAPI Implementation Guide - Complete with Code

**Date:** October 16, 2025  
**Purpose:** Step-by-step implementation guide for simplified FastAPI endpoints with actual code

---

## 📋 Overview

This guide provides **complete, working code** for implementing the 4-5 simplified FastAPI endpoints. The endpoints wrap existing `mechanism_classifier.py` and `cascade_predictor.py` modules.

---

## 🏗️ Project Structure

```
api_endpoints/
├── main.py                          # FastAPI app entry point
├── config.py                        # Environment variables
├── requirements.txt                 # Dependencies
├── .env                             # Environment variables (not in git)
├── __init__.py
└── README.md
```

**Simple structure** - everything in one folder, no complex routing needed for 4-5 endpoints.

---

## 📦 Step 1: Dependencies

Create `api_endpoints/requirements.txt`:

```txt
# FastAPI framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Neo4j driver
neo4j==5.14.0

# Gemini API
google-generativeai==0.3.0

# Environment variables
python-dotenv==1.0.0

# Data validation
pydantic==2.5.0

# Optional: for production
gunicorn==21.2.0
```

---

## ⚙️ Step 2: Configuration

Create `api_endpoints/config.py`:

```python
"""
Configuration management for FastAPI application
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration"""
    
    # Neo4j Configuration
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
    NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")
    
    # Gemini API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    # API Configuration
    API_KEY = os.getenv("API_KEY")  # For API key authentication
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
    
    # CORS Configuration
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

# Global config instance
config = Config()
```

Create `api_endpoints/.env`:

```bash
# Neo4j Configuration
NEO4J_URI=bolt://your-neo4j-instance:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password_here
NEO4J_DATABASE=neo4j

# Gemini API
GEMINI_API_KEY=your_gemini_key_here

# FastAPI Configuration
ENVIRONMENT=production
DEBUG=False

# Security
API_KEY=generate_a_secure_random_key_here
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com
```

---

## 🚀 Step 3: Main FastAPI Application

Create `api_endpoints/main.py`:

```python
"""
FastAPI Application for Drug-Target Graph AI Endpoints
Simplified design: Only AI classification and cascade prediction endpoints
"""

from fastapi import FastAPI, Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import sys
import os
import logging
from datetime import datetime

# Add parent directory to path to import existing modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import existing modules
from mechanism_classifier import DrugTargetMechanismClassifier, MechanismClassification
from cascade_predictor import BiologicalCascadePredictor, CascadePrediction
from config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO if config.DEBUG else logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Drug-Target Graph AI API",
    description="AI-powered drug-target relationship classification and cascade prediction",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key Authentication
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """Verify API key"""
    if config.API_KEY and api_key != config.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )
    return api_key

# Initialize AI modules
classifier = None
cascade_predictor = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global classifier, cascade_predictor
    
    try:
        # Initialize classifier
        classifier = DrugTargetMechanismClassifier(
            gemini_api_key=config.GEMINI_API_KEY,
            neo4j_uri=config.NEO4J_URI,
            neo4j_user=config.NEO4J_USER,
            neo4j_password=config.NEO4J_PASSWORD,
            neo4j_database=config.NEO4J_DATABASE
        )
        logger.info("Classifier initialized successfully")
        
        # Initialize cascade predictor
        cascade_predictor = BiologicalCascadePredictor(
            gemini_api_key=config.GEMINI_API_KEY,
            neo4j_uri=config.NEO4J_URI,
            neo4j_user=config.NEO4J_USER,
            neo4j_password=config.NEO4J_PASSWORD,
            neo4j_database=config.NEO4J_DATABASE
        )
        logger.info("Cascade predictor initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global classifier, cascade_predictor
    
    if classifier:
        classifier.close()
    if cascade_predictor:
        cascade_predictor.close()

# ============================================
# PYDANTIC MODELS
# ============================================

# Request Models
class ClassificationRequest(BaseModel):
    """Request model for single classification"""
    drug_name: str = Field(..., description="Name of the drug")
    target_name: str = Field(..., description="Name of the biological target")
    additional_context: Optional[str] = Field(None, description="Additional context")
    force_reclassify: bool = Field(False, description="Force reclassification even if exists")

class BatchClassificationRequest(BaseModel):
    """Request model for batch classification"""
    drug_name: str = Field(..., description="Name of the drug")
    targets: List[str] = Field(..., description="List of target names to classify")
    additional_context: Optional[str] = Field(None, description="Additional context")
    force_reclassify: bool = Field(False, description="Force reclassification even if exists")

class CascadePredictionRequest(BaseModel):
    """Request model for cascade prediction"""
    drug_name: str = Field(..., description="Name of the drug")
    target_name: str = Field(..., description="Name of the biological target")
    depth: int = Field(2, ge=1, le=3, description="Cascade depth (1-3)")
    additional_context: Optional[str] = Field(None, description="Additional context")

# Response Models
class ClassificationResponse(BaseModel):
    """Response model for classification"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class BatchClassificationResponse(BaseModel):
    """Response model for batch classification"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class CascadeResponse(BaseModel):
    """Response model for cascade prediction"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# ============================================
# ENDPOINTS
# ============================================

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint
    No authentication required
    """
    try:
        # Check if services are initialized
        services_status = {
            "classifier": "ready" if classifier else "not initialized",
            "cascade_predictor": "ready" if cascade_predictor else "not initialized",
        }
        
        return {
            "status": "healthy",
            "services": services_status,
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )

@app.post("/classification/classify", response_model=ClassificationResponse, tags=["AI Classification"])
async def classify_drug_target(
    request: ClassificationRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Classify a single drug-target relationship
    
    **When to call:** When r.classified IS NULL OR r.classified = false in Neo4j
    """
    if not classifier:
        raise HTTPException(status_code=503, detail="Classifier not available")
    
    try:
        logger.info(f"Classifying {request.drug_name} -> {request.target_name}")
        
        # Call existing classifier
        classification = classifier.classify_and_store(
            drug_name=request.drug_name,
            target_name=request.target_name,
            additional_context=request.additional_context or "",
            force_reclassify=request.force_reclassify
        )
        
        if not classification:
            return ClassificationResponse(
                success=False,
                error="Classification failed or drug-target relationship not found"
            )
        
        # Format response
        response_data = {
            "drug_name": request.drug_name,
            "target_name": request.target_name,
            "relationship_type": classification.get('relationship_type'),
            "target_class": classification.get('target_class'),
            "target_subclass": classification.get('target_subclass'),
            "mechanism": classification.get('mechanism'),
            "confidence": classification.get('confidence'),
            "reasoning": classification.get('reasoning'),
            "source": classification.get('source'),
            "timestamp": classification.get('timestamp'),
            "stored_in_db": True
        }
        
        return ClassificationResponse(success=True, data=response_data)
        
    except Exception as e:
        logger.error(f"Classification error: {e}")
        return ClassificationResponse(
            success=False,
            error=str(e)
        )

@app.post("/classification/batch", response_model=BatchClassificationResponse, tags=["AI Classification"])
async def batch_classify_drug_targets(
    request: BatchClassificationRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Batch classify multiple drug-target relationships
    
    **When to call:** When multiple targets need classification
    """
    if not classifier:
        raise HTTPException(status_code=503, detail="Classifier not available")
    
    try:
        logger.info(f"Batch classifying {len(request.targets)} targets for {request.drug_name}")
        
        results = []
        successful = 0
        failed = 0
        
        for target_name in request.targets:
            try:
                classification = classifier.classify_and_store(
                    drug_name=request.drug_name,
                    target_name=target_name,
                    additional_context=request.additional_context or "",
                    force_reclassify=request.force_reclassify
                )
                
                if classification:
                    results.append({
                        "target_name": target_name,
                        "status": "success",
                        "classification": classification
                    })
                    successful += 1
                else:
                    results.append({
                        "target_name": target_name,
                        "status": "failed",
                        "error": "Classification returned None"
                    })
                    failed += 1
                    
            except Exception as e:
                logger.warning(f"Failed to classify {request.drug_name} -> {target_name}: {e}")
                results.append({
                    "target_name": target_name,
                    "status": "failed",
                    "error": str(e)
                })
                failed += 1
        
        # Format response
        response_data = {
            "drug_name": request.drug_name,
            "total": len(request.targets),
            "successful": successful,
            "failed": failed,
            "results": results
        }
        
        return BatchClassificationResponse(success=True, data=response_data)
        
    except Exception as e:
        logger.error(f"Batch classification error: {e}")
        return BatchClassificationResponse(
            success=False,
            error=str(e)
        )

@app.post("/classification/status/{drug_name}/{target_name}", tags=["AI Classification"])
async def check_classification_status(
    drug_name: str,
    target_name: str,
    api_key: str = Depends(verify_api_key)
):
    """
    Check if classification exists for a drug-target pair
    
    **Alternative to querying Neo4j directly**
    """
    if not classifier:
        raise HTTPException(status_code=503, detail="Classifier not available")
    
    try:
        existing = classifier.get_existing_classification(drug_name, target_name)
        
        return {
            "drug_name": drug_name,
            "target_name": target_name,
            "exists": existing is not None,
            "classification": existing if existing else None
        }
        
    except Exception as e:
        logger.error(f"Status check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cascade/predict", response_model=CascadeResponse, tags=["AI Cascade"])
async def predict_cascade_effects(
    request: CascadePredictionRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Predict biological cascade effects for a drug-target pair
    
    **When to call:** When AFFECTS_DOWNSTREAM relationships missing for drug-target
    """
    if not cascade_predictor:
        raise HTTPException(status_code=503, detail="Cascade predictor not available")
    
    try:
        logger.info(f"Predicting cascade for {request.drug_name} -> {request.target_name} (depth={request.depth})")
        
        # Call existing cascade predictor
        cascade = cascade_predictor.predict_and_store(
            drug_name=request.drug_name,
            target_name=request.target_name,
            depth=request.depth,
            additional_context=request.additional_context or ""
        )
        
        if not cascade:
            return CascadeResponse(
                success=False,
                error="Cascade prediction failed or drug-target relationship not found"
            )
        
        # Format response
        response_data = {
            "drug_name": request.drug_name,
            "target_name": request.target_name,
            "direct_effects": [
                {
                    "entity_name": e.get('entity_name'),
                    "entity_type": e.get('entity_type'),
                    "effect_type": e.get('effect_type'),
                    "confidence": e.get('confidence'),
                    "reasoning": e.get('reasoning'),
                    "depth": e.get('depth')
                }
                for e in cascade.get('direct_effects', [])
            ],
            "secondary_effects": [
                {
                    "entity_name": e.get('entity_name'),
                    "entity_type": e.get('entity_type'),
                    "effect_type": e.get('effect_type'),
                    "confidence": e.get('confidence'),
                    "reasoning": e.get('reasoning'),
                    "depth": e.get('depth')
                }
                for e in cascade.get('secondary_effects', [])
            ],
            "tertiary_effects": [
                {
                    "entity_name": e.get('entity_name'),
                    "entity_type": e.get('entity_type'),
                    "effect_type": e.get('effect_type'),
                    "confidence": e.get('confidence'),
                    "reasoning": e.get('reasoning'),
                    "depth": e.get('depth')
                }
                for e in cascade.get('tertiary_effects', [])
            ],
            "stored_in_db": True,
            "timestamp": cascade.get('prediction_timestamp')
        }
        
        return CascadeResponse(success=True, data=response_data)
        
    except Exception as e:
        logger.error(f"Cascade prediction error: {e}")
        return CascadeResponse(
            success=False,
            error=str(e)
        )

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=config.DEBUG)
```

---

## 🧪 Step 4: Testing

Create `api_endpoints/test_endpoints.py`:

```python
"""
Test script for FastAPI endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"
API_KEY = "your_api_key_here"  # Change this

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    print("Health Check:", response.json())

def test_classify():
    """Test single classification"""
    data = {
        "drug_name": "aspirin",
        "target_name": "PTGS2",
        "additional_context": "COX-2 enzyme"
    }
    response = requests.post(
        f"{BASE_URL}/classification/classify",
        headers=headers,
        json=data
    )
    print("Classification:", json.dumps(response.json(), indent=2))

def test_batch_classify():
    """Test batch classification"""
    data = {
        "drug_name": "aspirin",
        "targets": ["PTGS2", "NFKBIA", "TGFBR1"],
        "additional_context": "Multiple targets"
    }
    response = requests.post(
        f"{BASE_URL}/classification/batch",
        headers=headers,
        json=data
    )
    print("Batch Classification:", json.dumps(response.json(), indent=2))

def test_cascade():
    """Test cascade prediction"""
    data = {
        "drug_name": "aspirin",
        "target_name": "PTGS2",
        "depth": 2,
        "additional_context": "COX-2 inhibition"
    }
    response = requests.post(
        f"{BASE_URL}/cascade/predict",
        headers=headers,
        json=data
    )
    print("Cascade Prediction:", json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    print("Testing FastAPI endpoints...")
    test_health()
    # test_classify()
    # test_batch_classify()
    # test_cascade()
```

---

## 🚀 Step 5: Running the API

### Development Mode:

```bash
cd api_endpoints
python main.py
```

Or with uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode:

```bash
# Using Gunicorn
gunicorn main:app -w 4 --worker-class uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

---

## 📝 Step 6: API Documentation

Once running, documentation is auto-generated at:
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

---

## 🔐 Step 7: Authentication

All endpoints except `/health` require API key authentication.

**Send requests with header:**
```bash
curl -X POST http://localhost:8000/classification/classify \
  -H "X-API-Key: your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{"drug_name": "aspirin", "target_name": "PTGS2"}'
```

---

## ✅ Summary

**Complete Implementation:**
- ✅ `main.py` - FastAPI app with all 5 endpoints
- ✅ `config.py` - Configuration management
- ✅ `requirements.txt` - Dependencies
- ✅ `.env` - Environment variables
- ✅ Reuses existing `mechanism_classifier.py` and `cascade_predictor.py`
- ✅ API key authentication
- ✅ Auto-generated documentation
- ✅ Error handling
- ✅ Logging

**Endpoints:**
1. `GET /health` - Health check
2. `POST /classification/classify` - Single classification
3. `POST /classification/batch` - Batch classification
4. `POST /classification/status/{drug}/{target}` - Status check
5. `POST /cascade/predict` - Cascade prediction

**Next:** Follow `EC2_DEPLOYMENT_GUIDE.md` for deployment to AWS EC2.

