# Figma Design - Neo4j Queries Mapping

**Project:** Drug-Target Graph Database Explorer  
**Purpose:** Map Figma UI designs to Neo4j queries  
**Last Updated:** October 16, 2025

---

## 📋 Design 1: Search Drugs - Basic Information Tab

**Figma Section:** Search Drugs Page → Basic Information Tab  
**Current View:** Aspirin drug details

---

## 🔍 UI Elements to Query Mapping

### **1. Basic Information Section**

**UI Fields Displayed:**
- Name: ASPIRIN
- Disease Area: neurology/psychiatry, endo... (truncated)
- Vendor: Tocris, MicroSource, Micros... (truncated)
- Development Phase: Launched
- Purity: 99.34%
- Indication: headache, fever, toothache

**Query:**
```cypher
MATCH (d:Drug {name: $drug_name})
RETURN d.name as name,
       d.disease_area as disease_area,
       d.vendor as vendor,
       d.phase as development_phase,
       d.purity as purity,
       d.indication as indication
```

**Parameters:**
- `$drug_name`: "ASPIRIN" (or uppercase drug name)

**Expected Output:**
```json
{
  "name": "ASPIRIN",
  "disease_area": "neurology/psychiatry, endocrinology, inflammation",
  "vendor": "Tocris, MicroSource, Microsource Discovery",
  "development_phase": "Launched",
  "purity": "99.34%",
  "indication": "headache, fever, toothache"
}
```

**Module:** `streamlit_app.py` - `get_drug_details()` method  
**API Endpoint:** None (Backend queries Neo4j directly)

---

### **2. Mechanism of Action (MoA)**

**UI Element:**
- MoA: "cyclooxygenase inhibitor"
- Link: "Find other drugs with same MOA"

**Query for MoA:**
```cypher
MATCH (d:Drug {name: $drug_name})
RETURN d.moa as mechanism_of_action
```

**Query for Similar Drugs by MoA:**
```cypher
MATCH (current:Drug {name: $drug_name})
MATCH (d:Drug)
WHERE d.moa = current.moa 
  AND d.name <> current.name
  AND d.moa IS NOT NULL
RETURN d.name as drug_name,
       d.moa as moa,
       d.phase as phase
ORDER BY d.name
LIMIT $limit
```

**Parameters:**
- `$drug_name`: "ASPIRIN"
- `$limit`: 20 (or desired limit)

**Expected Output (Similar Drugs):**
```json
[
  {
    "drug_name": "IBUPROFEN",
    "moa": "cyclooxygenase inhibitor",
    "phase": "Launched"
  },
  {
    "drug_name": "NAPROXEN",
    "moa": "cyclooxygenase inhibitor",
    "phase": "Launched"
  }
]
```

**Module:** `streamlit_app.py` - `get_similar_drugs_by_moa()` method  
**Query Reference:** See `Queries.md` - Query #10 (Get Similar Drugs by MOA)

---

### **3. SMILES Notation**

**UI Element:**
- Raw SMILES string displayed
- Used for 3D molecular structure visualization

**Query:**
```cypher
MATCH (d:Drug {name: $drug_name})
RETURN d.smiles as smiles_notation
```

**Parameters:**
- `$drug_name`: "ASPIRIN"

**Expected Output:**
```json
{
  "smiles_notation": "CC(=O)Oc1ccccc1C(=O)O"
}
```

**Note:** The UI may display multiple SMILES strings concatenated. The query returns a single SMILES string. If multiple SMILES are stored, adjust query accordingly.

**Module:** `streamlit_app.py` - `get_drug_details()` method  
**Query Reference:** See `Queries.md` - Query #4 (Get Drug Details) - includes `d.smiles`

---

### **4. Complete Basic Information (Combined Query)**

**Single Query for All Basic Information Fields:**

```cypher
MATCH (d:Drug {name: $drug_name})
RETURN d.name as name,
       d.moa as mechanism_of_action,
       d.phase as development_phase,
       d.smiles as smiles_notation,
       d.disease_area as disease_area,
       d.indication as indication,
       d.vendor as vendor,
       d.purity as purity
```

**Parameters:**
- `$drug_name`: "ASPIRIN" (case-sensitive, usually uppercase)

**Expected Output:**
```json
{
  "name": "ASPIRIN",
  "mechanism_of_action": "cyclooxygenase inhibitor",
  "development_phase": "Launched",
  "smiles_notation": "CC(=O)Oc1ccccc1C(=O)O",
  "disease_area": "neurology/psychiatry, endocrinology, inflammation",
  "indication": "headache, fever, toothache",
  "vendor": "Tocris, MicroSource, Microsource Discovery",
  "purity": "99.34%"
}
```

**Module:** `streamlit_app.py` - `get_drug_details()` method  
**Query Reference:** See `Queries.md` - Query #4 (Get Drug Details)

---

### **5. Drug Search (Input Field)**

**UI Element:**
- Search input: "Enter drug name"
- Example buttons: "ASPIRIN", "INSULIN", "MORPHIN", "METFORMIN"

**Query:**
```cypher
MATCH (d:Drug)
WHERE toLower(d.name) CONTAINS toLower($search_term)
RETURN d.name as drug_name,
       d.moa as moa,
       d.phase as phase
ORDER BY d.name
LIMIT $limit
```

**Parameters:**
- `$search_term`: User input (e.g., "aspirin")
- `$limit`: 20 (or desired limit)

**Expected Output:**
```json
[
  {
    "drug_name": "ASPIRIN",
    "moa": "cyclooxygenase inhibitor",
    "phase": "Launched"
  }
]
```

**Module:** `streamlit_app.py` - `search_drugs()` method  
**Query Reference:** See `Queries.md` - Query #6 (Search Drugs)

---

## 📊 Summary Table

| UI Element | Query Type | Query Location |
|------------|-----------|----------------|
| Basic Information (all fields) | Single query | `Queries.md` - Query #4 |
| Drug Name | Part of basic info | `Queries.md` - Query #4 |
| Disease Area | Part of basic info | `Queries.md` - Query #4 |
| Vendor | Part of basic info | `Queries.md` - Query #4 |
| Development Phase | Part of basic info | `Queries.md` - Query #4 |
| Purity | Part of basic info | `Queries.md` - Query #4 |
| Indication | Part of basic info | `Queries.md` - Query #4 |
| Mechanism of Action | Part of basic info | `Queries.md` - Query #4 |
| SMILES Notation | Part of basic info | `Queries.md` - Query #4 |
| Similar Drugs by MoA | Separate query | `Queries.md` - Query #10 |
| Drug Search | Separate query | `Queries.md` - Query #6 |

---

## 🎯 Implementation Notes

1. **Case Sensitivity:** Drug names in Neo4j are typically stored in UPPERCASE. Ensure `$drug_name` parameter matches case.

2. **SMILES Multiple Values:** If SMILES field contains multiple values separated by commas, consider:
   - Storing as array in Neo4j, or
   - Splitting in application code after retrieval

3. **Truncated Display:** Fields like "disease_area" and "vendor" may be truncated in UI. Full values are returned by queries.

4. **3D Molecular Structure:** The 3D visualization uses the SMILES string. The visualization library (e.g., py3Dmol, stmol) handles rendering.

5. **Backend Integration:** All these queries are executed directly by the backend. No API calls needed for basic information retrieval.

---

## 📝 Next Designs

When additional Figma designs are provided, they will be added to this document with:
- UI element description
- Corresponding Neo4j queries
- Expected output format
- Implementation notes

---

---

## 📋 Design 2: Search Drugs - Biological Targets Tab

**Figma Section:** Search Drugs Page → Biological Targets Tab  
**Current View:** Aspirin biological targets table with pagination

---

## 🔍 UI Elements to Query Mapping

### **1. Total Biological Targets Count**

**UI Element:** 
- Summary text: "This drug targets 19 biological proteins/receptors"

**Query:**
```cypher
MATCH (d:Drug {name: $drug_name})-[:TARGETS]->(t:Target)
RETURN count(DISTINCT t) as total_targets
```

**Parameters:**
- `$drug_name`: "ASPIRIN"

**Expected Output:**
```json
{
  "total_targets": 19
}
```

**Module:** `streamlit_app.py` - `get_drug_details()` method  
**API Endpoint:** None (Backend queries Neo4j directly)

---

### **2. Biological Targets Table Data (Paginated)**

**UI Elements:**
- Table columns: TARGET, RELATIONSHIP TYPE, MECHANISM, TARGET CLASS, CONFIDENCE
- Pagination: "1-10 of 19"
- Rows per page: 10

**Query:**
```cypher
MATCH (d:Drug {name: $drug_name})-[r:TARGETS]->(t:Target)
RETURN t.name as target,
       r.relationship_type as relationship_type,
       r.mechanism as mechanism,
       r.target_class as target_class,
       r.confidence as confidence
ORDER BY t.name
SKIP $skip
LIMIT $limit
```

**Parameters:**
- `$drug_name`: "ASPIRIN"
- `$skip`: 0 (for first page), 10 (for second page), etc.
- `$limit`: 10 (rows per page)

**Expected Output:**
```json
[
  {
    "target": "AKR1C1",
    "relationship_type": "Secondary/Off-target",
    "mechanism": "Inhibitor",
    "target_class": "Protein",
    "confidence": 80.0
  },
  {
    "target": "AKR1C2",
    "relationship_type": "Secondary/Off-target",
    "mechanism": "Inhibitor",
    "target_class": "Protein",
    "confidence": 75.0
  }
]
```

**Module:** `streamlit_app.py` - `get_drug_details()` method  
**Query Reference:** See `Queries.md` - Query #5A (Get Drug Targets with Classification)  
**API Endpoint:** None (Backend queries Neo4j directly)

---

### **3. Drug Search Input (Same as Design 1)**

**UI Element:** "Enter drug name" input field

**Query:**
```cypher
MATCH (d:Drug)
WHERE toLower(d.name) CONTAINS toLower($search_term)
RETURN d.name as drug_name,
       d.moa as moa,
       d.phase as phase
ORDER BY d.name
LIMIT $limit
```

**Parameters:**
- `$search_term`: User input (e.g., "aspirin")
- `$limit`: 20

**Module:** `streamlit_app.py` - `search_drugs()` method  
**Query Reference:** See `Queries.md` - Query #6 (Search Drugs)

---

## 📋 Design 3: Search Drugs - Biological Targets Tab with Sidebar

**Figma Section:** Search Drugs Page → Biological Targets Tab → Sidebar Detail View  
**Current View:** Aspirin targets table with detailed AKR1C1 target sidebar

---

## 🔍 UI Elements to Query Mapping

### **1. Target Detail Information (Sidebar)**

**UI Elements:**
- Target: AKR1C1
- Relationship Type: Secondary/Off-Target
- Mechanism: Inhibitor
- Target Class: Protein
- Confidence: 80%
- Scientific Reasoning: Long text explanation

**Query:**
```cypher
MATCH (d:Drug {name: $drug_name})-[r:TARGETS]->(t:Target {name: $target_name})
RETURN r.relationship_type as relationship_type,
       r.mechanism as mechanism,
       r.target_class as target_class,
       r.target_subclass as target_subclass,
       r.confidence as confidence,
       r.reasoning as scientific_reasoning,
       r.classification_source as source,
       r.classification_timestamp as timestamp
```

**Parameters:**
- `$drug_name`: "ASPIRIN"
- `$target_name`: "AKR1C1"

**Expected Output:**
```json
{
  "relationship_type": "Secondary/Off-target",
  "mechanism": "Inhibitor",
  "target_class": "Protein",
  "target_subclass": "Enzyme",
  "confidence": 80.0,
  "scientific_reasoning": "While Aspirin's primary mechanism involves COX-1 and COX-2 inhibition, it exhibits some inhibitory activity against AKR1C1...",
  "source": "Gemini_API",
  "timestamp": "2025-10-16T10:00:00Z"
}
```

**Module:** `streamlit_app.py` - `get_drug_target_classification()` method  
**Query Reference:** See `Queries.md` - Query #14 (Get Existing Classification)  
**API Endpoint:** None (Backend queries Neo4j directly, unless classification missing then calls AI API)

---

### **2. Biological Targets Table (Same as Design 2)**

**UI Element:** Main table with target list

**Query:** Same as Design 2, Query #2

**Module:** `streamlit_app.py` - `get_drug_details()` method

---

## 📋 Design 4: Search Drugs - Drug Target Network Tab

**Figma Section:** Search Drugs Page → Drug Target Network Tab  
**Current View:** Aspirin network statistics and visualization area

---

## 🔍 UI Elements to Query Mapping

### **1. Network Statistics Card**

**UI Elements:**
- Primary Effects: 2
- Secondary Effects: 17
- Unknown Type: 0
- Unclassified: 0
- Under Analysis: 0
- Analysis Progress: 100%

**Query:**
```cypher
MATCH (d:Drug {name: $drug_name})-[r:TARGETS]->(t:Target)
RETURN 
    count(CASE WHEN r.relationship_type = 'Primary/On-Target' THEN 1 END) as primary_effects,
    count(CASE WHEN r.relationship_type = 'Secondary/Off-Target' THEN 1 END) as secondary_effects,
    count(CASE WHEN r.relationship_type = 'Unknown' OR r.relationship_type IS NULL THEN 1 END) as unknown_type,
    count(CASE WHEN r.classified = false OR r.classified IS NULL THEN 1 END) as unclassified,
    count(CASE WHEN r.classified IS NULL THEN 1 END) as under_analysis,
    count(t) as total_targets
```

**Parameters:**
- `$drug_name`: "ASPIRIN"

**Expected Output:**
```json
{
  "primary_effects": 2,
  "secondary_effects": 17,
  "unknown_type": 0,
  "unclassified": 0,
  "under_analysis": 0,
  "total_targets": 19
}
```

**Note:** Analysis Progress = `((total_targets - unclassified - under_analysis) / total_targets) * 100`

**Module:** `streamlit_app.py` - `get_drug_network()` method  
**Query Reference:** See `Queries.md` - Query #5B (Get Drug Target Statistics)  
**API Endpoint:** None (Backend queries Neo4j directly)

---

### **2. Drug Target Network Visualization Data**

**UI Elements:**
- Network graph area (placeholder in design)
- Legend: Primary Effects (gray), Secondary Effects (red/pink), Unknown Type (green), Unclassified (blue)

**Query:**
```cypher
MATCH (d:Drug {name: $drug_name})
OPTIONAL MATCH (d)-[r:TARGETS]->(t:Target)
OPTIONAL MATCH (t)<-[:TARGETS]-(other:Drug)
WHERE other.name <> $drug_name
RETURN d.name as drug_name,
       d.moa as moa,
       d.phase as phase,
       collect(DISTINCT {
         target: t.name,
         relationship_type: r.relationship_type,
         mechanism: r.mechanism,
         target_class: r.target_class,
         confidence: r.confidence,
         classified: r.classified
       }) as targets,
       collect(DISTINCT {
         other_drug: other.name,
         other_moa: other.moa,
         other_phase: other.phase
       }) as other_drugs
```

**Alternative Query (For vis.js/Plotly Network):**
```cypher
MATCH (d:Drug {name: $drug_name})-[r:TARGETS]->(t:Target)
OPTIONAL MATCH (t)<-[:TARGETS]-(other:Drug)
WHERE other.name <> $drug_name
RETURN d.name as drug,
       d.moa as moa,
       d.phase as phase,
       t.name as target,
       r.relationship_type as relationship_type,
       r.mechanism as mechanism,
       r.target_class as target_class,
       r.confidence as confidence,
       r.classified as classified,
       other.name as other_drug,
       other.moa as other_moa,
       other.phase as other_phase
LIMIT 100
```

**Parameters:**
- `$drug_name`: "ASPIRIN"

**Expected Output:** Returns nodes and edges data for graph visualization

**Node Groups (for visualization):**
- `central_drug` - The searched drug
- `primary_target` - Targets with `relationship_type = 'Primary/On-Target'`
- `secondary_target` - Targets with `relationship_type = 'Secondary/Off-Target'`
- `unknown_type` - Targets with `relationship_type = 'Unknown'` or NULL
- `unclassified` - Targets with `classified = false`
- `other_drug` - Other drugs targeting the same targets

**Module:** `streamlit_app.py` - `get_drug_network()` method  
**Query Reference:** See `Queries.md` - Query #8 (Get Drug Network)  
**API Endpoint:** None (Backend queries Neo4j directly)

---

### **3. Drug Search Input (Same as Design 1)**

**UI Element:** "Enter drug name" input field and example buttons

**Query:** Same as Design 1, Query #5

**Module:** `streamlit_app.py` - `search_drugs()` method

---

## 📊 Complete Summary Table

| Design | UI Element | Query Type | Module | Query Reference |
|--------|------------|-----------|--------|-----------------|
| **Design 1** | Basic Information | Single query | `get_drug_details()` | Query #4 |
| **Design 1** | MoA Display | Single query | `get_drug_details()` | Query #4 |
| **Design 1** | Similar Drugs by MoA | Separate query | `get_similar_drugs_by_moa()` | Query #10 |
| **Design 1** | SMILES Notation | Single query | `get_drug_details()` | Query #4 |
| **Design 1** | Drug Search | Separate query | `search_drugs()` | Query #6 |
| **Design 2** | Total Targets Count | Count query | `get_drug_details()` | Query #5A |
| **Design 2** | Targets Table (Paginated) | Paginated query | `get_drug_details()` | Query #5A |
| **Design 3** | Target Detail Sidebar | Single query | `get_drug_target_classification()` | Query #14 |
| **Design 3** | Targets Table | Same as Design 2 | `get_drug_details()` | Query #5A |
| **Design 4** | Network Statistics | Aggregation query | `get_drug_network()` | Query #5B |
| **Design 4** | Network Visualization | Graph query | `get_drug_network()` | Query #8 ⏭️ |
| **Design 5** | Similar Drugs Table | Relationship query | `get_drug_similarity_analysis()` | Query #7 |
| **Design 6** | Target Basic Information | Aggregation query | `get_target_details()` | - |
| **Design 6** | Drugs Table (Paginated) | Paginated query | `get_target_details()` | - |
| **Design 6** | Drug Details Expander | Single query | `get_drug_details()` | Query #4 |
| **Design 6** | All Targets for Drug | List query | `get_drug_details()` | Query #5 |
| **Design 7** | Development Phases Distribution | Aggregation query | `get_target_details()` | Query #19 |
| **Design 7** | Mechanisms Distribution | Aggregation query | `get_target_details()` | - |
| **Design 7** | Detailed Drug Table | Paginated query | `get_target_details()` | Query #5A |
| **Design 8** | Search by MOA | Search query | `search_drugs_by_moa()` | - |
| **Design 9** | Therapeutic Class Overview | Aggregation query | `get_therapeutic_class_analysis()` | - |
| **Design 9** | Drugs per Therapeutic Class Chart | Same query | `get_therapeutic_class_analysis()` | - |
| **Design 10** | Top Mechanisms of Action | Statistics query | `get_moa_statistics()` | - |
| **Design 11** | Get Classification for Drug-Target Pair | Classification query | `get_existing_classification()` | - |
| **Design 12** | Drug Distribution by Phase | Aggregation query | `get_phase_statistics()` | - |
| **Design 12** | Top 15 Mechanisms of Action | Aggregation query | `get_moa_statistics()` | - |
| **Design 12** | Top 15 Drugs by Target Count | Aggregation query | `get_top_drugs_by_targets()` | - |
| **Design 12** | Top 15 Targets by Drug Count | Aggregation query | `get_top_targets_by_drugs()` | - |
| **Design 13** | Drug Comparison Details | Multiple queries | `get_drug_comparison()` | Query #26 |
| **Design 14** | Therapeutic Pathway Analysis | Single query with grouping | `get_therapeutic_pathways()` | - |
| **Design 15** | Top 10 Polypharmacology Drugs | Aggregation query | `get_drug_repurposing_insights()` | - |
| **Design 15** | Top 10 Druggable Targets | Aggregation query | `get_drug_repurposing_insights()` | - |

---

## 🎯 Implementation Notes

### **General Notes:**

1. **Case Sensitivity:** Drug names in Neo4j are typically stored in UPPERCASE. Ensure `$drug_name` parameter matches case.

2. **Pagination:** For Design 2, use `SKIP` and `LIMIT` parameters:
   - Page 1: `SKIP 0 LIMIT 10`
   - Page 2: `SKIP 10 LIMIT 10`
   - Page N: `SKIP (N-1)*10 LIMIT 10`

3. **Classification Status:** 
   - If `r.classified = true` → Classification exists (use existing data)
   - If `r.classified = false` or NULL → Call AI Classification API

4. **Network Visualization:** 
   - Frontend processes query results to create nodes and edges
   - Node colors/groups based on `relationship_type` and `classified` status
   - Visualization libraries: vis.js, Plotly, or D3.js

5. **Backend Integration:** All queries execute directly in Neo4j. No API calls needed for data retrieval (except when AI classification is missing).

---

---

## 🧪 Testing Queries

All queries in this document can be tested using the test suite:

**Test Suite:** `test_figma_queries.py`

**Run Tests:**
```bash
cd api_endpoints
python test_figma_queries.py
```

**Test Output:**
- Console output with test results
- JSON file: `figma_queries_test_results.json` with detailed results
- Test tracker: `FIGMA_QUERIES_TEST_TRACKER.md`

**Test Coverage:**
- ✅ 30 queries from Designs 1-15 (Network Visualization skipped)
- ✅ Validates query execution
- ✅ Checks expected fields
- ✅ Validates data presence
- ✅ Tests with sample data (ASPIRIN, PTGS1)
- ⏭️ Network Visualization query skipped (handled by dedicated endpoint)

See `FIGMA_QUERIES_TEST_TRACKER.md` for test status and results.

---

---

## 📋 Design 5: Search Drugs - Similar Drugs Tab

**Figma Section:** Search Drugs Page → Similar Drugs Tab  
**Current View:** Aspirin similar drugs table with shared targets

---

## 🔍 UI Elements to Query Mapping

### **1. Similar Drugs Table**

**UI Elements:**
- Table columns: DRUG NAME, MECHANISM OF ACTION, DEVELOPMENT PHASE, SHARED TARGETS, SIMILARITY
- Pagination: "1-10 of 19"
- Similarity labels: HIGH (green), GOOD (blue), MODERATE (orange)

**Query:**
```cypher
MATCH (d1:Drug {name: $drug_name})-[:TARGETS]->(t:Target)<-[:TARGETS]-(d2:Drug)
WHERE d2.name <> $drug_name
WITH d2, count(t) as common_targets
ORDER BY common_targets DESC
LIMIT $limit
RETURN d2.name as drug, 
       d2.moa as mechanism_of_action, 
       d2.phase as development_phase, 
       common_targets as shared_targets
```

**Parameters:**
- `$drug_name`: "ASPIRIN"
- `$limit`: 19 (or desired limit)

**Expected Output:**
```json
[
  {
    "drug": "salicylic acid",
    "mechanism_of_action": "cyclooxygenase inhibitor",
    "development_phase": "Launched",
    "shared_targets": 4
  },
  {
    "drug": "mesalazine",
    "mechanism_of_action": "cyclooxygenase inhibitor",
    "development_phase": "Launched",
    "shared_targets": 3
  }
]
```

**Note:** Similarity calculation is done in application logic:
- `similarity_score = (shared_targets / total_targets) * 100`
- HIGH: >= 50%
- GOOD: >= 30%
- MODERATE: < 30%

**Module:** `streamlit_app.py` - `get_drug_similarity_analysis()` method  
**Query Reference:** See `Queries.md` - Query #7 (Get Similar Drugs)  
**API Endpoint:** None (Backend queries Neo4j directly)

---

## 📋 Design 6: Search Targets - Target Information Tab

**Figma Section:** Search Targets Page → Target Information (first tab)  
**Current View:** Target basic information and drugs table (paginated)

---

## 🔍 UI Elements to Query Mapping

### 1) Target Basic Information Card

**UI Fields:**
- Target Class
- Target Subclass
- Targeting Drugs (count)
- Classified Interactions (X/Y)
- Classification Progress (%)

**Query:**
```cypher
MATCH (t:Target {name: $target_name})<-[r:TARGETS]-(d:Drug)
WITH 
  count(r) as total_interactions,
  count(CASE WHEN r.classified = true THEN 1 END) as classified_interactions,
  head([x IN collect(r.target_class) WHERE x IS NOT NULL]) as target_class,
  head([x IN collect(r.target_subclass) WHERE x IS NOT NULL]) as target_subclass,
  count(DISTINCT d) as targeting_drugs
RETURN 
  target_class,
  target_subclass,
  targeting_drugs,
  total_interactions,
  classified_interactions,
  CASE WHEN total_interactions = 0 THEN 0 
       ELSE round((toFloat(classified_interactions) / toFloat(total_interactions)) * 100) END as classification_progress
```

**Parameters:**
- `$target_name`: "DRD2" (example)

**Expected Output:**
```json
{
  "target_class": "Protein",
  "target_subclass": "Receptor",
  "targeting_drugs": 126,
  "total_interactions": 126,
  "classified_interactions": 126,
  "classification_progress": 100
}
```

**Module:** `streamlit_app.py` - `get_target_details()` and `get_target_network_data()` usage  
**API Endpoint:** None (Backend queries Neo4j directly)

---

### 2) Drugs Table (Paginated)

**UI Columns:** NAME, CLASSIFICATION, MECHANISM, PHASE

**Query:**
```cypher
MATCH (t:Target {name: $target_name})<-[r:TARGETS]-(d:Drug)
RETURN 
  d.name as drug_name,
  CASE WHEN r.classified = true THEN 'Classified' ELSE 'Unclassified' END as classification,
  r.mechanism as mechanism,
  d.phase as phase
ORDER BY d.name
SKIP $skip
LIMIT $limit
```

**Parameters:**
- `$target_name`: "DRD2" (example)
- `$skip`: 0 (page 1), 10 (page 2), etc.
- `$limit`: 10

**Expected Output:**
```json
[
  {"drug_name": "(R)-(+)-apomorphine", "classification": "Classified", "mechanism": "dopamine receptor agonist", "phase": "Launched"}
]
```

**Module:** `streamlit_app.py` - `get_target_details()`  
**Query Reference:** Related to `Queries.md` - Query #5A/#14 patterns  
**API Endpoint:** None (Backend queries Neo4j directly)

---

### 3) Search Targets (Input)

Use existing search query (from Design 2/earlier docs):
```cypher
MATCH (t:Target)
WHERE toLower(t.name) CONTAINS toLower($search_term)
RETURN t.name as target
ORDER BY t.name
LIMIT $limit
```

**Module:** `streamlit_app.py` - `search_targets()`

---

### 4) Drug Details Expander (Right Panel)

**UI Fields:**
- Name
- Classification
- Mechanism
- Phase
- Indication
- Therapeutic Class
- All Targets (list with "+X more")

**Query:**
```cypher
MATCH (d:Drug {name: $drug_name})
RETURN d.name as name,
       d.moa as mechanism,
       d.phase as phase,
       d.indication as indication,
       d.disease_area as disease_area
```

**Query for All Targets:**
```cypher
MATCH (d:Drug {name: $drug_name})-[:TARGETS]->(t:Target)
RETURN t.name as target
ORDER BY t.name
```

**Parameters:**
- `$drug_name`: "(R)-(-)-apomorphine" (example)

**Expected Output (Basic Info):**
```json
{
  "name": "(R)-(-)-apomorphine",
  "mechanism": "dopamine receptor agonist",
  "phase": "Launched",
  "indication": "Not Specified",
  "disease_area": "Not Specified"
}
```

**Expected Output (All Targets):**
```json
[
  {"target": "ADRA2A"},
  {"target": "ADRA2B"},
  {"target": "ADRA2C"},
  {"target": "CALY"},
  {"target": "DRD1"},
  {"target": "DRD2"}
]
```

**Note:** Classification status is determined by checking `r.classified = true` for the specific drug-target relationship.

**Module:** `streamlit_app.py` - `get_drug_details()` method  
**Query Reference:** See `Queries.md` - Query #4 (Get Drug Details) and Query #5 (Get Drug Targets)  
**API Endpoint:** None (Backend queries Neo4j directly)

---

## 📋 Design 7: Search Targets - Drug Analysis Tab

**Figma Section:** Search Targets Page → Drug Analysis Tab  
**Current View:** DRD2 target analysis with two graphs and detailed drug table

---

## 🔍 UI Elements to Query Mapping

### 1) Development Phases Distribution Chart (Donut/Pie Chart)

**UI Element:** "Development Phases for DRD2 Targeting Drugs" - Donut chart showing phase distribution

**Query:**
```cypher
MATCH (t:Target {name: $target_name})<-[r:TARGETS]-(d:Drug)
WHERE d.phase IS NOT NULL AND d.phase <> ''
RETURN d.phase as phase, count(d) as drug_count
ORDER BY drug_count DESC
```

**Parameters:**
- `$target_name`: "DRD2" (example)

**Expected Output:**
```json
[
  {"phase": "LAUNCHED", "drug_count": 45},
  {"phase": "PRECLINICAL", "drug_count": 28},
  {"phase": "PHASE 2", "drug_count": 15},
  {"phase": "PHASE 3", "drug_count": 8},
  {"phase": "WITHDRAWN", "drug_count": 5}
]
```

**Module:** `streamlit_app.py` - `get_target_details()` + Python aggregation  
**Query Reference:** Similar to `Queries.md` - Query #19 (Get Phase Distribution)  
**API Endpoint:** None (Backend queries Neo4j directly)

---

### 2) Mechanisms Targeting Target Chart (Bar Chart)

**UI Element:** "Mechanisms Targeting DRD2" - Vertical bar chart showing mechanism distribution

**Query:**
```cypher
MATCH (t:Target {name: $target_name})<-[r:TARGETS]-(d:Drug)
WHERE r.mechanism IS NOT NULL AND r.mechanism <> ''
RETURN r.mechanism as mechanism, count(d) as drug_count
ORDER BY drug_count DESC
LIMIT $limit
```

**Parameters:**
- `$target_name`: "DRD2"
- `$limit`: 20 (or desired limit)

**Expected Output:**
```json
[
  {"mechanism": "dopamine receptor agonist", "drug_count": 35},
  {"mechanism": "dopamine receptor antagonist", "drug_count": 28},
  {"mechanism": "partial agonist", "drug_count": 12}
]
```

**Module:** `streamlit_app.py` - `get_target_details()` + Python aggregation  
**Query Reference:** Related to mechanism classification queries  
**API Endpoint:** None (Backend queries Neo4j directly)

---

### 3) Detailed Drug Table (Paginated)

**UI Element:** "Detailed Drug Table" with columns: DRUG NAME, MOA, PHASE, TARGET MECHANISM, RELATIONSHIP, CONFIDENCE

**Query:**
```cypher
MATCH (t:Target {name: $target_name})<-[r:TARGETS]-(d:Drug)
RETURN d.name as drug_name,
       d.moa as moa,
       d.phase as phase,
       r.mechanism as target_mechanism,
       r.relationship_type as relationship,
       r.confidence as confidence
ORDER BY d.name
SKIP $skip
LIMIT $limit
```

**Parameters:**
- `$target_name`: "DRD2"
- `$skip`: 0 (for first page)
- `$limit`: 10 (rows per page)

**Expected Output:**
```json
[
  {
    "drug_name": "3-fluorobenzylspiperone",
    "moa": "dopamine receptor agonist",
    "phase": "Launched",
    "target_mechanism": "Agonist",
    "relationship": "Primary/On-Target",
    "confidence": 99.0
  }
]
```

**Module:** `streamlit_app.py` - `get_target_details()` method  
**Query Reference:** See `Queries.md` - Query patterns similar to Query #5A/#14  
**API Endpoint:** None (Backend queries Neo4j directly)

---

## 📋 Design 8: MOA Analysis - Search Mechanisms Tab

**Figma Section:** MOA Analysis Page → Search Mechanisms Tab  
**Current View:** MOA search results with target diversity and drug counts

---

## 🔍 UI Elements to Query Mapping

### 1) Search by Mechanism of Action

**UI Element:** "Search by Mechanism of Action" - Search bar with example buttons

**Query (If MOA nodes exist):**
```cypher
MATCH (m:MOA)
WHERE toLower(m.name) CONTAINS toLower($moa_search)
MATCH (m)<-[:HAS_MOA]-(d:Drug)
RETURN d.name as drug, 
       d.moa as moa, 
       d.phase as phase,
       m.drug_count as moa_drug_count,
       m.target_diversity as moa_target_diversity
ORDER BY m.drug_count DESC, d.name
LIMIT $limit
```

**Query (If MOA nodes don't exist - Alternative):**
```cypher
MATCH (d:Drug)
WHERE toLower(d.moa) CONTAINS toLower($moa_search)
WITH d,
     (MATCH (d)-[:TARGETS]->(t:Target)
      RETURN count(DISTINCT t) as target_diversity) as target_diversity,
     (MATCH (d)-[:TARGETS]->(t:Target)<-[:TARGETS]-(other:Drug)
      WHERE other.moa = d.moa
      RETURN count(DISTINCT other) as drug_count) as drug_count
RETURN d.name as drug,
       d.moa as moa,
       d.phase as phase,
       drug_count as drugs_in_moa,
       target_diversity as target_diversity
ORDER BY drug_count DESC, d.name
LIMIT $limit
```

**Parameters:**
- `$moa_search`: "kinase inhibitor" or "Aurora kinase inhibitor"
- `$limit`: 25

**Expected Output:**
```json
[
  {
    "drug": "AMG900",
    "moa": "Aurora kinase inhibitor",
    "phase": "Launched",
    "drugs_in_moa": 22,
    "target_diversity": 10
  }
]
```

**Note:** The query handles two cases:
1. If `:MOA` nodes exist with pre-computed statistics
2. If `:MOA` nodes don't exist, compute statistics on-the-fly from Drug properties

**Module:** `streamlit_app.py` - `search_drugs_by_moa()` method  
**API Endpoint:** None (Backend queries Neo4j directly)

---

### 2) Search Results Table (Paginated)

**UI Columns:** NAME, MECHANISM, PHASE, DRUGS IN MOA, TARGET DIVERSITY

**Query:** Same as Query #1 above

**Parameters:**
- `$moa_search`: Search term
- `$limit`: 19 (or desired limit for pagination)

**Expected Output:** Same as Query #1

**Note:** Pagination is handled in application layer using `SKIP` and `LIMIT` with calculated offsets.

**Module:** `streamlit_app.py` - `search_drugs_by_moa()` method  
**API Endpoint:** None (Backend queries Neo4j directly)

---

---

## 📋 Design 9: MOA Analysis - Therapeutic Class Tab

**Figma Section:** MOA Analysis Page → Therapeutic Class Tab  
**Current View:** Therapeutic Class overview with table and bar chart

---

## 🔍 UI Elements to Query Mapping

### 1) Therapeutic Class Overview Table

**UI Element:** "Therapeutic Class Overview" table with columns: THERAPEUTIC CLASS, MOA COUNT, DRUG COUNT

**Query (If TherapeuticClass nodes exist):**
```cypher
MATCH (tc:TherapeuticClass)<-[:BELONGS_TO_CLASS]-(m:MOA)<-[:HAS_MOA]-(d:Drug)
RETURN tc.name as class_name,
       count(DISTINCT m) as moa_count,
       count(DISTINCT d) as drug_count
ORDER BY drug_count DESC
```

**Query (If TherapeuticClass nodes don't exist - Alternative):**
```cypher
// Group drugs by a derived therapeutic class from their MOA/indication patterns
MATCH (d:Drug)
WHERE d.moa IS NOT NULL
WITH d,
     CASE 
       WHEN toLower(d.moa) CONTAINS 'inhibitor' THEN 'Inhibitor'
       WHEN toLower(d.moa) CONTAINS 'agonist' THEN 'Agonist'
       WHEN toLower(d.moa) CONTAINS 'antagonist' THEN 'Antagonist'
       WHEN toLower(d.moa) CONTAINS 'blocker' THEN 'Blocker'
       ELSE 'Other'
     END as therapeutic_class
WITH therapeutic_class as class_name,
     collect(DISTINCT d.moa) as unique_moas,
     collect(DISTINCT d.name) as unique_drugs
RETURN class_name,
       size(unique_moas) as moa_count,
       size(unique_drugs) as drug_count
ORDER BY drug_count DESC
```

**Parameters:** None

**Expected Output:**
```json
[
  {
    "class_name": "Receptor Antagonist",
    "moa_count": 979,
    "drug_count": 4427
  },
  {
    "class_name": "Enzyme Inhibitor",
    "moa_count": 652,
    "drug_count": 3215
  }
]
```

**Module:** `streamlit_app.py` - `get_therapeutic_class_analysis()` method  
**API Endpoint:** None (Backend queries Neo4j directly)

---

### 2) Drugs per Therapeutic Class Chart

**UI Element:** "Drugs per Therapeutic Class" bar chart showing drug counts per class

**Query:** Same as Query #1 above (therapeutic class overview)

**Expected Output:** Same as Query #1

**Note:** Chart visualization is handled in application layer using results from the therapeutic class overview query.

**Module:** `streamlit_app.py` - `get_therapeutic_class_analysis()` method  
**API Endpoint:** None (Backend queries Neo4j directly)

---

## 📋 Design 10: MOA Analysis - Top Mechanisms Tab

**Figma Section:** MOA Analysis Page → Top Mechanisms Tab  
**Current View:** Top mechanisms table with MOA, drug counts, and therapeutic class

---

## 🔍 UI Elements to Query Mapping

### 1) Top Mechanisms of Action Table (Paginated)

**UI Element:** "Top Mechanisms of Action" table with columns: MOA, DRUG COUNT, THERAPEUTIC CLASS

**Query (If MOA nodes exist):**
```cypher
MATCH (m:MOA)
OPTIONAL MATCH (m)<-[:HAS_MOA]-(d:Drug)
OPTIONAL MATCH (m)-[:TARGETS_VIA]->(t:Target)
OPTIONAL MATCH (m)-[:BELONGS_TO_CLASS]->(tc:TherapeuticClass)
RETURN m.name as moa, 
       count(DISTINCT d) as drug_count,
       count(DISTINCT t) as target_count,
       collect(DISTINCT tc.name)[0] as therapeutic_class
ORDER BY drug_count DESC
LIMIT $limit
```

**Query (If MOA nodes don't exist - Alternative):**
```cypher
MATCH (d:Drug)
WHERE d.moa IS NOT NULL AND d.moa <> ''
WITH d.moa as moa_name, collect(DISTINCT d.name) as drugs
WITH moa_name, 
     size(drugs) as drug_count,
     (MATCH (d2:Drug {moa: moa_name})-[:TARGETS]->(t:Target)
      RETURN count(DISTINCT t) as target_count) as target_count,
     CASE 
       WHEN toLower(moa_name) CONTAINS 'inhibitor' THEN 'Inhibitor'
       WHEN toLower(moa_name) CONTAINS 'agonist' THEN 'Agonist'
       WHEN toLower(moa_name) CONTAINS 'antagonist' THEN 'Antagonist'
       WHEN toLower(moa_name) CONTAINS 'blocker' THEN 'Blocker'
       ELSE 'Other'
     END as therapeutic_class
RETURN moa_name as moa,
       drug_count,
       target_count,
       therapeutic_class
ORDER BY drug_count DESC
LIMIT $limit
```

**Parameters:**
- `$limit`: 19 (or desired limit for pagination)

**Expected Output:**
```json
[
  {
    "moa": "adrenergic receptor antagonist",
    "drug_count": 104,
    "target_count": 29,
    "therapeutic_class": "Receptor Antagonist"
  }
]
```

**Note:** The query handles two cases:
1. If `:MOA` nodes exist with relationships
2. If `:MOA` nodes don't exist, aggregate from Drug properties

**Module:** `streamlit_app.py` - `get_moa_statistics()` method  
**API Endpoint:** None (Backend queries Neo4j directly)

---

## 📋 Design 11: Mechanism Classification - Individual Classification Display

**Figma Section:** Mechanism Classification Page → Individual Classification Tab  
**Current View:** Classification results for a specific drug-target pair

---

## 🔍 UI Elements to Query Mapping

### 1) Get Existing Drug-Target Classification

**UI Element:** "Drug-Target Mechanism Classification" form showing classification details

**Query:**
```cypher
MATCH (d:Drug {name: $drug_name})-[r:TARGETS]->(t:Target {name: $target_name})
WHERE r.classified = true
RETURN r.relationship_type as relationship_type,
       r.target_class as target_class,
       r.target_subclass as target_subclass,
       r.mechanism as mechanism,
       r.confidence as confidence,
       r.reasoning as reasoning,
       r.classification_source as source,
       r.classification_timestamp as timestamp
```

**Parameters:**
- `$drug_name`: "aspirin" (or any drug name)
- `$target_name`: "PTGS1" (or any target name)

**Expected Output:**
```json
{
  "relationship_type": "Primary/On-Target",
  "target_class": "Protein",
  "target_subclass": "Enzyme",
  "mechanism": "Irreversible Inhibitor",
  "confidence": 0.95,
  "reasoning": "Aspirin's primary mechanism of action involves the irreversible inhibition of cyclooxygenase (COX) enzymes, specifically COX-1 (PTGS1) and COX-2 (PTGS2)...",
  "source": "ai_classifier",
  "timestamp": "2025-09-09T12:00:00Z"
}
```

**Note:** This query retrieves previously classified data. If no classification exists, the application triggers the Gemini API to classify the pair (see `mechanism_classifier.py`).

**Module:** `mechanism_classifier.py` - `get_existing_classification()` method  
**API Endpoint:** None (Backend queries Neo4j directly)

---

### 2) Force Reclassify (Update Classification)

**Action:** "Reclassify" button triggers new classification via Gemini API

**Query (Update existing classification):**
```cypher
MATCH (d:Drug {name: $drug_name})-[r:TARGETS]->(t:Target {name: $target_name})
SET r.relationship_type = $relationship_type,
    r.target_class = $target_class,
    r.target_subclass = $target_subclass,
    r.mechanism = $mechanism,
    r.confidence = $confidence,
    r.reasoning = $reasoning,
    r.classification_source = $source,
    r.classification_timestamp = $timestamp,
    r.classified = true
RETURN r
```

**Parameters:**
- All properties from the Gemini API classification result

**Note:** This is executed automatically after the Gemini API call in `mechanism_classifier.py` - `store_classification_in_neo4j()` method.

**Module:** `mechanism_classifier.py` - `store_classification_in_neo4j()` method  
**API Endpoint:** None (Backend updates Neo4j directly)

---

## 📋 Design 12: Comprehensive Statistics Dashboard

**Figma Section:** Dashboard Page → Comprehensive Statistics  
**Current View:** Overview of drug distribution, top mechanisms, top drugs by target count, and top targets by drug count

---

## 🔍 UI Elements to Query Mapping

### 1) Drug Distribution by Development Phase

**UI Element:** Bar chart showing the number of drugs in each development phase

**Query:**
```cypher
MATCH (d:Drug)
WHERE d.phase IS NOT NULL AND d.phase <> ''
RETURN d.phase as phase, count(d) as drug_count
ORDER BY drug_count DESC
```

**Parameters:** None

**Expected Output:**
```json
[
  {"phase": "LAUNCHED", "drug_count": 3750},
  {"phase": "PRECLINICAL", "drug_count": 2650},
  {"phase": "PHASE 1", "drug_count": 2450}
]
```

**Module:** `streamlit_app.py` - `get_phase_statistics()` method  
**API Endpoint:** None (Backend queries Neo4j directly)

---

### 2) Top 15 Mechanisms of Action

**UI Element:** Horizontal bar chart showing the top 15 mechanisms of action by drug count

**Query (If MOA nodes exist):**
```cypher
MATCH (m:MOA)
RETURN m.name as moa, m.drug_count as drug_count
ORDER BY m.drug_count DESC
LIMIT 15
```

**Query (If MOA nodes don't exist - Alternative):**
```cypher
MATCH (d:Drug)
WHERE d.moa IS NOT NULL AND d.moa <> ''
WITH d.moa as moa_name, count(d) as drug_count
RETURN moa_name as moa, drug_count
ORDER BY drug_count DESC
LIMIT 15
```

**Parameters:** None

**Expected Output:**
```json
[
  {"moa": "HDAC INHIBITOR", "drug_count": 95},
  {"moa": "GLUCOCORTICOID RECEPTOR AGONIST", "drug_count": 88},
  {"moa": "CALCIUM CHANNEL BLOCKER", "drug_count": 82}
]
```

**Module:** `streamlit_app.py` - `get_moa_statistics()` method  
**API Endpoint:** None (Backend queries Neo4j directly)

---

### 3) Top 15 Drugs by Target Count

**UI Element:** Bar chart showing the top 15 drugs based on the number of targets they interact with

**Query:**
```cypher
MATCH (d:Drug)-[:TARGETS]->(t:Target)
RETURN d.name as drug, d.moa as moa, d.phase as phase, count(t) as target_count
ORDER BY target_count DESC
LIMIT 15
```

**Parameters:** None

**Expected Output:**
```json
[
  {"drug": "aspirin", "moa": "cyclooxygenase inhibitor", "phase": "Approved", "target_count": 185},
  {"drug": "imatinib", "moa": "tyrosine kinase inhibitor", "phase": "Approved", "target_count": 172}
]
```

**Module:** `streamlit_app.py` - `get_top_drugs_by_targets(limit=15)` method  
**API Endpoint:** None (Backend queries Neo4j directly)

---

### 4) Top 15 Targets by Drug Count

**UI Element:** Bar chart showing the top 15 targets based on the number of drugs that interact with them

**Query:**
```cypher
MATCH (d:Drug)-[:TARGETS]->(t:Target)
RETURN t.name as target, count(d) as drug_count
ORDER BY drug_count DESC
LIMIT 15
```

**Parameters:** None

**Expected Output:**
```json
[
  {"target": "PTGS2", "drug_count": 72},
  {"target": "PTGS1", "drug_count": 55},
  {"target": "DRD2", "drug_count": 48}
]
```

**Module:** `streamlit_app.py` - `get_top_targets_by_drugs(limit=15)` method  
**API Endpoint:** None (Backend queries Neo4j directly)

---

## 📋 Design 13: Drug Comparison Tab

**Figma Section:** Enhanced Drug Discovery Insights Page → Drug Comparison Tab  
**Current View:** Side-by-side comparison of two drugs (aspirin vs ibuprofen)

---

## 🔍 UI Elements to Query Mapping

### 1) Get Drug Comparison Details

**UI Element:** Comparison table showing drug details and targets side-by-side

**Query Structure:** Multiple queries executed together

**Query 1: Get Drug 1 Details**
```cypher
MATCH (d:Drug {name: $drug1})
RETURN d.name as name, d.moa as moa, d.phase as phase
```

**Query 2: Get Drug 2 Details**
```cypher
MATCH (d:Drug {name: $drug2})
RETURN d.name as name, d.moa as moa, d.phase as phase
```

**Query 3: Get Drug 1 Targets**
```cypher
MATCH (d:Drug {name: $drug1})-[:TARGETS]->(t:Target)
RETURN t.name as target
ORDER BY t.name
```

**Query 4: Get Drug 2 Targets**
```cypher
MATCH (d:Drug {name: $drug2})-[:TARGETS]->(t:Target)
RETURN t.name as target
ORDER BY t.name
```

**Query 5: Get Common Targets**
```cypher
MATCH (d1:Drug {name: $drug1})-[:TARGETS]->(t:Target)<-[:TARGETS]-(d2:Drug {name: $drug2})
RETURN t.name as target
ORDER BY t.name
```

**Parameters:**
- `$drug1`: "aspirin" (or any first drug name)
- `$drug2`: "ibuprofen" (or any second drug name)

**Expected Output:**
```json
{
  "drug1": {
    "name": "aspirin",
    "moa": "cyclooxygenase inhibitor",
    "phase": "Approved"
  },
  "drug2": {
    "name": "ibuprofen",
    "moa": "NSAID",
    "phase": "Approved"
  },
  "drug1_targets": ["AKR1C1", "ASIC3", "EDNRA", "HSPA5", "IKBKB", ...],
  "drug2_targets": ["PTGS1", "PTGS2", ...],
  "common_targets": ["PTGS1", "PTGS2"],
  "drug1_unique": ["AKR1C1", "ASIC3", ...],
  "drug2_unique": [],
  "similarity_score": 10.5
}
```

**Note:** This requires multiple sequential queries or a single complex query. The implementation uses multiple queries for clarity.

**Module:** `streamlit_app.py` - `get_drug_comparison(drug1, drug2)` method  
**API Endpoint:** None (Backend queries Neo4j directly)

---

## 📋 Design 14: Therapeutic Pathways Tab

**Figma Section:** Enhanced Drug Discovery Insights Page → Therapeutic Pathways Tab  
**Current View:** Therapeutic pathway analysis with MOA breakdown and targets table

---

## 🔍 UI Elements to Query Mapping

### 1) Get Therapeutic Pathway Analysis

**UI Element:** Therapeutic pathway analysis summary and targets table with MOA breakdown

**Query:**
```cypher
MATCH (d:Drug {name: $drug_name})-[:TARGETS]->(t:Target)
OPTIONAL MATCH (t)<-[:TARGETS]-(other:Drug)
WHERE other.name <> $drug_name
RETURN d.name as drug, d.moa as moa, d.phase as phase,
       t.name as target, count(other) as other_drugs
ORDER BY other_drugs DESC
```

**Parameters:**
- `$drug_name`: "aspirin" (or any drug name)

**Expected Output:**
```json
[
  {
    "drug": "aspirin",
    "moa": "cyclooxygenase inhibitor",
    "phase": "Approved",
    "target": "PTGS1",
    "other_drugs": 96
  }
]
```

**Note:** This query is processed in Python to group by MOA and create the breakdown structure shown in the UI.

**Post-Processing Logic:**
- Group targets by MOA to create `moa_groups`
- Count unique MOAs to create `unique_moa`
- Count total targets to create `total_targets`

**Module:** `streamlit_app.py` - `get_therapeutic_pathways(drug_name)` method  
**API Endpoint:** None (Backend queries Neo4j directly)

---

## 📋 Design 15: Repurposing Insights Tab

**Figma Section:** Enhanced Drug Discovery Insights Page → Repurposing Insights Tab  
**Current View:** Polypharmacology drugs chart and repurposing opportunities analysis

---

## 🔍 UI Elements to Query Mapping

### 1) Top 10 Polypharmacology Drugs by Target Count

**UI Element:** Bar chart titled "Top 10 Drugs by Target Count" showing drugs with highest repurposing potential

**Query:**
```cypher
MATCH (d:Drug)-[:TARGETS]->(t:Target)
WITH d, count(t) as target_count
WHERE target_count > 3
RETURN d.name as drug, d.moa as moa, d.phase as phase, target_count
ORDER BY target_count DESC
LIMIT 10
```

**Parameters:** None

**Expected Output:**
```json
[
  {
    "drug": "aspirin",
    "moa": "cyclooxygenase inhibitor",
    "phase": "Approved",
    "target_count": 19
  }
]
```

**Module:** `streamlit_app.py` - `get_drug_repurposing_insights()` method  
**API Endpoint:** None (Backend queries Neo4j directly)

---

### 2) Top 10 Druggable Targets by Drug Count

**UI Element:** Analysis of targets most targeted by multiple drugs (not shown in Figma but available in the system)

**Query:**
```cypher
MATCH (d:Drug)-[:TARGETS]->(t:Target)
WITH t, count(d) as drug_count
WHERE drug_count > 2
RETURN t.name as target, drug_count
ORDER BY drug_count DESC
LIMIT 10
```

**Parameters:** None

**Expected Output:**
```json
[
  {
    "target": "PTGS2",
    "drug_count": 45
  }
]
```

**Module:** `streamlit_app.py` - `get_drug_repurposing_insights()` method  
**API Endpoint:** None (Backend queries Neo4j directly)

---

**Status:** ✅ All Designs Complete  
**Total Queries Documented:** 38+ queries across 15 designs  
**Test Suite:** ✅ Available - Run `python test_figma_queries.py`

---

