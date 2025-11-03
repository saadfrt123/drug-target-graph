# Backend Code Review & FastAPI Integration Plan

**Date:** October 16, 2025  
**Backend:** NestJS API in `trial-match-api`  
**Integration:** FastAPI AI endpoints for drug-target classification

---

## 🔍 Backend Analysis

### **What the Backend Currently Has:**

#### **1. Drug Neo4j Module** (`drug-neo4j`)

**Endpoints (20+):**
- ✅ Create drug nodes
- ✅ Create drug relationships
- ✅ Search drugs
- ✅ Get drug network
- ✅ Get drug statistics
- ✅ Dashboard analytics
- ✅ Top drugs/targets
- ✅ **Drug basic information** (with classification fields)
- ✅ **Target search** (with classification fields)

**Key Observations:**
- ✅ Already queries `relationship_type` field on `TARGETS` relationships
- ✅ Already queries `classified` boolean field
- ✅ Returns `mechanism`, `target_class`, `target_subclass`, `confidence`
- ✅ Has classification statistics (primary/secondary/unknown/unclassified counts)
- ❌ **NO AI endpoints** - Classification data comes from Neo4j only
- ❌ **NO Gemini integration** - No AI calls in the backend

#### **2. Classification Fields in Backend:**

```typescript
// From drug-neo4j.service.ts lines 410-426
interface BiologicTarget {
  target: string;
  relationship_type?: string;      // Primary/On-Target, Secondary/Off-Target
  mechanism?: string;              // Specific mechanism
  target_class?: string;           // Protein, Nucleic Acid, etc.
  target_subclass?: string;        // Enzyme, Receptor, etc.
  confidence?: number;             // 0.0 to 1.0
}

// Classification status queries:
- r.classified = true   → Classified
- r.classified = false  → Unclassified
- r.classified IS NULL  → Under analysis
```

---

## 🎯 Integration Gap Analysis

### **What's Missing:**

**The backend:**
1. ✅ Queries Neo4j for existing classification data
2. ❌ Has **NO way to generate new classifications** when data is missing
3. ❌ Has **NO AI service** to call when `r.classified IS NULL OR false`
4. ❌ **Cannot populate** `relationship_type`, `mechanism`, `target_class`, etc.

**Our FastAPI endpoints:**
1. ✅ Classify drug-target relationships via Gemini AI
2. ✅ Batch classify multiple targets
3. ✅ Predict cascade effects
4. ✅ Store results in Neo4j automatically

---

## 📋 Integration Plan

### **Phase 1: Understanding Current Flow**

**Current Backend Flow:**
```
User → Backend API → Neo4j Query
                         ↓
                    Check r.classified
                         ↓
              ┌──────────┴──────────┐
              ↓                     ↓
        classified=true        classified=false
              ↓                     ↓
       Return existing       Return "Unclassified"
       classification        (limited data)
```

**Problem:** No way to populate `unclassified` data!

---

### **Phase 2: Integrated Flow with FastAPI**

**New Integrated Flow:**
```
User → Backend API → Neo4j Query
                         ↓
                    Check r.classified
                         ↓
              ┌──────────┴──────────┐
              ↓                     ↓
        classified=true      classified=false OR NULL
              ↓                     ↓
       Return existing       Call FastAPI Endpoint
       classification             ↓
                          Gemini AI Classification
                                 ↓
                          Store in Neo4j
                                 ↓
                          Return classification
```

---

### **Phase 3: Backend Code Changes Needed**

#### **3.1 Add FastAPI Client Service**

**Create:** `src/drug-neo4j/drug-neo4j-ai.service.ts`

```typescript
import { Injectable, HttpException, HttpStatus } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import axios from 'axios';

@Injectable()
export class DrugNeo4jAiService {
  private readonly fastApiBaseUrl: string;
  private readonly fastApiKey: string;

  constructor(private configService: ConfigService) {
    this.fastApiBaseUrl = this.configService.get('FASTAPI_BASE_URL');
    this.fastApiKey = this.configService.get('FASTAPI_API_KEY');
  }

  /**
   * Check if classification exists before calling AI
   */
  async needsClassification(drugName: string, targetName: string): Promise<boolean> {
    // Query Neo4j to check if classified
    // Implementation in main service
  }

  /**
   * Call FastAPI to classify drug-target relationship
   */
  async classifyDrugTarget(
    drugName: string,
    targetName: string,
    additionalContext?: string
  ): Promise<any> {
    try {
      const response = await axios.post(
        `${this.fastApiBaseUrl}/classification/classify`,
        {
          drug_name: drugName,
          target_name: targetName,
          additional_context: additionalContext
        },
        {
          headers: {
            'X-API-Key': this.fastApiKey,
            'Content-Type': 'application/json'
          },
          timeout: 30000  // 30 seconds
        }
      );

      return response.data;
    } catch (error) {
      throw new HttpException(
        `Classification failed: ${error.message}`,
        HttpStatus.SERVICE_UNAVAILABLE
      );
    }
  }

  /**
   * Call FastAPI for batch classification
   */
  async batchClassifyDrugTargets(
    drugName: string,
    targets: string[],
    additionalContext?: string
  ): Promise<any> {
    try {
      const response = await axios.post(
        `${this.fastApiBaseUrl}/classification/batch`,
        {
          drug_name: drugName,
          targets: targets,
          additional_context: additionalContext
        },
        {
          headers: {
            'X-API-Key': this.fastApiKey,
            'Content-Type': 'application/json'
          },
          timeout: 120000  // 2 minutes for batch
        }
      );

      return response.data;
    } catch (error) {
      throw new HttpException(
        `Batch classification failed: ${error.message}`,
        HttpStatus.SERVICE_UNAVAILABLE
      );
    }
  }

  /**
   * Call FastAPI to predict cascade effects
   */
  async predictCascadeEffects(
    drugName: string,
    targetName: string,
    depth: number = 2,
    additionalContext?: string
  ): Promise<any> {
    try {
      const response = await axios.post(
        `${this.fastApiBaseUrl}/cascade/predict`,
        {
          drug_name: drugName,
          target_name: targetName,
          depth: depth,
          additional_context: additionalContext
        },
        {
          headers: {
            'X-API-Key': this.fastApiKey,
            'Content-Type': 'application/json'
          },
          timeout: 60000  // 60 seconds
        }
      );

      return response.data;
    } catch (error) {
      throw new HttpException(
        `Cascade prediction failed: ${error.message}`,
        HttpStatus.SERVICE_UNAVAILABLE
      );
    }
  }
}
```

---

#### **3.2 Update Existing Service to Auto-Classify**

**Modify:** `src/drug-neo4j/drug-neo4j.service.ts`

**Add to `getDrugBasicInformation` method (line 345):**

```typescript
async getDrugBasicInformation(drugName: string): Promise<{
  basic_information: DrugDetailsDto;
  drug_target_network: {...};
  similar_drugs: [...];
  biologic_targets: [...];
}> {
  try {
    // ... existing code to get basic info ...
    
    // NEW: Check if targets need classification
    const unclassifiedTargets = this.biologicTargets
      .filter(t => !t.relationship_type && !t.mechanism);

    if (unclassifiedTargets.length > 0) {
      // Call FastAPI to auto-classify
      try {
        const aiResult = await this.drugNeo4jAiService.batchClassifyDrugTargets(
          drugName,
          unclassifiedTargets.map(t => t.target)
        );

        // Refresh biologic_targets after classification
        const refreshedQuery = `
          MATCH (d:Drug {name: $drug_name})-[r:TARGETS]->(t:Target)
          RETURN 
            t.name as target,
            r.relationship_type as relationship_type,
            r.mechanism as mechanism,
            r.target_class as target_class,
            r.target_subclass as target_subclass,
            r.confidence as confidence
          ORDER BY r.confidence DESC, t.name
        `;
        const refreshed = await this.neo4jService.runQuery(refreshedQuery, { drug_name: drugName });
        biologic_targets = refreshed.map(item => ({
          ...item,
          confidence: this.convertNeo4jInt(item.confidence)
        }));
      } catch (aiError) {
        console.error('Auto-classification failed:', aiError);
        // Continue without AI classification
      }
    }

    return { basic_information: basic, drug_target_network, similar_drugs, biologic_targets };
  } catch (error) {
    // ... existing error handling ...
  }
}
```

---

#### **3.3 Add New Endpoints for Manual Classification**

**Add to:** `src/drug-neo4j/drug-neo4j.controller.ts`

```typescript
@Controller('drugs-neo4j')
@UseGuards(AuthGuard('jwt'))
export class DrugNeo4jController {
  constructor(
    private readonly drugNeo4jService: DrugNeo4jService,
    private readonly drugNeo4jAiService: DrugNeo4jAiService  // NEW
  ) {}

  // NEW ENDPOINT 1: Classify single drug-target pair
  @Post('classify')
  async classifyDrugTarget(
    @Body() body: { drugName: string; targetName: string; additionalContext?: string }
  ) {
    return await this.drugNeo4jAiService.classifyDrugTarget(
      body.drugName,
      body.targetName,
      body.additionalContext
    );
  }

  // NEW ENDPOINT 2: Batch classify targets for a drug
  @Post('batch-classify')
  async batchClassifyDrugTargets(
    @Body() body: { drugName: string; targets: string[]; additionalContext?: string }
  ) {
    return await this.drugNeo4jAiService.batchClassifyDrugTargets(
      body.drugName,
      body.targets,
      body.additionalContext
    );
  }

  // NEW ENDPOINT 3: Predict cascade effects
  @Post('cascade')
  async predictCascade(
    @Body() body: { drugName: string; targetName: string; depth?: number; additionalContext?: string }
  ) {
    return await this.drugNeo4jAiService.predictCascadeEffects(
      body.drugName,
      body.targetName,
      body.depth || 2,
      body.additionalContext
    );
  }

  // ... existing endpoints ...
}
```

---

### **Phase 4: Environment Configuration**

**Add to `.env`:**
```env
# FastAPI Integration
FASTAPI_BASE_URL=http://localhost:8000
FASTAPI_API_KEY=your_secure_api_key_here
```

**Update:** `src/config/neo4j.config.ts` (create if doesn't exist)

```typescript
export default () => ({
  neo4j: {
    uri: process.env.NEO4J_URI,
    username: process.env.NEO4J_USERNAME,
    password: process.env.NEO4J_PASSWORD,
    database: process.env.NEO4J_DATABASE || 'neo4j',
  },
  fastapi: {
    baseUrl: process.env.FASTAPI_BASE_URL,
    apiKey: process.env.FASTAPI_API_KEY,
  },
});
```

---

### **Phase 5: Installation Requirements**

**Install axios:**
```bash
npm install axios
npm install --save-dev @types/axios
```

---

## 📊 Integration Architecture Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    Frontend Application                       │
└───────────────────────┬──────────────────────────────────────┘
                        │
                        │ HTTP Requests
                        ↓
┌──────────────────────────────────────────────────────────────┐
│               NestJS Backend (trial-match-api)                │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │    drug-neo4j.controller.ts                             │  │
│  │  - GET /drugs-neo4j/search/drugs                        │  │
│  │  - POST /drugs-neo4j/classify          ← NEW            │  │
│  │  - POST /drugs-neo4j/batch-classify    ← NEW            │  │
│  │  - POST /drugs-neo4j/cascade           ← NEW            │  │
│  └────────────────────┬────────────────────────────────────┘  │
│                       │                                        │
│  ┌────────────────────┴────────────────────────────────────┐  │
│  │    drug-neo4j.service.ts                                │  │
│  │  - getDrugBasicInformation()                            │  │
│  │  - Auto-classify missing targets        ← UPDATED       │  │
│  └────────────────────┬────────────────────────────────────┘  │
│                       │                                        │
│  ┌────────────────────┴────────────────────────────────────┐  │
│  │    drug-neo4j-ai.service.ts            ← NEW            │  │
│  │  - classifyDrugTarget()                                 │  │
│  │  - batchClassifyDrugTargets()                           │  │
│  │  - predictCascadeEffects()                              │  │
│  └────────────────────┬────────────────────────────────────┘  │
└───────────────────────┼────────────────────────────────────────┘
                        │
                        │ HTTP + API Key Auth
                        ↓
┌──────────────────────────────────────────────────────────────┐
│              FastAPI Service (AI Endpoints)                   │
│                                                                │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │    main.py                                              │  │
│  │  - POST /classification/classify                        │  │
│  │  - POST /classification/batch                           │  │
│  │  - POST /cascade/predict                                │  │
│  └────────────────────┬────────────────────────────────────┘  │
│                       │                                        │
│  ┌────────────────────┴────────────────────────────────────┐  │
│  │    mechanism_classifier.py                              │  │
│  │    cascade_predictor.py                                 │  │
│  │  - Gemini API calls                                     │  │
│  │  - Classification logic                                 │  │
│  └────────────────────┬────────────────────────────────────┘  │
└───────────────────────┼────────────────────────────────────────┘
                        │
                        │ Store results
                        ↓
┌──────────────────────────────────────────────────────────────┐
│                    Neo4j Database                             │
│                                                                │
│  (d:Drug)-[r:TARGETS]->(t:Target)                           │
│  r.classified = true/false                                  │
│  r.relationship_type = "Primary/On-Target"                  │
│  r.mechanism = "Irreversible Inhibitor"                     │
│  r.target_class = "Protein"                                 │
│  r.target_subclass = "Enzyme"                               │
│  r.confidence = 0.95                                        │
└──────────────────────────────────────────────────────────────┘
```

---

## 🔧 DETAILED BACKEND CHANGES REQUIRED

### **Summary of Changes:**

**Total Files to Create:** 1  
**Total Files to Modify:** 3  
**Total Endpoints to Add:** 3  
**Zero Breaking Changes**

---

### **CHANGE 1: Create New Service File**

**File:** `src/drug-neo4j/drug-neo4j-ai.service.ts`

**Action:** Create this file with the following code (see Phase 3.1 above for full implementation)

**Purpose:** Handle all FastAPI AI endpoint calls

**Key Methods:**
- `classifyDrugTarget()` - Single classification
- `batchClassifyDrugTargets()` - Batch classification
- `predictCascadeEffects()` - Cascade prediction

---

### **CHANGE 2: Modify Existing Service**

**File:** `src/drug-neo4j/drug-neo4j.service.ts`

**Location:** Line 345-433 (`getDrugBasicInformation` method)

**Current Code (Lines 410-426):**
```typescript
const biologicTargetsQuery = `
  MATCH (d:Drug {name: $drug_name})-[r:TARGETS]->(t:Target)
  RETURN 
      t.name as target,
      r.relationship_type as relationship_type,
      r.mechanism as mechanism,
      r.target_class as target_class,
      r.target_subclass as target_subclass,
      r.confidence as confidence
  ORDER BY r.confidence DESC, t.name
`;
const biologicTargetsRaw = await this.neo4jService.runQuery(biologicTargetsQuery, { drug_name: drugName });
const biologic_targets = biologicTargetsRaw.map(item => ({
  ...item,
  confidence: this.convertNeo4jInt(item.confidence)
}));
```

**NEW Code to Add AFTER line 426:**
```typescript
// NEW: Auto-classify missing targets
const unclassifiedTargets = biologic_targets.filter(
  t => !t.relationship_type && !t.mechanism && !t.target_class
);

if (unclassifiedTargets.length > 0) {
  console.log(`Found ${unclassifiedTargets.length} unclassified targets, attempting auto-classification...`);
  
  try {
    const aiResult = await this.drugNeo4jAiService.batchClassifyDrugTargets(
      drugName,
      unclassifiedTargets.map(t => t.target)
    );
    
    // Refresh biologic_targets after classification
    const refreshedQuery = `
      MATCH (d:Drug {name: $drug_name})-[r:TARGETS]->(t:Target)
      RETURN 
        t.name as target,
        r.relationship_type as relationship_type,
        r.mechanism as mechanism,
        r.target_class as target_class,
        r.target_subclass as target_subclass,
        r.confidence as confidence
      ORDER BY r.confidence DESC, t.name
    `;
    const refreshed = await this.neo4jService.runQuery(refreshedQuery, { drug_name: drugName });
    biologic_targets = refreshed.map(item => ({
      ...item,
      confidence: this.convertNeo4jInt(item.confidence)
    }));
    
    console.log(`Successfully classified ${aiResult.data.successful} targets`);
  } catch (aiError) {
    console.error('Auto-classification failed, continuing with existing data:', aiError.message);
    // Continue without AI classification - graceful degradation
  }
}
```

**Dependency to Add at Top of File:**
```typescript
// Add to imports section at top of file
constructor(
  private neo4jService: Neo4jService,
  private drugNeo4jAiService?: DrugNeo4jAiService  // NEW - Make optional for graceful degradation
) {}
```

---

### **CHANGE 3: Modify Controller**

**File:** `src/drug-neo4j/drug-neo4j.controller.ts`

**Action 1:** Add import at top
```typescript
import { DrugNeo4jAiService } from './drug-neo4j-ai.service';  // NEW
```

**Action 2:** Update constructor
```typescript
constructor(
  private readonly drugNeo4jService: DrugNeo4jService,
  private readonly drugNeo4jAiService: DrugNeo4jAiService  // NEW
) {}
```

**Action 3:** Add 3 new endpoints (add at end of class, before closing brace)

**Endpoint 1: Single Classification**
```typescript
@Post('classify')
async classifyDrugTarget(
  @Body() body: { drugName: string; targetName: string; additionalContext?: string }
) {
  if (!body.drugName || !body.targetName) {
    throw new Error('Drug name and target name are required');
  }
  
  return await this.drugNeo4jAiService.classifyDrugTarget(
    body.drugName,
    body.targetName,
    body.additionalContext
  );
}
```

**Endpoint 2: Batch Classification**
```typescript
@Post('batch-classify')
async batchClassifyDrugTargets(
  @Body() body: { drugName: string; targets: string[]; additionalContext?: string }
) {
  if (!body.drugName || !body.targets || body.targets.length === 0) {
    throw new Error('Drug name and at least one target are required');
  }
  
  if (body.targets.length > 20) {
    throw new Error('Maximum 20 targets allowed per batch request');
  }
  
  return await this.drugNeo4jAiService.batchClassifyDrugTargets(
    body.drugName,
    body.targets,
    body.additionalContext
  );
}
```

**Endpoint 3: Cascade Prediction**
```typescript
@Post('cascade')
async predictCascade(
  @Body() body: { drugName: string; targetName: string; depth?: number; additionalContext?: string }
) {
  if (!body.drugName || !body.targetName) {
    throw new Error('Drug name and target name are required');
  }
  
  const depth = body.depth || 2;
  if (depth < 1 || depth > 3) {
    throw new Error('Depth must be between 1 and 3');
  }
  
  return await this.drugNeo4jAiService.predictCascadeEffects(
    body.drugName,
    body.targetName,
    depth,
    body.additionalContext
  );
}
```

---

### **CHANGE 4: Update Module**

**File:** `src/drug-neo4j/drug-neo4j.module.ts`

**Current imports should look like:**
```typescript
import { Module } from '@nestjs/common';
import { DrugNeo4jController } from './drug-neo4j.controller';
import { DrugNeo4jService } from './drug-neo4j.service';
import { Neo4jModule } from '../neo4j/neo4j.module';
```

**Add:**
```typescript
import { DrugNeo4jAiService } from './drug-neo4j-ai.service';  // NEW
```

**Update providers array:**
```typescript
@Module({
  imports: [Neo4jModule],
  controllers: [DrugNeo4jController],
  providers: [DrugNeo4jService, DrugNeo4jAiService],  // Add DrugNeo4jAiService
  exports: [DrugNeo4jService],
})
export class DrugNeo4jModule {}
```

---

### **CHANGE 5: Environment Configuration**

**File:** `.env` (in project root)

**Add these lines:**
```env
# FastAPI Integration
FASTAPI_BASE_URL=http://localhost:8000
FASTAPI_API_KEY=your_secure_api_key_here_generate_random_32_char_string
```

**Production values should be:**
```env
FASTAPI_BASE_URL=https://your-fastapi-domain.com
FASTAPI_API_KEY=<generate secure random key>
```

---

### **CHANGE 6: Configuration Module**

**File:** `src/config/neo4j.config.ts` (create if doesn't exist, or add to existing config)

**Add FastAPI configuration:**
```typescript
export default () => ({
  neo4j: {
    uri: process.env.NEO4J_URI,
    username: process.env.NEO4J_USERNAME,
    password: process.env.NEO4J_PASSWORD,
    database: process.env.NEO4J_DATABASE || 'neo4j',
  },
  fastapi: {
    baseUrl: process.env.FASTAPI_BASE_URL || 'http://localhost:8000',
    apiKey: process.env.FASTAPI_API_KEY,
  },
});
```

**If using existing config file, just add fastapi section to the return object.**

---

### **CHANGE 7: Install Dependencies**

**File:** `package.json`

**Run in terminal:**
```bash
npm install axios
npm install --save-dev @types/axios
```

**This will add to dependencies:**
```json
"axios": "^1.x.x",
"@types/axios": "^x.x.x"
```

---

### **CHANGE 8: Update AI Service Dependencies**

**File:** `src/drug-neo4j/drug-neo4j-ai.service.ts`

**Import ConfigService (should already be imported if backend uses @nestjs/config):**

```typescript
import { Injectable, HttpException, HttpStatus } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import axios from 'axios';
```

**If ConfigService is not available, inject it:**
```typescript
constructor(private configService: ConfigService) {
  // Service initialization
}
```

---

## 📝 Code Verification Checklist

After making all changes, verify:

- [ ] `drug-neo4j-ai.service.ts` exists and has all 3 methods
- [ ] `drug-neo4j.service.ts` imports DrugNeo4jAiService
- [ ] `drug-neo4j.service.ts` has auto-classification logic in `getDrugBasicInformation`
- [ ] `drug-neo4j.controller.ts` has DrugNeo4jAiService in constructor
- [ ] `drug-neo4j.controller.ts` has 3 new POST endpoints
- [ ] `drug-neo4j.module.ts` includes DrugNeo4jAiService in providers
- [ ] `.env` has FASTAPI_BASE_URL and FASTAPI_API_KEY
- [ ] `axios` is installed in package.json
- [ ] Backend compiles without errors: `npm run build`
- [ ] Backend starts without errors: `npm run start:dev`

---

## 🎯 Specific Functional Requirements

### **Requirement 1: Auto-Classification on Drug Search**

**Trigger:** When user calls `GET /drugs-neo4j/search/drugs?name=aspirin`

**Expected Behavior:**
1. Backend queries Neo4j for drug basic information
2. Checks if any targets have `relationship_type IS NULL`
3. If found, automatically calls FastAPI batch classification
4. Waits for classification to complete (max 60 seconds)
5. Returns complete data with all classifications

**Error Handling:**
- If FastAPI unavailable: Return existing data with unclassified targets
- If classification fails: Continue without error, log warning
- If timeout: Return existing data, classify in background

---

### **Requirement 2: Manual Classification Endpoint**

**Trigger:** When user calls `POST /drugs-neo4j/classify`

**Request Body:**
```json
{
  "drugName": "aspirin",
  "targetName": "PTGS2",
  "additionalContext": "COX-2 enzyme"
}
```

**Expected Behavior:**
1. Call FastAPI `/classification/classify`
2. Wait for result
3. Return complete classification data
4. Data automatically stored in Neo4j by FastAPI

**Response:**
```json
{
  "success": true,
  "data": {
    "drug_name": "aspirin",
    "target_name": "PTGS2",
    "relationship_type": "Primary/On-Target",
    "mechanism": "Irreversible Inhibitor",
    "target_class": "Protein",
    "target_subclass": "Enzyme",
    "confidence": 0.95,
    "reasoning": "Aspirin irreversibly acetylates COX-2...",
    "stored_in_db": true
  }
}
```

---

### **Requirement 3: Batch Classification Endpoint**

**Trigger:** When user calls `POST /drugs-neo4j/batch-classify`

**Request Body:**
```json
{
  "drugName": "aspirin",
  "targets": ["PTGS2", "NFKBIA", "TGFBR1"],
  "additionalContext": "Multiple targets"
}
```

**Expected Behavior:**
1. Validate targets array (max 20 targets)
2. Call FastAPI `/classification/batch`
3. Wait for all classifications (max 120 seconds)
4. Return summary with success/failure counts
5. All data stored in Neo4j by FastAPI

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
        "target_name": "PTGS2",
        "status": "success",
        "classification": {...}
      }
    ]
  }
}
```

---

### **Requirement 4: Cascade Prediction Endpoint**

**Trigger:** When user calls `POST /drugs-neo4j/cascade`

**Request Body:**
```json
{
  "drugName": "aspirin",
  "targetName": "PTGS2",
  "depth": 2,
  "additionalContext": "COX-2 inhibition"
}
```

**Expected Behavior:**
1. Validate depth (1-3)
2. Call FastAPI `/cascade/predict`
3. Wait for prediction (max 60 seconds)
4. Return complete cascade data
5. All relationships stored in Neo4j by FastAPI

**Response:**
```json
{
  "success": true,
  "data": {
    "drug_name": "aspirin",
    "target_name": "PTGS2",
    "direct_effects": [...],
    "secondary_effects": [...],
    "tertiary_effects": [],
    "stored_in_db": true
  }
}
```

---

### **Requirement 5: Graceful Degradation**

**Scenario:** FastAPI service is down or unreachable

**Expected Behavior:**
- Existing endpoints continue to work
- Unclassified targets shown as "Unclassified" status
- No errors thrown to user
- Warning logged in backend
- User can still access all existing data
- Manual classification endpoints return 503 Service Unavailable

**Code Pattern:**
```typescript
try {
  const result = await this.drugNeo4jAiService.classifyDrugTarget(...);
} catch (error) {
  console.error('AI service unavailable:', error);
  // Return existing data without error
  return existingData;
}
```

---

## 🚨 Critical Implementation Notes

### **Note 1: Service Availability Check**

**Add health check before calling FastAPI:**

```typescript
private async isFastApiAvailable(): Promise<boolean> {
  try {
    const response = await axios.get(`${this.fastApiBaseUrl}/health`, {
      timeout: 5000
    });
    return response.status === 200;
  } catch {
    return false;
  }
}

// Use before classification:
if (!(await this.isFastApiAvailable())) {
  console.warn('FastAPI service unavailable, skipping auto-classification');
  return existingData;
}
```

---

### **Note 2: Rate Limiting Awareness**

**Gemini API limits:**
- 60 requests per minute
- Sequential processing (one per target)
- 1-second delay between calls

**Backend should:**
- Use batch endpoint for 3+ targets (more efficient)
- Set appropriate timeouts (30s for single, 120s for batch)
- Not queue requests if rate limit hit
- Return error to user with clear message

---

### **Note 3: Data Validation**

**Before calling FastAPI, validate:**
- Drug exists in Neo4j
- Target exists in Neo4j
- Drug-target relationship exists
- Relationship not already fully classified

**Example:**
```typescript
// In classifyDrugTarget, check first:
const exists = await this.neo4jService.runQuery(`
  MATCH (d:Drug {name: $drug_name})-[r:TARGETS]->(t:Target {name: $target_name})
  RETURN r.classified as is_classified
`, { drug_name: drugName, target_name: targetName });

if (exists.length === 0) {
  throw new HttpException(
    'Drug-target relationship not found',
    HttpStatus.NOT_FOUND
  );
}

if (exists[0].is_classified === true) {
  // Already classified, return existing
  return await this.getExistingClassification(drugName, targetName);
}
```

---

### **Note 4: Background Processing (Optional Enhancement)**

**For better UX, classify in background:**

```typescript
// Instead of blocking:
async getDrugBasicInformation(drugName: string) {
  // ... get basic info ...
  
  // Fire-and-forget background classification
  if (unclassifiedTargets.length > 0) {
    this.drugNeo4jAiService.batchClassifyDrugTargets(
      drugName,
      unclassifiedTargets.map(t => t.target)
    ).then(result => {
      console.log(`Background classification complete: ${result.data.successful}`);
    }).catch(error => {
      console.error('Background classification failed:', error);
    });
  }
  
  // Return immediately with existing data
  return { basic_information, drug_target_network, similar_drugs, biologic_targets };
}
```

**Trade-off:**
- ✅ Faster response time
- ✅ Better UX
- ❌ Initial data incomplete
- ❌ More complex state management

---

---

## ✅ Integration Checklist

### **Backend (NestJS) Tasks:**

- [ ] Add `axios` dependency
- [ ] Add FastAPI config to `.env`
- [ ] Create `drug-neo4j-ai.service.ts`
- [ ] Update `drug-neo4j.service.ts` to auto-classify
- [ ] Add 3 new endpoints to `drug-neo4j.controller.ts`
- [ ] Update module imports
- [ ] Test integration locally

### **FastAPI Tasks:**

- [ ] Deploy FastAPI service to EC2
- [ ] Configure API key authentication
- [ ] Test all endpoints
- [ ] Monitor performance and rate limits
- [ ] Set up logging and error tracking

### **Testing:**

- [ ] Test single classification via backend
- [ ] Test batch classification via backend
- [ ] Test cascade prediction via backend
- [ ] Test auto-classification flow
- [ ] Verify data stored in Neo4j correctly
- [ ] Test error handling and fallbacks

---

## 🔍 Key Differences & Alignment

### **What Matches:**

| Backend Field | FastAPI Output | Status |
|--------------|----------------|--------|
| `relationship_type` | `relationship_type` | ✅ Match |
| `mechanism` | `mechanism` | ✅ Match |
| `target_class` | `target_class` | ✅ Match |
| `target_subclass` | `target_subclass` | ✅ Match |
| `confidence` | `confidence` | ✅ Match |
| `classified` | Set to `true` | ✅ Match |

**Perfect alignment! No schema changes needed.**

---

### **What's New:**

| Backend Before | Backend After | Status |
|----------------|---------------|--------|
| Returns `null` for unclassified | Auto-calls FastAPI | ✅ NEW |
| No classification generation | AI-powered classification | ✅ NEW |
| Manual data entry only | Automated via Gemini API | ✅ NEW |
| No cascade prediction | Full cascade API | ✅ NEW |

---

## 🚨 Potential Issues & Solutions

### **Issue 1: FastAPI Service Downtime**

**Problem:** What if FastAPI service is unavailable?

**Solution:** Graceful degradation in backend
```typescript
try {
  const result = await this.drugNeo4jAiService.classifyDrugTarget(...);
} catch (error) {
  console.error('AI service unavailable:', error);
  // Continue without classification
  return {
    ...basicData,
    biologic_targets: [...existing targets, ...unclassified_targets]
  };
}
```

---

### **Issue 2: Rate Limiting**

**Problem:** Gemini API has rate limits (60 requests/min)

**Solution:** 
- Use batch endpoint for multiple targets
- Add retry logic with exponential backoff
- Queue requests if needed
- Cache results in Neo4j

---

### **Issue 3: Slow Response Times**

**Problem:** AI classification takes 2-3 seconds per target

**Solution:**
- **For UI:** Show loading indicator
- **For API:** Return immediately, classify in background
- **For batch:** Progress updates via WebSockets (optional)

---

### **Issue 4: Cost Control**

**Problem:** Gemini API costs money per request

**Solution:**
- Only classify when `r.classified IS NULL OR false`
- Cache results in Neo4j permanently
- Add admin flag to disable auto-classification
- Monitor API usage

---

## 📝 Summary

### **Current State:**
- ✅ Backend queries Neo4j for classification data
- ✅ Returns `relationship_type`, `mechanism`, `target_class`, etc.
- ❌ Cannot generate new classifications
- ❌ No AI integration

### **Proposed State:**
- ✅ Backend queries Neo4j (existing flow)
- ✅ Auto-detects missing classifications
- ✅ Calls FastAPI endpoints for AI classification
- ✅ Returns complete data immediately
- ✅ Background classification supported

### **Integration Benefits:**
1. **Zero Breaking Changes** - Existing endpoints work as before
2. **Enhanced Functionality** - Auto-populate missing data
3. **Better UX** - Complete classification data always available
4. **Flexible** - Manual or automatic classification
5. **Cost-Effective** - Classify once, cache forever

---

## 🎯 Next Steps

1. **Review this document** with backend team
2. **Implement drug-neo4j-ai.service.ts**
3. **Update getDrugBasicInformation** for auto-classification
4. **Add new endpoints** to controller
5. **Deploy FastAPI** service
6. **Test integration** end-to-end
7. **Monitor performance** and costs
8. **Document for frontend** team

---

**🎉 Integration is straightforward and non-breaking!**

