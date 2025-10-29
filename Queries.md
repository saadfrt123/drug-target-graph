# Neo4j Database Queries Documentation

**Project:** Drug-Target Graph Database Explorer  
**Database:** Neo4j Aura (Cloud)  
**Driver:** `neo4j` Python driver  
**Last Updated:** October 15, 2025  

---

## Table of Contents

1. [Connection & Setup Queries](#connection--setup-queries)
2. [Drug Search & Discovery](#drug-search--discovery)
3. [Target Analysis](#target-analysis)
4. [Network Visualization](#network-visualization)
5. [Mechanism Classification](#mechanism-classification)
6. [Cascade Effects](#cascade-effects)
7. [Statistics & Analytics](#statistics--analytics)
8. [MOA & Therapeutic Classes](#moa--therapeutic-classes)
9. [Drug Comparison](#drug-comparison)
10. [Data Management](#data-management)

---

## Connection & Setup Queries

### 1. Test Database Connection
**Module:** `streamlit_app.py` - `test_connection()`  
**Purpose:** Verify database connectivity  

```cypher
RETURN 1
```

**Input:** None  
**Output:** `{'1': 1}`  
**Description:** Simple connectivity test to ensure Neo4j is accessible.

---

### 2. Create Cascade Schema Constraints
**Module:** `cascade_predictor.py` - `create_cascade_schema()`  
**Purpose:** Set up constraints and indexes for cascade entities  

```cypher
CREATE CONSTRAINT pathway_name IF NOT EXISTS 
FOR (p:Pathway) REQUIRE p.name IS UNIQUE

CREATE CONSTRAINT gene_symbol IF NOT EXISTS 
FOR (g:Gene) REQUIRE g.symbol IS UNIQUE

CREATE CONSTRAINT metabolite_name IF NOT EXISTS 
FOR (m:Metabolite) REQUIRE m.name IS UNIQUE

CREATE CONSTRAINT process_name IF NOT EXISTS 
FOR (cp:CellularProcess) REQUIRE cp.name IS UNIQUE
```

**Input:** None  
**Output:** Success/Error message  
**Description:** Creates unique constraints for cascade entity types to prevent duplicates.

---

## Drug Search & Discovery

### 3. Search Drugs by Name
**Module:** `streamlit_app.py` - `search_drugs()`  
**Purpose:** Find drugs matching search term  

```cypher
MATCH (d:Drug)
WHERE toLower(d.name) CONTAINS toLower($search_term)
RETURN d.name as drug, d.moa as moa, d.phase as phase
ORDER BY d.name
LIMIT $limit
```

**Input:** 
- `search_term`: "aspirin"
- `limit`: 20

**Output:**
```json
[
  {
    "drug": "aspirin",
    "moa": "cyclooxygenase inhibitor",
    "phase": "Launched"
  }
]
```

**Description:** Case-insensitive partial matching for drug names.

---

### 4. Get Drug Details
**Module:** `streamlit_app.py` - `get_drug_details()`  
**Purpose:** Retrieve comprehensive drug information  

```cypher
MATCH (d:Drug {name: $drug_name})
RETURN d.name as name, d.moa as moa, d.phase as phase,
       d.disease_area as disease_area, d.indication as indication,
       d.vendor as vendor, d.purity as purity, d.smiles as smiles
```

**Input:** `drug_name`: "aspirin"  
**Output:**
```json
{
  "name": "aspirin",
  "moa": "cyclooxygenase inhibitor", 
  "phase": "Launched",
  "disease_area": "Cardiovascular",
  "indication": "Pain relief",
  "vendor": "Multiple",
  "purity": ">99%",
  "smiles": "CC(=O)OC1=CC=CC=C1C(=O)O"
}
```

**Description:** Retrieves all properties for a specific drug including SMILES notation for chemical structure.

---

### 5. Get Drug Targets (Basic)
**Module:** `streamlit_app.py` - `get_drug_details()`  
**Purpose:** Find all targets for a drug (basic list)  

```cypher
MATCH (d:Drug {name: $drug_name})-[:TARGETS]->(t:Target)
RETURN t.name as target
```

**Input:** `drug_name`: "aspirin"  
**Output:**
```json
[
  {"target": "PTGS1"},
  {"target": "PTGS2"},
  {"target": "NFKBIA"}
]
```

**Description:** Lists all biological targets for a specific drug.

---

### 5A. Get Drug Targets with Classification (For Biological Targets Tab)
**Module:** `streamlit_app.py` - Enhanced version for frontend table  
**Purpose:** Get targets with relationship type, mechanism, target class, and confidence  

```cypher
MATCH (d:Drug {name: $drug_name})-[r:TARGETS]->(t:Target)
RETURN 
    t.name as target,
    r.relationship_type as relationship_type,
    r.mechanism as mechanism,
    r.target_class as target_class,
    r.target_subclass as target_subclass,
    r.confidence as confidence
ORDER BY r.confidence DESC, t.name
```

**Input:** `drug_name`: "aspirin"  
**Output:**
```json
[
  {
    "target": "PTGS1",
    "relationship_type": "Primary/On-Target",
    "mechanism": "Irreversible Inhibitor",
    "target_class": "Protein",
    "target_subclass": "Enzyme",
    "confidence": 0.95
  },
  {
    "target": "AKR1C1",
    "relationship_type": "Secondary/Off-Target",
    "mechanism": "Inhibitor",
    "target_class": "Protein",
    "target_subclass": "Enzyme",
    "confidence": 0.80
  }
]
```

**Description:** Retrieves all biological targets with classification details for the frontend Biological Targets tab. Shows relationship type, mechanism of action, target class, and confidence score for each target-drug interaction.

---

### 5B. Get Drug Target Statistics (For Drug Target Network Tab) ✅ TESTED & WORKING
**Module:** `streamlit_app.py` - Network statistics summary  
**Purpose:** Get summary counts of primary effects, secondary effects, unclassified targets  

**Note:**
While the Streamlit app currently calculates these statistics in Python (requiring multiple database calls), this Neo4j query is the recommended approach for better performance.

**Cypher Query:**
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

**Input:** `drug_name`: "aspirin"  
**Output:**
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

**Description:** Retrieves summary statistics for the Drug Target Network tab showing counts of primary/secondary targets, unclassified targets, and analysis progress.

**Test Results (October 15, 2025):**
- ✅ Query tested successfully with aspirin
- Results: Primary Effects: 2, Secondary Effects: 17, Total Targets: 19
- Performance: Single database call (much faster than N calls in Python implementation)
- Status: Ready for production use

---

### 6. Get Drug Indications
**Module:** `streamlit_app.py` - `get_drug_details()`  
**Purpose:** Find therapeutic indications  

```cypher
MATCH (d:Drug {name: $drug_name})-[:TREATS]->(i:Indication)
RETURN i.name as indication
```

**Input:** `drug_name`: "aspirin"  
**Output:**
```json
[
  {"indication": "Pain relief"},
  {"indication": "Anti-inflammatory"},
  {"indication": "Cardioprotective"}
]
```

**Description:** Retrieves therapeutic uses for a drug.

---

### 7. Get Similar Drugs
**Module:** `streamlit_app.py` - `get_drug_details()`  
**Purpose:** Find drugs targeting same targets  

```cypher
MATCH (d:Drug {name: $drug_name})-[:TARGETS]->(t:Target)<-[:TARGETS]-(other:Drug)
WHERE other.name <> $drug_name
RETURN other.name as similar_drug, other.moa as moa, other.phase as phase
ORDER BY other.name
LIMIT 10
```

**Input:** `drug_name`: "aspirin"  
**Output:**
```json
[
  {
    "similar_drug": "ibuprofen",
    "moa": "cyclooxygenase inhibitor",
    "phase": "Launched"
  }
]
```

**Description:** Finds drugs that share targets with the queried drug.

---

## Target Analysis

### 8. Search Targets by Name
**Module:** `streamlit_app.py` - `search_targets()`  
**Purpose:** Find targets matching search term  

```cypher
MATCH (t:Target)
WHERE toLower(t.name) CONTAINS toLower($search_term)
RETURN t.name as target, t.type as type, t.description as description
ORDER BY t.name
LIMIT $limit
```

**Input:** 
- `search_term`: "PTGS"
- `limit`: 20

**Output:**
```json
[
  {
    "target": "PTGS1",
    "type": "Enzyme",
    "description": "Prostaglandin-endoperoxide synthase 1"
  }
]
```

**Description:** Case-insensitive target search with type and description.

---

### 9. Get Target Details
**Module:** `streamlit_app.py` - `get_target_details()`  
**Purpose:** Comprehensive target information  

```cypher
MATCH (t:Target {name: $target_name})<-[r:TARGETS]-(d:Drug)
RETURN 
    t.name as target,
    t.type as target_type,
    t.description as description,
    count(d) as drug_count,
    collect(DISTINCT d.name)[0..5] as sample_drugs
```

**Input:** `target_name`: "PTGS2"  
**Output:**
```json
{
  "target": "PTGS2",
  "target_type": "Enzyme",
  "description": "Prostaglandin-endoperoxide synthase 2",
  "drug_count": 15,
  "sample_drugs": ["aspirin", "ibuprofen", "celecoxib"]
}
```

**Description:** Target information with drug count and sample drugs.

---

### 10. Find Drugs by Target
**Module:** `streamlit_app.py` - `find_drugs_by_target()`  
**Purpose:** Get all drugs targeting a specific target  

```cypher
MATCH (d:Drug)-[:TARGETS]->(t:Target {name: $target_name})
RETURN d.name as drug, d.moa as moa, d.phase as phase
ORDER BY d.name
```

**Input:** `target_name`: "PTGS2"  
**Output:**
```json
[
  {
    "drug": "aspirin",
    "moa": "cyclooxygenase inhibitor",
    "phase": "Launched"
  },
  {
    "drug": "celecoxib", 
    "moa": "COX-2 inhibitor",
    "phase": "Launched"
  }
]
```

**Description:** Lists all drugs that target a specific biological entity.

---

## Network Visualization

### 11. Get Drug Network
**Module:** `streamlit_app.py` - `get_drug_network()`  
**Purpose:** Build network around a drug for visualization  

```cypher
MATCH (d:Drug {name: $drug_name})-[r:TARGETS]->(t:Target)
OPTIONAL MATCH (t)<-[:TARGETS]-(other:Drug)
WHERE other.name <> $drug_name
RETURN d.name as drug, d.moa as moa, d.phase as phase,
       t.name as target, other.name as other_drug, 
       other.moa as other_moa, other.phase as other_phase,
       r.relationship_type as relationship_type,
       r.mechanism as mechanism,
       r.confidence as confidence
ORDER BY t.name, other.name
```

**Input:** `drug_name`: "aspirin"  
**Output:**
```json
[
  {
    "drug": "aspirin",
    "moa": "cyclooxygenase inhibitor",
    "phase": "Launched",
    "target": "PTGS1",
    "other_drug": "ibuprofen",
    "other_moa": "cyclooxygenase inhibitor",
    "other_phase": "Launched",
    "relationship_type": "Primary/On-Target",
    "mechanism": "Irreversible Inhibitor",
    "confidence": 0.95
  }
]
```

**Description:** Creates network data for interactive visualization with AI classifications.

---

### 12. Get Target Network
**Module:** `streamlit_app.py` - `get_target_network()`  
**Purpose:** Build network around a target  

```cypher
MATCH (t:Target {name: $target_name})<-[:TARGETS]-(d:Drug)
OPTIONAL MATCH (d)-[:TARGETS]->(other_t:Target)
WHERE other_t.name <> $target_name
RETURN t.name as target, d.name as drug, d.moa as moa, d.phase as phase,
       other_t.name as other_target
ORDER BY d.name
```

**Input:** `target_name`: "PTGS2"  
**Output:**
```json
[
  {
    "target": "PTGS2",
    "drug": "aspirin",
    "moa": "cyclooxygenase inhibitor",
    "phase": "Launched",
    "other_target": "PTGS1"
  }
]
```

**Description:** Shows all drugs targeting a specific target and their other targets.

---

## Mechanism Classification

### 13. Store Mechanism Classification
**Module:** `mechanism_classifier.py` - `store_classification_in_neo4j()`  
**Purpose:** Store AI classification results on relationships  

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
RETURN count(r) as updated_count
```

**Input:**
- `drug_name`: "aspirin"
- `target_name`: "PTGS2"
- `relationship_type`: "Primary/On-Target"
- `target_class`: "Protein"
- `target_subclass`: "Enzyme"
- `mechanism`: "Irreversible Inhibitor"
- `confidence`: 0.95
- `reasoning`: "Aspirin irreversibly inhibits COX-2 enzyme"
- `source`: "Gemini_API"
- `timestamp`: "2025-10-15T19:30:00Z"

**Output:** `{"updated_count": 1}`  
**Description:** Permanently stores AI classification results on TARGETS relationships.

---

### 14. Get Existing Classification
**Module:** `mechanism_classifier.py` - `get_existing_classification()`  
**Purpose:** Retrieve stored classification data  

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

**Input:** 
- `drug_name`: "aspirin"
- `target_name`: "PTGS2"

**Output:**
```json
{
  "relationship_type": "Primary/On-Target",
  "target_class": "Protein",
  "target_subclass": "Enzyme", 
  "mechanism": "Irreversible Inhibitor",
  "confidence": 0.95,
  "reasoning": "Aspirin irreversibly inhibits COX-2 enzyme",
  "source": "Gemini_API",
  "timestamp": "2025-10-15T19:30:00Z"
}
```

**Description:** Retrieves cached AI classification to avoid re-processing.

---

### 15. Get Unclassified Targets
**Module:** `mechanism_classifier.py` - `get_unclassified_targets()`  
**Purpose:** Find targets needing classification  

```cypher
MATCH (d:Drug {name: $drug_name})-[r:TARGETS]->(t:Target)
WHERE r.classified IS NULL OR r.classified = false
RETURN t.name as target_name
LIMIT $limit
```

**Input:** 
- `drug_name`: "aspirin"
- `limit`: 10

**Output:**
```json
[
  {"target_name": "NFKBIA"},
  {"target_name": "TP53"}
]
```

**Description:** Identifies targets that haven't been classified by AI yet.

---

## Cascade Effects

### 16. Store Cascade Effects
**Module:** `cascade_predictor.py` - `store_cascade_in_neo4j()`  
**Purpose:** Store AI-predicted cascade effects  

```cypher
MERGE (e:Pathway {name: $entity_name})
ON CREATE SET e.created_date = datetime()

MATCH (t:Target {name: $target_name})
MATCH (e:Pathway {name: $entity_name})
MERGE (t)-[r:AFFECTS_DOWNSTREAM]->(e)
SET r.effect_type = $effect_type,
    r.confidence = $confidence,
    r.reasoning = $reasoning,
    r.depth = $depth,
    r.source_entity = $source_entity,
    r.predicted_by = $predicted_by,
    r.prediction_date = datetime($prediction_date),
    r.drug_context = $drug_name,
    r.validated = false
```

**Input:**
- `target_name`: "PTGS2"
- `entity_name`: "Arachidonic acid metabolism"
- `effect_type`: "Pathway Activation"
- `confidence`: 0.87
- `reasoning`: "COX-2 inhibition affects prostaglandin synthesis"
- `depth`: 1
- `drug_name`: "aspirin"

**Output:** Success/Error  
**Description:** Creates cascade effect nodes and relationships with AI predictions.

---

### 17. Get Existing Cascade Effects
**Module:** `cascade_predictor.py` - `get_existing_cascade()`  
**Purpose:** Retrieve stored cascade predictions  

```cypher
MATCH (t:Target {name: $target_name})-[r:AFFECTS_DOWNSTREAM]->(e)
WHERE r.drug_context = $drug_name AND r.confidence >= $min_confidence
RETURN e, labels(e)[0] as entity_type, r
ORDER BY r.depth, r.confidence DESC
```

**Input:**
- `target_name`: "PTGS2"
- `drug_name`: "aspirin"
- `min_confidence`: 0.7

**Output:**
```json
[
  {
    "e": {"name": "Arachidonic acid metabolism"},
    "entity_type": "Pathway",
    "r": {
      "effect_type": "Pathway Activation",
      "confidence": 0.87,
      "reasoning": "COX-2 inhibition affects prostaglandin synthesis"
    }
  }
]
```

**Description:** Retrieves cached cascade effects to avoid re-prediction.

---

## Statistics & Analytics

### 18. Get Database Statistics
**Module:** `streamlit_app.py` - `get_graph_statistics()`  
**Purpose:** Overall database metrics  

```cypher
MATCH (d:Drug)
RETURN count(d) as count

MATCH (t:Target)
RETURN count(t) as count

MATCH ()-[r:TARGETS]->()
RETURN count(r) as count
```

**Input:** None  
**Output:**
```json
{
  "drug_count": 6798,
  "target_count": 2183,
  "relationship_count": 15420
}
```

**Description:** Provides high-level database statistics. Executes three separate queries to count drugs, targets, and relationships.

---

### 19. Get Phase Distribution
**Module:** `streamlit_app.py` - `get_phase_insights()`  
**Purpose:** Drug development phase analysis  

```cypher
MATCH (d:Drug)
WHERE d.phase IS NOT NULL AND d.phase <> ''
RETURN d.phase as phase, count(d) as count
ORDER BY count DESC
```

**Input:** None  
**Output:**
```json
[
  {"phase": "Launched", "count": 2450},
  {"phase": "Phase 3", "count": 1200},
  {"phase": "Phase 2", "count": 890}
]
```

**Description:** Shows distribution of drugs across development phases.

---

### 20. Get Target Popularity
**Module:** `streamlit_app.py` - `get_target_insights()`  
**Purpose:** Most targeted biological entities  

```cypher
MATCH (d:Drug)-[:TARGETS]->(t:Target)
RETURN t.name as target, count(d) as drug_count
ORDER BY drug_count DESC
LIMIT 20
```

**Input:** None  
**Output:**
```json
[
  {"target": "PTGS2", "drug_count": 45},
  {"target": "PTGS1", "drug_count": 38},
  {"target": "NFKBIA", "drug_count": 25}
]
```

**Description:** Identifies the most druggable targets.

---

### 21. Get Polypharmacology Analysis
**Module:** `streamlit_app.py` - `get_polypharmacology_insights()`  
**Purpose:** Drugs with multiple targets  

```cypher
MATCH (d:Drug)-[:TARGETS]->(t:Target)
WITH d, count(t) as target_count
WHERE target_count > 5
RETURN d.name as drug, d.moa as moa, target_count
ORDER BY target_count DESC
LIMIT 20
```

**Input:** None  
**Output:**
```json
[
  {
    "drug": "aspirin",
    "moa": "cyclooxygenase inhibitor",
    "target_count": 19
  }
]
```

**Description:** Identifies drugs with high polypharmacology (many targets).

---

### 22. Get Top Targets by Drug Count
**Module:** `streamlit_app.py` - `get_top_targets_by_drugs()`  
**Purpose:** Most druggable targets with MOA information  

```cypher
MATCH (d:Drug)-[:TARGETS]->(t:Target)
WITH t, count(d) as drug_count, collect(DISTINCT d.moa) as moas
WITH t, drug_count, moas, 
     CASE WHEN size([m IN moas WHERE m IS NOT NULL]) > 0 
          THEN [m IN moas WHERE m IS NOT NULL][0]
          ELSE "Unknown"
     END as moa
RETURN t.name as target,
       drug_count,
       moa,
       size([m IN moas WHERE m IS NOT NULL]) as unique_moas
ORDER BY drug_count DESC
LIMIT $limit
```

**Input:** `limit`: 20  
**Output:**
```json
[
  {
    "target": "PTGS2",
    "drug_count": 45,
    "moa": "cyclooxygenase inhibitor",
    "unique_moas": 3
  },
  {
    "target": "PTGS1", 
    "drug_count": 38,
    "moa": "cyclooxygenase inhibitor",
    "unique_moas": 2
  },
  {
    "target": "NFKBIA",
    "drug_count": 25,
    "moa": "IKB kinase inhibitor",
    "unique_moas": 1
  }
]
```

**Description:** Identifies the most druggable targets (targets with the most drugs) and includes the most common MOA for each target. MOA is aggregated from all drugs targeting that target.

---

## MOA & Therapeutic Classes

### 23. Get MOA Statistics
**Module:** `streamlit_app.py` - `get_moa_insights()`  
**Purpose:** Mechanism of action analysis  

```cypher
MATCH (m:MOA)
OPTIONAL MATCH (m)<-[:HAS_MOA]-(d:Drug)
RETURN m.name as moa, count(d) as drug_count
ORDER BY drug_count DESC
LIMIT 20
```

**Input:** None  
**Output:**
```json
[
  {"moa": "cyclooxygenase inhibitor", "drug_count": 45},
  {"moa": "receptor antagonist", "drug_count": 38}
]
```

**Description:** Shows most common mechanisms of action.

---

### 24. Get Therapeutic Class Analysis
**Module:** `streamlit_app.py` - `get_therapeutic_class_insights()`  
**Purpose:** Therapeutic class distribution  

```cypher
MATCH (tc:TherapeuticClass)<-[:BELONGS_TO_CLASS]-(m:MOA)<-[:HAS_MOA]-(d:Drug)
RETURN tc.name as class_name,
       count(DISTINCT d) as drug_count,
       count(DISTINCT m) as moa_count
ORDER BY drug_count DESC
```

**Input:** None  
**Output:**
```json
[
  {
    "class_name": "Enzyme Inhibitors",
    "drug_count": 1200,
    "moa_count": 45
  }
]
```

**Description:** Analyzes therapeutic class distribution.

---

## Drug Comparison

### 25. Find Common Targets
**Module:** `streamlit_app.py` - `find_common_targets()`  
**Purpose:** Compare two drugs for shared targets  

```cypher
MATCH (d1:Drug {name: $drug1})-[:TARGETS]->(t:Target)<-[:TARGETS]-(d2:Drug {name: $drug2})
RETURN t.name as target
```

**Input:** 
- `drug1`: "aspirin"
- `drug2`: "ibuprofen"

**Output:**
```json
[
  {"target": "PTGS1"},
  {"target": "PTGS2"}
]
```

**Description:** Finds targets shared between two drugs.

---

### 26. Get Drug Comparison Details
**Module:** `streamlit_app.py` - `compare_drugs()`  
**Purpose:** Comprehensive drug comparison  

```cypher
MATCH (d1:Drug {name: $drug1})
RETURN d1.name as name, d1.moa as moa, d1.phase as phase

MATCH (d2:Drug {name: $drug2})
RETURN d2.name as name, d2.moa as moa, d2.phase as phase

MATCH (d1:Drug {name: $drug1})-[:TARGETS]->(t:Target)
RETURN t.name as target

MATCH (d2:Drug {name: $drug2})-[:TARGETS]->(t:Target)
RETURN t.name as target

MATCH (d1:Drug {name: $drug1})-[:TARGETS]->(t:Target)<-[:TARGETS]-(d2:Drug {name: $drug2})
RETURN t.name as target
```

**Input:** 
- `drug1`: "aspirin"
- `drug2`: "ibuprofen"

**Output:**
```json
{
  "drug1": {
    "name": "aspirin",
    "moa": "cyclooxygenase inhibitor",
    "phase": "Launched",
    "targets": ["PTGS1", "PTGS2", "NFKBIA"]
  },
  "drug2": {
    "name": "ibuprofen", 
    "moa": "cyclooxygenase inhibitor",
    "phase": "Launched",
    "targets": ["PTGS1", "PTGS2"]
  },
  "common_targets": ["PTGS1", "PTGS2"]
}
```

**Description:** Comprehensive comparison of two drugs including shared targets.

---

## Data Management

### 27. Get Cascade Statistics
**Module:** `cascade_predictor.py` - `get_cascade_statistics()`  
**Purpose:** Cascade effect database metrics  

```cypher
MATCH ()-[r:AFFECTS_DOWNSTREAM]->()
RETURN count(r) as count

MATCH ()-[:AFFECTS_DOWNSTREAM]->(e)
RETURN labels(e)[0] as entity_type, count(e) as count
ORDER BY count DESC

MATCH ()-[r:AFFECTS_DOWNSTREAM]->()
RETURN avg(r.confidence) as avg_confidence
```

**Input:** None  
**Output:**
```json
{
  "total_cascade_relationships": 150,
  "entity_counts_by_type": [
    {"entity_type": "Pathway", "count": 75},
    {"entity_type": "Gene", "count": 45}
  ],
  "average_confidence": 0.82
}
```

**Description:** Statistics for AI-generated cascade effects.

---

### 28. Get Top Drugs by Target Count
**Module:** `streamlit_app.py` - `get_top_drugs_by_targets()`  
**Purpose:** Most polypharmacological drugs  

```cypher
MATCH (d:Drug)-[:TARGETS]->(t:Target)
RETURN d.name as drug, d.moa as moa, d.phase as phase, count(t) as target_count
ORDER BY target_count DESC
LIMIT $limit
```

**Input:** `limit`: 20  
**Output:**
```json
[
  {
    "drug": "aspirin",
    "moa": "cyclooxygenase inhibitor",
    "phase": "Launched",
    "target_count": 19
  }
]
```

**Description:** Identifies drugs with the most biological targets.

---

## Implementation Notes

### Connection Pattern
All queries follow this pattern:
```python
with self.driver.session(database=self.database) as session:
    result = session.run(query, **parameters)
    return result.data()
```

### Error Handling
```python
try:
    # Query execution
except Exception as e:
    st.error(f"Database error: {e}")
    return []
```

### Parameterization
All queries use parameterized inputs for security:
```python
session.run(query, param1=value1, param2=value2)
```

### Performance Considerations
- Use `LIMIT` clauses for large result sets
- Create indexes on frequently queried properties
- Use `OPTIONAL MATCH` for incomplete data
- Consider query complexity for real-time applications

---

**Total Queries Documented:** 30 (28 main + 2 enhanced variants)  
**Modules Covered:** 4 (streamlit_app.py, mechanism_classifier.py, cascade_predictor.py, query_interface.py)  
**Use Cases:** Drug discovery, target analysis, network visualization, AI classification, cascade prediction, analytics, frontend table rendering, network statistics summary

