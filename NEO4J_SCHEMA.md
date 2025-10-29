# Neo4j Database Schema Documentation

**Project:** Drug-Target Graph Database Explorer  
**Date:** October 15, 2025  
**Database:** Neo4j (Cloud Aura or Local)  
**Purpose:** Complete schema documentation for developers and database administrators

---

## 📋 Summary

**Total Node Types:** 10  
**Total Relationship Types:** 5 (+ cascade relationships)  
**Total Constraints:** 8  
**Total Indexes:** 5

---

## 🎯 Node Types

### 1. **Drug** (Primary Entity)
**Purpose:** Represents pharmaceutical compounds

**Properties:**
- `name` (string, **unique, required**) - Drug name
- `moa` (string) - Mechanism of Action
- `phase` (string) - Development phase (Preclinical, Phase 1-4, Approved)
- `smiles` (string) - SMILES notation for chemical structure
- `purity` (float) - Chemical purity percentage
- `disease_area` (string) - Disease category
- `indication` (string) - Medical indication
- `vendor` (string) - Commercial supplier

**Constraints:**
```cypher
CREATE CONSTRAINT drug_name IF NOT EXISTS 
FOR (d:Drug) REQUIRE d.name IS UNIQUE
```

**Indexes:**
```cypher
CREATE INDEX drug_moa FOR (d:Drug) ON (d.moa)
CREATE INDEX drug_phase FOR (d:Drug) ON (d.phase)
CREATE INDEX drug_smiles FOR (d:Drug) ON (d.smiles)
```

**Example:**
```cypher
(:Drug {
  name: "aspirin",
  moa: "cyclooxygenase inhibitor",
  phase: "Approved",
  smiles: "CC(=O)OC1=CC=CC=C1C(=O)O"
})
```

---

### 2. **Target** (Primary Entity)
**Purpose:** Represents biological targets (proteins, genes, etc.)

**Properties:**
- `name` (string, **unique, required**) - Target name (e.g., "PTGS2", "COX-2")

**Constraints:**
```cypher
CREATE CONSTRAINT target_name IF NOT EXISTS 
FOR (t:Target) REQUIRE t.name IS UNIQUE
```

**Example:**
```cypher
(:Target {name: "PTGS2"})
```

**Note:** Classification properties are stored on TARGETS relationships, not nodes

---

### 3. **Pathway** (Cascade Entity)
**Purpose:** Represents biological pathways

**Properties:**
- `name` (string, **unique, required**) - Pathway name
- `category` (string, optional) - Pathway category
- `created_date` (datetime) - When node was created

**Constraints:**
```cypher
CREATE CONSTRAINT pathway_name IF NOT EXISTS 
FOR (p:Pathway) REQUIRE p.name IS UNIQUE
```

**Indexes:**
```cypher
CREATE INDEX pathway_category FOR (p:Pathway) ON (p.category)
```

**Example:**
```cypher
(:Pathway {
  name: "Prostaglandin synthesis pathway",
  category: "Metabolism",
  created_date: "2025-10-15T12:00:00Z"
})
```

---

### 4. **Gene** (Cascade Entity)
**Purpose:** Represents genes with expression changes

**Properties:**
- `symbol` (string, **unique, required**) - Gene symbol (e.g., "PTGS1")
- `name` (string, optional) - Gene name
- `created_date` (datetime) - When node was created

**Constraints:**
```cypher
CREATE CONSTRAINT gene_symbol IF NOT EXISTS 
FOR (g:Gene) REQUIRE g.symbol IS UNIQUE
```

**Indexes:**
```cypher
CREATE INDEX gene_name FOR (g:Gene) ON (g.name)
```

**Example:**
```cypher
(:Gene {
  symbol: "PTGS1",
  name: "Prostaglandin-endoperoxide synthase 1",
  created_date: "2025-10-15T12:00:00Z"
})
```

---

### 5. **Metabolite** (Cascade Entity)
**Purpose:** Represents metabolic products

**Properties:**
- `name` (string, **unique, required**) - Metabolite name
- `created_date` (datetime) - When node was created

**Constraints:**
```cypher
CREATE CONSTRAINT metabolite_name IF NOT EXISTS 
FOR (m:Metabolite) REQUIRE m.name IS UNIQUE
```

**Example:**
```cypher
(:Metabolite {
  name: "Prostaglandin E2",
  created_date: "2025-10-15T12:00:00Z"
})
```

---

### 6. **CellularProcess** (Cascade Entity)
**Purpose:** Represents cellular processes

**Properties:**
- `name` (string, **unique, required**) - Process name
- `created_date` (datetime) - When node was created

**Constraints:**
```cypher
CREATE CONSTRAINT process_name IF NOT EXISTS 
FOR (cp:CellularProcess) REQUIRE cp.name IS UNIQUE
```

**Example:**
```cypher
(:CellularProcess {
  name: "Inflammatory response",
  created_date: "2025-10-15T12:00:00Z"
})
```

---

### 7. **Protein** (Cascade Entity)
**Purpose:** Represents proteins affected in cascade

**Properties:**
- `name` (string, **unique, required**) - Protein name
- `created_date` (datetime) - When node was created

**Example:**
```cypher
(:Protein {
  name: "COX-2 enzyme",
  created_date: "2025-10-15T12:00:00Z"
})
```

---

### 8. **DiseaseArea**
**Purpose:** Represents disease categories

**Properties:**
- `name` (string, **unique, required**) - Disease area name

**Constraints:**
```cypher
CREATE CONSTRAINT disease_area_name IF NOT EXISTS 
FOR (da:DiseaseArea) REQUIRE da.name IS UNIQUE
```

**Example:**
```cypher
(:DiseaseArea {name: "Oncology"})
```

---

### 9. **Indication**
**Purpose:** Represents medical indications

**Properties:**
- `name` (string, **unique, required**) - Indication name

**Constraints:**
```cypher
CREATE CONSTRAINT indication_name IF NOT EXISTS 
FOR (i:Indication) REQUIRE i.name IS UNIQUE
```

**Example:**
```cypher
(:Indication {name: "Pain relief"})
```

---

### 10. **Vendor**
**Purpose:** Represents commercial vendors

**Properties:**
- `name` (string, **unique, required**) - Vendor name

**Constraints:**
```cypher
CREATE CONSTRAINT vendor_name IF NOT EXISTS 
FOR (v:Vendor) REQUIRE v.name IS UNIQUE
```

**Example:**
```cypher
(:Vendor {name: "Selleck Chemicals"})
```

---

## 🔗 Relationship Types

### 1. **TARGETS** (Drug → Target)
**Purpose:** Links drugs to their biological targets

**Direction:** `(Drug)-[:TARGETS]->(Target)`

**Properties:**
- `relationship_type` (string) - "Primary/On-Target" or "Secondary/Off-Target"
- `target_class` (string) - "Protein", "Nucleic Acid", "Lipid", "Carbohydrate"
- `target_subclass` (string) - "Enzyme", "Receptor", "Ion Channel", etc.
- `mechanism` (string) - Specific mechanism (e.g., "Irreversible Inhibitor")
- `confidence` (float) - 0.0 to 1.0
- `reasoning` (string) - AI's explanation
- `classification_source` (string) - "Gemini_API"
- `classification_timestamp` (datetime) - When classified
- `classified` (boolean) - Whether classification exists

**Example:**
```cypher
(:Drug {name: "aspirin"})-[:TARGETS {
  relationship_type: "Primary/On-Target",
  target_class: "Protein",
  target_subclass: "Enzyme",
  mechanism: "Irreversible Inhibitor",
  confidence: 0.98,
  reasoning: "Aspirin irreversibly acetylates COX-2",
  classification_source: "Gemini_API",
  classification_timestamp: "2025-10-15T12:00:00Z",
  classified: true
}]->(:Target {name: "PTGS2"})
```

---

### 2. **AFFECTS_DOWNSTREAM** (Target → Cascade Entities)
**Purpose:** Links targets to downstream effects (from cascade prediction)

**Direction:** `(Target)-[:AFFECTS_DOWNSTREAM]->(Pathway|Gene|Metabolite|CellularProcess|Protein)`

**Properties:**
- `effect_type` (string) - "inhibits", "activates", "upregulates", "downregulates", "modulates"
- `confidence` (float) - 0.0 to 1.0
- `reasoning` (string) - AI's explanation
- `depth` (int) - 1, 2, or 3 (hops from target)
- `source_entity` (string) - What entity causes this effect
- `predicted_by` (string) - "Gemini_API"
- `prediction_date` (datetime) - When predicted

**Example:**
```cypher
(:Target {name: "PTGS2"})-[:AFFECTS_DOWNSTREAM {
  effect_type: "downregulates",
  confidence: 0.98,
  reasoning: "COX-2 inhibition reduces PGE2 production",
  depth: 1,
  source_entity: "PTGS2",
  predicted_by: "Gemini_API",
  prediction_date: "2025-10-15T12:00:00Z"
}]->(:Metabolite {name: "Prostaglandin E2"})
```

---

### 3. **TREATS** (Drug → Indication)
**Purpose:** Links drugs to their medical indications

**Direction:** `(Drug)-[:TREATS]->(Indication)`

**Example:**
```cypher
(:Drug {name: "aspirin"})-[:TREATS]->(:Indication {name: "Pain relief"})
```

---

### 4. **BELONGS_TO** (Drug → DiseaseArea)
**Purpose:** Links drugs to disease categories

**Direction:** `(Drug)-[:BELONGS_TO]->(DiseaseArea)`

**Example:**
```cypher
(:Drug {name: "aspirin"})-[:BELONGS_TO]->(:DiseaseArea {name: "Pain Management"})
```

---

### 5. **SUPPLIED_BY** (Drug → Vendor)
**Purpose:** Links drugs to their commercial vendors

**Direction:** `(Drug)-[:SUPPLIED_BY]->(Vendor)`

**Example:**
```cypher
(:Drug {name: "aspirin"})-[:SUPPLIED_BY]->(:Vendor {name: "Selleck Chemicals"})
```

---

## 📊 Complete Schema Diagram

```
┌─────────────┐
│    Drug     │
│─────────────│
│ name*       │
│ moa         │
│ phase       │
│ smiles      │
│ purity      │
└──────┬──────┘
       │
       ├──[TARGETS]──────────>┌─────────────┐
       │                      │   Target    │
       │                      │─────────────│
       │                      │ name*       │
       │                      └──────┬──────┘
       │                             │
       ├──[TREATS]────────────────>┌──────────────┐
       │                           │  Indication  │
       │                           │──────────────│
       │                           │ name*        │
       │                           └──────────────┘
       │
       ├──[BELONGS_TO]───────────>┌──────────────┐
       │                          │DiseaseArea   │
       │                          │──────────────│
       │                          │ name*        │
       │                          └──────────────┘
       │
       └──[SUPPLIED_BY]──────────>┌──────────────┐
                                  │   Vendor     │
                                  │──────────────│
                                  │ name*        │
                                  └──────────────┘

┌─────────────┐
│   Target    │
│  (PTGS2)    │
└──────┬──────┘
       │
       ├──[AFFECTS_DOWNSTREAM]──>┌──────────────┐
       │                         │   Pathway    │
       │                         │──────────────│
       │                         │ name*        │
       │                         │ category     │
       │                         └──────────────┘
       │
       ├──[AFFECTS_DOWNSTREAM]──>┌──────────────┐
       │                         │    Gene      │
       │                         │──────────────│
       │                         │ symbol*      │
       │                         │ name         │
       │                         └──────────────┘
       │
       ├──[AFFECTS_DOWNSTREAM]──>┌──────────────┐
       │                         │  Metabolite  │
       │                         │──────────────│
       │                         │ name*        │
       │                         └──────────────┘
       │
       └──[AFFECTS_DOWNSTREAM]──>┌──────────────┐
                                 │CellularProcess│
                                 │──────────────│
                                 │ name*        │
                                 └──────────────┘
```

---

## 🔍 Data Flow Examples

### **Example 1: Basic Drug-Target Relationship**
```
(Aspirin:Drug)-[TARGETS {mechanism: "Irreversible Inhibitor"}]->(PTGS2:Target)
```

### **Example 2: Cascade Effect Chain**
```
(Aspirin:Drug)-[TARGETS]->(PTGS2:Target)
                                   │
                                   ├─[AFFECTS_DOWNSTREAM {depth: 1}]─>(Prostaglandin E2:Metabolite)
                                   │
                                   └─[AFFECTS_DOWNSTREAM {depth: 2}]─>(Inflammatory response:CellularProcess)
```

### **Example 3: Complete Drug Profile**
```
(Aspirin:Drug)-[TARGETS]->(PTGS2:Target)
           │
           ├─[TREATS]->(Pain relief:Indication)
           ├─[BELONGS_TO]->(Pain Management:DiseaseArea)
           └─[SUPPLIED_BY]->(Selleck Chemicals:Vendor)
```

---

## 📈 Database Statistics

Based on typical dataset (Repurposing Hub):

- **Drugs:** ~12,000+
- **Targets:** ~2,000+
- **TARGETS relationships:** ~25,000+
- **Pathways:** Variable (depends on cascade predictions)
- **Cascade relationships:** Variable (depends on predictions)

---

## 🔧 Common Queries

### **Get all properties for a drug:**
```cypher
MATCH (d:Drug {name: "aspirin"})
RETURN d
```

### **Get all targets for a drug:**
```cypher
MATCH (d:Drug {name: "aspirin"})-[r:TARGETS]->(t:Target)
RETURN t.name, r.mechanism, r.confidence
```

### **Get cascade effects for a target:**
```cypher
MATCH (t:Target {name: "PTGS2"})-[r:AFFECTS_DOWNSTREAM]->(e)
RETURN labels(e)[0] as entity_type, e.name, r.effect_type, r.depth
ORDER BY r.depth
```

### **Get complete drug profile:**
```cypher
MATCH (d:Drug {name: "aspirin"})
OPTIONAL MATCH (d)-[r1:TARGETS]->(t:Target)
OPTIONAL MATCH (d)-[r2:TREATS]->(i:Indication)
OPTIONAL MATCH (d)-[r3:BELONGS_TO]->(da:DiseaseArea)
RETURN d, collect(t) as targets, collect(i) as indications, collect(da) as disease_areas
```

---

## 🎯 Key Design Decisions

1. **Classification data on relationships:** TARGETS relationships store classification properties, not Target nodes
2. **Cascade entities are dynamic:** Pathway, Gene, Metabolite, etc. are created as needed by cascade predictions
3. **Uniqueness constraints:** All node types have unique name constraints
4. **Indexes for common queries:** Drug MOA, phase, and SMILES are indexed
5. **Audit trails:** Timestamps track when predictions and classifications were made

---

## 📝 Notes

- **Cascade schema is optional:** Only created when `create_cascade_schema()` is called
- **Gemini API data:** All AI-generated data is marked with `prediction_source: "Gemini_API"` or `classification_source: "Gemini_API"`
- **Retention:** Cascade predictions are stored permanently (not deleted unless explicitly removed)
- **Performance:** Indexes on commonly queried properties improve query speed

---

**Last Updated:** October 15, 2025  
**Status:** Production-ready schema documentation

