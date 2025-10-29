# Dashboard Queries - Line 7589 Section

**Location:** `streamlit_app.py` - Dashboard section  
**Date:** October 16, 2025

---

## 📋 Queries Used in This Section

### **1. Top Drugs by Target Count**
**Function:** `app.get_top_drugs_by_targets(5)`  
**Location:** Line 7593  
**Implementation:** Line 5845-5898

```cypher
MATCH (d:Drug)-[:TARGETS]->(t:Target)
RETURN d.name as drug, d.moa as moa, d.phase as phase, count(t) as target_count
ORDER BY target_count DESC
LIMIT $limit
```

**Parameters:**
- `$limit`: 5

**Returns:**
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

**Display:** Line 7603-7609
- `drug['drug']` - Drug name
- `drug['target_count']` - Number of targets
- `drug['moa']` - Mechanism of Action
- `drug['phase']` - Development phase

---

### **2. Top Targets by Drug Count**
**Function:** `app.get_top_targets_by_drugs(5)`  
**Location:** Line 7627  
**Implementation:** Line 5917-5965

```cypher
MATCH (d:Drug)-[:TARGETS]->(t:Target)
RETURN t.name as target, count(d) as drug_count
ORDER BY drug_count DESC
LIMIT $limit
```

**Parameters:**
- `$limit`: 5

**Returns:**
```json
[
  {
    "target": "PTGS2",
    "drug_count": 45
  },
  {
    "target": "PTGS1",
    "drug_count": 38
  }
]
```

**Display:** Line 7637-7640
- `target['target']` - Target name
- `target['drug_count']` - Number of drugs targeting it

---

### **3. Search Drugs (Quick Search)**
**Function:** `app.search_drugs(search_term, 10)`  
**Location:** Line 7679  
**Implementation:** Line 4027-4095

```cypher
MATCH (d:Drug)
WHERE toLower(d.name) CONTAINS toLower($search_term)
RETURN d.name as drug, d.moa as moa, d.phase as phase
ORDER BY d.name
LIMIT $limit
```

**Parameters:**
- `$search_term`: User input from text field
- `$limit`: 10

**Returns:**
```json
[
  {
    "drug": "aspirin",
    "moa": "cyclooxygenase inhibitor",
    "phase": "Approved"
  },
  {
    "drug": "aspirin derivative",
    "moa": "anti-inflammatory",
    "phase": "Phase 2"
  }
]
```

**Display:** Line 7916
```python
st.write(f"- **{drug['drug']}** (MOA: {drug['moa']}, Phase: {drug['phase']})")
```

---

### **4. Search Targets (Quick Search)**
**Function:** `app.search_targets(search_term, 10)`  
**Location:** Line 7690  
**Implementation:** Line 4103-4170

```cypher
MATCH (t:Target)
WHERE toLower(t.name) CONTAINS toLower($search_term)
RETURN t.name as target
ORDER BY t.name
LIMIT $limit
```

**Parameters:**
- `$search_term`: User input from text field
- `$limit`: 10

**Returns:**
```json
[
  {
    "target": "PTGS2"
  },
  {
    "target": "PTGS1"
  }
]
```

**Display:** Line 7926
```python
st.write(f"- **{target['target']}**")
```

---

## 📊 Summary

| Query | Function | Limit | Purpose |
|-------|----------|-------|---------|
| **Top Drugs** | `get_top_drugs_by_targets()` | 5 | Show drugs with most targets |
| **Top Targets** | `get_top_targets_by_drugs()` | 5 | Show targets targeted by most drugs |
| **Search Drugs** | `search_drugs()` | 10 | Search drugs by name (case-insensitive) |
| **Search Targets** | `search_targets()` | 10 | Search targets by name (case-insensitive) |

---

## 🔍 Query Details

### **Case-Insensitive Search:**
Both search queries use:
- `toLower()` function on both sides
- `CONTAINS` for partial matching
- Example: "asp" matches "Aspirin", "aspirin", "ASPIRIN"

### **Ordering:**
- Top Drugs/Targets: Ordered by count DESC (highest first)
- Search results: Ordered alphabetically by name ASC

### **Performance:**
- All queries use `LIMIT` for efficiency
- Simple pattern matching (no complex joins needed)
- Indexed on `Drug.name` and `Target.name` (from schema)

---

**Status:** ✅ All queries documented


