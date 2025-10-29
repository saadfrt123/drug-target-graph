# FastAPI Endpoints - Module Structure

## Overview

This module provides RESTful API endpoints for the Drug-Target Graph Database Explorer application.

## Module Organization

### Core Files
- `main.py` - FastAPI application setup and router registration
- `config.py` - API configuration (API keys, rate limits, etc.)
- `dependencies.py` - Shared dependencies (DB connection, auth)

### Routers (`routers/`)
Each router handles a specific domain:

1. **health.py** - Health check endpoints
2. **drugs.py** - Drug search, details, network endpoints
3. **targets.py** - Target search, details, network endpoints
4. **network.py** - Network visualization endpoints
5. **statistics.py** - Statistics and analytics endpoints
6. **classification.py** - AI mechanism classification endpoints
7. **cascade.py** - AI cascade prediction endpoints
8. **repurposing.py** - Drug repurposing endpoints
9. **analysis.py** - Analysis and comparison endpoints

### Services (`services/`)
Business logic layer that wraps existing Streamlit app methods:

1. **database.py** - Database connection and initialization
2. **drug_service.py** - Drug-related operations
3. **target_service.py** - Target-related operations
4. **classification_service.py** - Classification operations
5. **cascade_service.py** - Cascade prediction operations

### Models (`models/`)
Pydantic models for request/response validation:

1. **requests.py** - Request models
2. **responses.py** - Response models
3. **common.py** - Common/shared models

### Utils (`utils/`)
Utility functions:

1. **errors.py** - Custom error classes
2. **auth.py** - Authentication utilities
3. **rate_limit.py** - Rate limiting utilities

## Integration with Existing Code

The API wraps existing functionality from:
- `streamlit_app.py` - `DrugTargetGraphApp` class methods
- `mechanism_classifier.py` - Classification logic
- `cascade_predictor.py` - Cascade prediction logic

No changes needed to existing code - API is a wrapper layer.

## Authentication

Uses API key authentication via header:
```
X-API-Key: your-api-key
```

## Rate Limiting

Implemented using `slowapi`:
- Standard endpoints: 100/min
- AI endpoints: 10/min
- Statistics: 50/min

## Error Handling

Standardized error responses:
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description"
  }
}
```

## Testing

Tests located in `tests/` directory:
- Unit tests for each router
- Integration tests for services
- Mock database responses

## Deployment

Recommended deployment:
- **Development:** `uvicorn api_endpoints.main:app --reload`
- **Production:** Use `gunicorn` with `uvicorn` workers
- **Docker:** Containerized deployment

## Environment Variables

Required:
- `NEO4J_URI` - Neo4j database URI
- `NEO4J_USER` - Neo4j username
- `NEO4J_PASSWORD` - Neo4j password
- `NEO4J_DATABASE` - Neo4j database name
- `GEMINI_API_KEY` - Google Gemini API key
- `API_KEY` - API authentication key

Optional:
- `API_RATE_LIMIT` - Rate limit per minute (default: 100)
- `LOG_LEVEL` - Logging level (default: INFO)

