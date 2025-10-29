# Data Ingestion - Duplicate Record Handling

**Date:** October 16, 2025  
**Question:** What happens when a record already exists in the database?

---

## 🔍 Current Implementation

### **For Nodes (Line 316-320):**

```cypher
UNWIND $nodes AS node
MERGE (n:NodeType {name: node.name})
SET n += node
```

### **For Relationships (Line 353-357):**

```cypher
UNWIND $rels AS rel
MATCH (source:SourceType {name: rel.source_name})
MATCH (target:TargetType {name: rel.target_name})
MERGE (source)-[:RELATIONSHIP_TYPE]->(target)
```

---

## ✅ What Happens with Existing Records

### **1. Existing Nodes - MERGE Behavior:**

**If node EXISTS:**
- ✅ **Node is matched** by its `name` property
- ✅ **Properties are UPDATED** using `SET n += node`
- ✅ **No duplicate created**
- ✅ **No error thrown**

**If node DOES NOT EXIST:**
- ✅ **New node is created**
- ✅ **All properties are set**

**Example:**
```cypher
// Existing node in DB:
(Drug {name: "aspirin", moa: "cyclooxygenase inhibitor", phase: "Approved"})

// Ingesting:
(Drug {name: "aspirin", moa: "COX inhibitor", phase: "Launched", purity: 99.5})

// Result:
(Drug {name: "aspirin", moa: "COX inhibitor", phase: "Launched", purity: 99.5})
// Properties are OVERWRITTEN/ADDED, not merged intelligently
```

---

### **2. Existing Relationships - MERGE Behavior:**

**If relationship EXISTS:**
- ✅ **Relationship is matched**
- ✅ **No duplicate created**
- ✅ **No error thrown**

**If relationship DOES NOT EXIST:**
- ✅ **New relationship is created**

**Example:**
```cypher
// Existing:
(Drug {name: "aspirin"})-[:TARGETS]->(Target {name: "PTGS2"})

// Ingesting same relationship again:
// Result: No change, relationship already exists (no duplicate)
```

---

## ⚠️ Important Notes

### **Property Updates Are Additive:**

The `SET n += node` syntax means:
- **New properties are ADDED** to existing node
- **Existing properties are OVERWRITTEN** with new values
- **Properties not in new data are KEPT** (not deleted)

**Example:**
```cypher
// Existing:
(Drug {name: "aspirin", moa: "old MOA", phase: "Approved", purity: 95})

// Ingesting:
(Drug {name: "aspirin", moa: "new MOA", phase: "Launched"})

// Result:
(Drug {name: "aspirin", moa: "new MOA", phase: "Launched", purity: 95})
// purity is KEPT (not deleted)
// moa and phase are OVERWRITTEN
```

---

## 🎯 Behavior Summary

| Scenario | Action | Result |
|----------|--------|--------|
| **Node exists** | MERGE matches, SET updates | ✅ Properties updated, no duplicate |
| **Node doesn't exist** | MERGE creates new | ✅ New node created |
| **Relationship exists** | MERGE matches | ✅ No duplicate relationship |
| **Relationship doesn't exist** | MERGE creates new | ✅ New relationship created |
| **Partial property match** | SET adds/overwrites | ✅ Additive update (keeps existing, adds new) |

---

## 🔄 Update Strategy

**Current Strategy: "UPSERT" (Update or Insert)**
- **No errors** for existing records
- **No duplicate prevention needed** - MERGE handles it
- **Properties are updated** - may overwrite existing data
- **Safe for re-running** - can re-ingest same file multiple times

---

## ⚠️ Potential Issues

### **1. Property Overwriting:**
```cypher
// If you re-ingest with incomplete data:
Existing: {name: "aspirin", moa: "COX inhibitor", phase: "Approved", purity: 99.5}
New:      {name: "aspirin", moa: "unknown"}
Result:   {name: "aspirin", moa: "unknown", phase: "Approved", purity: 99.5}
// Good: phase and purity kept
// Bad: moa overwritten with "unknown"
```

### **2. No Conflict Resolution:**
- Doesn't check if data is "better" or "newer"
- Simply overwrites with whatever is in the file
- No timestamp comparison
- No "keep existing if newer" logic

---

## 💡 Recommendations

### **For Safe Re-Ingestion:**

1. **Always use preview mode first:**
   ```bash
   python minimal_data_ingestion.py your_file.csv --preview
   ```

2. **Check for existing data:**
   ```cypher
   MATCH (d:Drug {name: "aspirin"})
   RETURN d
   ```

3. **Use complete data files:**
   - Ensure all properties are in the file
   - Avoid partial updates if you want to preserve existing data

### **For Advanced Conflict Resolution (Future Enhancement):**

Consider adding options:
- `--skip-existing` - Skip nodes that already exist
- `--update-only` - Only update existing nodes, don't create new
- `--merge-intelligent` - Compare values and keep "better" one
- `--timestamp-aware` - Only update if new data is newer

---

## 📊 Example Scenarios

### **Scenario 1: Re-ingesting Same Data**
```bash
# First ingestion
python minimal_data_ingestion.py drugs.csv
# Creates: 100 nodes, 200 relationships

# Second ingestion (same file)
python minimal_data_ingestion.py drugs.csv
# Updates: 100 existing nodes (properties may change)
# Skips: 200 existing relationships (no duplicates)
```

### **Scenario 2: Partial Update**
```csv
# File with incomplete data
drug_name,moa
aspirin,cyclooxygenase inhibitor
# Missing: phase, purity, etc.
```

**Result:**
- Existing node updated with new MOA
- Other properties (phase, purity) kept from existing node
- If existing node doesn't exist, only name and MOA are set

### **Scenario 3: Adding New Properties**
```cypher
// Existing: (Drug {name: "aspirin", moa: "COX inhibitor"})
// Ingesting: (Drug {name: "aspirin", moa: "COX inhibitor", purity: 99.5})
// Result: (Drug {name: "aspirin", moa: "COX inhibitor", purity: 99.5})
// ✅ New property added, existing kept
```

---

## ✅ Summary

**What Happens:**
- ✅ **No errors** - Existing records are handled gracefully
- ✅ **No duplicates** - MERGE prevents duplicate nodes/relationships
- ✅ **Properties updated** - Existing nodes get updated with new data
- ✅ **Additive updates** - New properties added, existing properties can be overwritten
- ✅ **Safe to re-run** - Can re-ingest same file multiple times

**Key Behavior:**
- Uses **MERGE** (match or create)
- Uses **SET +=** (additive property update)
- **No duplicate prevention errors**
- **Properties may be overwritten** if file has different values

**Current Limitation:**
- No intelligent conflict resolution
- No "skip existing" option
- No timestamp-based comparisons
- Simply updates with file data

---

**Status:** ✅ Works correctly, but updates existing records (no skip option)


