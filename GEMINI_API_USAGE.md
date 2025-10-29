# Comprehensive Gemini API Usage Documentation

**Project:** Drug-Target Graph Database Explorer  
**Date:** October 15, 2025  
**Purpose:** Complete documentation of all Gemini API calls, prompts, inputs, and outputs for setting up endpoints

---

## 📋 Summary

**Total Modules Using Gemini API:** 2  
**Total API Call Locations:** 2  
1. `mechanism_classifier.py` - Drug-Target Mechanism Classification
2. `cascade_predictor.py` - Biological Cascade Effect Prediction

---

## 🔍 Module 1: mechanism_classifier.py

### **Purpose:**
Classify drug-target relationships as Primary/On-Target vs Secondary/Off-Target, identify target class, subclass, and mechanism.

### **API Call Location:**
- **File:** `mechanism_classifier.py`
- **Method:** `classify_drug_target_relationship()` - Line 176-273
- **Called from:** `streamlit_app.py` via `DrugTargetMechanismClassifier` class

### **Gemini API Configuration:**
```python
# Line 42: Initialize
genai.configure(api_key=gemini_api_key)

# Line 114-115: Create model
self.gemini_model = genai.GenerativeModel(model_name)

# Line 217: Call API
response = self.gemini_model.generate_content(prompt)
```

### **Models Used (in order of preference):**
1. `models/gemini-2.5-flash-lite` (fastest)
2. `models/gemini-2.5-flash`
3. `models/gemini-2.0-flash-exp`
4. `models/gemini-1.5-flash`
5. `models/gemini-1.5-pro` (fallback)

**Configuration:** Temperature = 0.5

---

### **INPUT PARAMETERS:**

#### **Function Call:**
```python
classification = classifier.classify_drug_target_relationship(
    drug_name="aspirin",
    target_name="PTGS2",
    additional_context="COX-2 enzyme"  # Optional
)
```

#### **Required Inputs:**
- `drug_name` (str): Name of drug (e.g., "aspirin", "ibuprofen")
- `target_name` (str): Name of biological target (e.g., "PTGS2", "COX-2")
- `additional_context` (str, optional): Additional context about the drug-target interaction

---

### **PROMPT SENT TO GEMINI:**

```
You are an expert pharmacologist. Classify the relationship between the drug "{drug_name}" and its target "{target_name}".

Classification Levels:
1. Relationship Type: Primary/On-Target OR Secondary/Off-Target
2. Target Class: Protein, Nucleic Acid, Lipid, OR Carbohydrate  
3. Target Subclass (if Protein): Enzyme, Receptor, Ion Channel, Transporter, Transcription Factor, OR Other
4. Mechanism: Specific action (e.g., Inhibitor, Agonist, Blocker)

RESPOND ONLY WITH VALID JSON:

{
    "relationship_type": "Primary/On-Target",
    "target_class": "Protein",
    "target_subclass": "Enzyme",
    "mechanism": "Irreversible Inhibitor",
    "confidence": 0.95,
    "reasoning": "Brief explanation here"
}

Drug: {drug_name}
Target: {target_name}
Context: {additional_context}

JSON Response:
```

---

### **EXPECTED OUTPUT:**

#### **JSON Structure:**
```json
{
    "relationship_type": "Primary/On-Target",
    "target_class": "Protein",
    "target_subclass": "Enzyme",
    "mechanism": "Irreversible Inhibitor",
    "confidence": 0.95,
    "reasoning": "Aspirin irreversibly acetylates COX-2, making it the primary therapeutic target"
}
```

#### **Field Definitions:**
- `relationship_type` (str): "Primary/On-Target" or "Secondary/Off-Target"
- `target_class` (str): "Protein", "Nucleic Acid", "Lipid", or "Carbohydrate"
- `target_subclass` (str): "Enzyme", "Receptor", "Ion Channel", "Transporter", "Transcription Factor", or "Other"
- `mechanism` (str): Specific mechanism like "Irreversible Inhibitor", "Competitive Agonist", "Allosteric Blocker", etc.
- `confidence` (float): 0.0 to 1.0
- `reasoning` (str): AI's explanation for the classification

#### **Example Actual Output:**
```json
{
    "relationship_type": "Primary/On-Target",
    "target_class": "Protein",
    "target_subclass": "Enzyme",
    "mechanism": "Irreversible Inhibitor",
    "confidence": 0.98,
    "reasoning": "Aspirin is a well-known irreversible COX-2 inhibitor. COX-2 is the primary cyclooxygenase enzyme responsible for prostaglandin synthesis, and aspirin's mechanism of action involves acetylation of the active site serine, making it the primary therapeutic target for pain relief and anti-inflammatory effects."
}
```

---

### **PROCESSING & STORAGE:**

1. **Parse JSON response** - Extract classification data
2. **Validate required fields** - Check all fields present
3. **Store in Neo4j** - Update TARGETS relationship properties:
   - `relationship_type`
   - `target_class`
   - `target_subclass`
   - `mechanism`
   - `confidence`
   - `reasoning`
   - `classification_source` = "Gemini_API"
   - `classification_timestamp` = ISO timestamp
   - `classified` = true

---

### **NEO4J QUERY TO RETRIEVE:**
```cypher
MATCH (d:Drug {name: "aspirin"})-[r:TARGETS]->(t:Target {name: "PTGS2"})
RETURN r.relationship_type, r.target_class, r.mechanism, r.confidence, r.reasoning
```

---

## 🔍 Module 2: cascade_predictor.py

### **Purpose:**
Predict downstream biological cascade effects when a drug acts on a target (pathways, genes, metabolites, cellular processes affected).

### **API Call Location:**
- **File:** `cascade_predictor.py`
- **Method:** `predict_cascade_effects()` - Line 157-228
- **Called from:** `streamlit_app.py` via `BiologicalCascadePredictor` class

### **Gemini API Configuration:**
```python
# Line 87: Initialize
genai.configure(api_key=api_key)

# Line 100: Create model
self.gemini_model = genai.GenerativeModel(model_name)

# Line 193: Call API with retry logic
response = self.gemini_model.generate_content(
    prompt,
    generation_config={
        'temperature': 0.3,
        'top_p': 0.8,
        'top_k': 40,
        'max_output_tokens': 2048
    }
)
```

### **Models Used (in order of preference):**
1. `models/gemini-2.0-flash-exp`
2. `models/gemini-1.5-flash-latest`
3. `models/gemini-1.5-flash`
4. `models/gemini-1.5-pro`
5. `models/gemini-pro` (fallback)

**Configuration:** Temperature = 0.3, Max tokens = 2048

---

### **INPUT PARAMETERS:**

#### **Function Call:**
```python
cascade = predictor.predict_cascade_effects(
    drug_name="aspirin",
    target_name="PTGS2",
    depth=2,  # 1, 2, or 3 (default: 2)
    additional_context="COX-2 enzyme inhibition"  # Optional
)
```

#### **Required Inputs:**
- `drug_name` (str): Name of drug (e.g., "aspirin", "ibuprofen")
- `target_name` (str): Name of biological target (e.g., "PTGS2")
- `depth` (int): Number of hops to predict (1=direct only, 2=direct+secondary, 3=all)
- `additional_context` (str, optional): Additional context about the interaction

---

### **PROMPT SENT TO GEMINI:**

```
You are an expert pharmacologist and systems biologist. 

Analyze the biological cascade effects when drug "{drug_name}" acts on target "{target_name}".

{depth_instructions}  // Changes based on depth parameter

Context: {additional_context}

Predict downstream effects on:
- Biological pathways
- Gene expression
- Metabolites
- Cellular processes
- Other proteins

For each effect, specify:
1. Entity name (be specific)
2. Entity type (Pathway, Gene, Metabolite, CellularProcess, or Protein)
3. Effect type (inhibits, activates, upregulates, downregulates, or modulates)
4. Confidence score (0.0 to 1.0)
5. Brief reasoning

RESPOND ONLY WITH VALID JSON in this EXACT format:

{
  "direct_effects": [
    {
      "entity_name": "Prostaglandin synthesis pathway",
      "entity_type": "Pathway",
      "effect_type": "inhibits",
      "confidence": 0.95,
      "reasoning": "COX-2 is the rate-limiting enzyme in prostaglandin production",
      "source_entity": "{target_name}"
    }
  ],
  "secondary_effects": [
    {
      "entity_name": "Inflammatory response",
      "entity_type": "CellularProcess",
      "effect_type": "downregulates",
      "confidence": 0.88,
      "reasoning": "Reduced prostaglandins lead to decreased inflammation",
      "source_entity": "Prostaglandin synthesis pathway"
    }
  ],
  "tertiary_effects": []
}

Focus on high-confidence, well-established biological relationships.
Provide 3-5 direct effects and 2-4 secondary effects.
Be specific with pathway and gene names.

JSON Response:
```

**Depth Instructions by depth parameter:**
- depth=1: "Focus only on DIRECT effects (1-hop from the target)."
- depth=2: "Include both DIRECT effects (1-hop) and SECONDARY effects (2-hop)."
- depth=3: "Include DIRECT effects (1-hop), SECONDARY effects (2-hop), and TERTIARY effects (3-hop)."

---

### **EXPECTED OUTPUT:**

#### **JSON Structure:**
```json
{
    "direct_effects": [
        {
            "entity_name": "Prostaglandin E2",
            "entity_type": "Metabolite",
            "effect_type": "downregulates",
            "confidence": 0.98,
            "reasoning": "COX-2 converts arachidonic acid to PGE2; inhibition reduces PGE2 levels",
            "source_entity": "PTGS2"
        },
        {
            "entity_name": "Prostaglandin synthesis pathway",
            "entity_type": "Pathway",
            "effect_type": "inhibits",
            "confidence": 0.95,
            "reasoning": "COX-2 is the rate-limiting enzyme in prostaglandin biosynthesis",
            "source_entity": "PTGS2"
        }
    ],
    "secondary_effects": [
        {
            "entity_name": "Inflammatory response",
            "entity_type": "CellularProcess",
            "effect_type": "downregulates",
            "confidence": 0.88,
            "reasoning": "Reduced prostaglandin levels lead to decreased inflammatory signaling",
            "source_entity": "Prostaglandin E2"
        },
        {
            "entity_name": "Pain perception",
            "entity_type": "CellularProcess",
            "effect_type": "downregulates",
            "confidence": 0.85,
            "reasoning": "PGE2 sensitizes nociceptors; reduced PGE2 decreases pain sensitivity",
            "source_entity": "Prostaglandin E2"
        }
    ],
    "tertiary_effects": []
}
```

#### **Field Definitions:**
- `entity_name` (str): Name of the affected biological entity
- `entity_type` (str): "Pathway", "Gene", "Metabolite", "CellularProcess", or "Protein"
- `effect_type` (str): "inhibits", "activates", "upregulates", "downregulates", or "modulates"
- `confidence` (float): 0.0 to 1.0
- `reasoning` (str): AI's explanation for the effect
- `source_entity` (str): What entity causes this effect

#### **Example Actual Output:**
```json
{
    "direct_effects": [
        {
            "entity_name": "Prostaglandin E2 synthesis",
            "entity_type": "Metabolite",
            "effect_type": "downregulates",
            "confidence": 0.98,
            "reasoning": "Aspirin inhibits COX-2, which converts arachidonic acid to PGE2. By blocking this enzyme, PGE2 production is significantly reduced.",
            "source_entity": "PTGS2"
        },
        {
            "entity_name": "Thromboxane A2 synthesis",
            "entity_type": "Metabolite",
            "effect_type": "downregulates",
            "confidence": 0.92,
            "reasoning": "COX-2 also plays a role in thromboxane production in inflammatory conditions. Aspirin's inhibition reduces thromboxane levels.",
            "source_entity": "PTGS2"
        }
    ],
    "secondary_effects": [
        {
            "entity_name": "Inflammatory cytokine production",
            "entity_type": "CellularProcess",
            "effect_type": "downregulates",
            "confidence": 0.87,
            "reasoning": "Reduced prostaglandin signaling leads to decreased production of pro-inflammatory cytokines such as IL-1 and TNF-alpha.",
            "source_entity": "Prostaglandin E2 synthesis"
        },
        {
            "entity_name": "Fever",
            "entity_type": "CellularProcess",
            "effect_type": "downregulates",
            "confidence": 0.85,
            "reasoning": "PGE2 acts on the hypothalamus to induce fever. Reduced PGE2 levels result in antipyretic effects.",
            "source_entity": "Prostaglandin E2 synthesis"
        }
    ],
    "tertiary_effects": []
}
```

---

### **PROCESSING & STORAGE:**

1. **Parse JSON response** - Extract cascade effects
2. **Convert to CascadeEffect objects** - Create Python dataclass objects
3. **Calculate average confidence** - Across all effects
4. **Store in Neo4j** - Create nodes and relationships:
   - Create nodes: `Pathway`, `Gene`, `Metabolite`, `CellularProcess`, `Protein`
   - Create relationships: `AFFECTS_DOWNSTREAM` with properties:
     - `effect_type`
     - `confidence`
     - `reasoning`
     - `depth` (1, 2, or 3)
     - `source_entity`
     - `predicted_by` = "Gemini_API"
     - `prediction_date` = ISO timestamp

---

### **NEO4J QUERIES TO RETRIEVE:**

#### **Get all cascade effects for a target:**
```cypher
MATCH (t:Target {name: "PTGS2"})-[r:AFFECTS_DOWNSTREAM]->(e)
RETURN e.name AS entity_name, 
       labels(e)[0] AS entity_type,
       r.effect_type, 
       r.confidence, 
       r.depth,
       r.reasoning
ORDER BY r.depth, r.confidence DESC
```

#### **Get direct effects only (depth 1):**
```cypher
MATCH (t:Target {name: "PTGS2"})-[r:AFFECTS_DOWNSTREAM]->(e)
WHERE r.depth = 1
RETURN e.name, r.effect_type, r.confidence
```

---

## 🚀 SETTING UP ENDPOINTS

### **Endpoint Architecture Recommendation:**

```
Frontend (React/Vue/etc)
    ↓ HTTP/HTTPS
Backend API (FastAPI/Flask/Django)
    ↓
gemini_endpoint.py
    ↓
Google Gemini API
    ↓
Response back to Frontend
```

---

### **Sample Endpoint Implementation (FastAPI):**

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
import os

app = FastAPI()

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
gemini_model = genai.GenerativeModel('models/gemini-2.5-flash')

# Request/Response models
class ClassificationRequest(BaseModel):
    drug_name: str
    target_name: str
    additional_context: str = ""

class ClassificationResponse(BaseModel):
    relationship_type: str
    target_class: str
    target_subclass: str
    mechanism: str
    confidence: float
    reasoning: str

class CascadeRequest(BaseModel):
    drug_name: str
    target_name: str
    depth: int = 2
    additional_context: str = ""

class CascadeResponse(BaseModel):
    direct_effects: list
    secondary_effects: list
    tertiary_effects: list
    total_confidence: float

# Endpoint 1: Drug-Target Classification
@app.post("/api/classify", response_model=ClassificationResponse)
async def classify_drug_target(request: ClassificationRequest):
    """Classify drug-target relationship"""
    
    # Use the same prompt from mechanism_classifier.py
    prompt = f"""
    You are an expert pharmacologist...
    [INSERT FULL PROMPT FROM mechanism_classifier.py LINE 144-165]
    Drug: {request.drug_name}
    Target: {request.target_name}
    Context: {request.additional_context}
    """
    
    try:
        response = gemini_model.generate_content(prompt)
        # Parse JSON from response
        # Return ClassificationResponse
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint 2: Cascade Prediction
@app.post("/api/cascade", response_model=CascadeResponse)
async def predict_cascade(request: CascadeRequest):
    """Predict biological cascade effects"""
    
    # Use the same prompt from cascade_predictor.py
    prompt = f"""
    You are an expert pharmacologist and systems biologist...
    [INSERT FULL PROMPT FROM cascade_predictor.py LINE 237-296]
    """
    
    try:
        response = gemini_model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.3,
                'max_output_tokens': 2048
            }
        )
        # Parse JSON from response
        # Return CascadeResponse
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 📊 API USAGE SUMMARY

### **Rate Limits:**
- **Gemini Free Tier:** 60 requests/minute, 1,500 requests/day
- **Recommendation:** Implement rate limiting and caching in your endpoint

### **Average Response Times:**
- Classification: 2-5 seconds
- Cascade Prediction: 5-15 seconds

### **Cost:**
- **Free tier:** $0/month (up to 1,500 requests/day)
- **Paid tier:** Variable based on model and usage

### **Error Handling:**
Both modules implement retry logic (max 3 attempts) with exponential backoff for transient failures.

---

## 🔑 ENVIRONMENT VARIABLES NEEDED:

```bash
# Required
GEMINI_API_KEY=your-google-gemini-api-key-here
```

---

## 📝 SUMMARY

**Total Gemini API Calls:** 2  
1. **Mechanism Classification** - Classifies drug-target relationships
2. **Cascade Prediction** - Predicts downstream biological effects

**Common Pattern:**
1. Build detailed prompt with specific JSON format requirement
2. Call Gemini API with prompt
3. Parse JSON response
4. Validate required fields
5. Store in Neo4j database
6. Return structured data

**Key Points:**
- Both use JSON-formatted responses
- Both implement retry logic
- Both store results in Neo4j
- Both include confidence scoring
- Temperature settings: 0.5 (classification), 0.3 (cascade)

---

**Last Updated:** October 15, 2025  
**Status:** Production-ready comprehensive documentation
