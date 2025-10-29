# Query Issue: `t.moa` Returns Null - Explanation

**Date:** October 16, 2025  
**Issue:** `t.moa` returning null in "Top Targets by Drug Count" query

---

## 🚨 Problem

The query you're using:
```cypher
MATCH (d:Drug)-[:TARGETS]->(t:Target)
RETURN t.name as target, t.moa as moa, count(d) as drug_count
ORDER BY drug_count DESC
LIMIT ${limitInt}
```

**Problem:** `t.moa` will **always return null** because **Target nodes don't have an `moa` property!**

---

## 📊 Database Schema

### **Target Node Properties:**
According to `NEO4J_SCHEMA.md`:
- ✅ `name` (string, required) - Target name (e.g., "PTGS2")
- ❌ **NO `moa` property** - MOA is a property of **Drug** nodes, not Target nodes

### **Drug Node Properties:**
- ✅ `name` (string, required)
- ✅ `moa` (string) - Mechanism of Action
- ✅ `phase` (string)
- ✅ `smiles` (string)
- ✅ `purity` (float)
- ✅ `disease_area` (string)
- ✅ `indication` (string)
- ✅ `vendor` (string)

---

## ✅ Actual Query Being Used

The **correct query** currently implemented in `streamlit_app.py` (line 3037-3047):

```cypher
MATCH (d:Drug)-[:TARGETS]->(t:Target)
RETURN t.name as target, count(d) as drug_count
ORDER BY drug_count DESC
LIMIT $limit
```

**This query does NOT include `t.moa`** - and that's correct!

---

## 💡 If You Need MOA Information

If you want to show MOA information for targets, you have **two options**:

### **Option 1: Show Most Common MOA for Each Target**
```cypher
MATCH (d:Drug)-[:TARGETS]->(t:Target)
WITH t, collect(DISTINCT d.moa) as moas, count(d) as drug_count
RETURN t.name as target, 
       drug_count,
       moas[0] as most_common_moa,  // First MOA (or you can find the mode)
       moas as all_moas              // All unique MOAs
ORDER BY drug_count DESC
LIMIT $limit
```

### **Option 2: Show All MOAs as a List**
```cypher
MATCH (d:Drug)-[:TARGETS]->(t:Target)
WITH t, collect(DISTINCT d.moa) as unique_moas, count(d) as drug_count
RETURN t.name as target,
       drug_count,
       unique_moas as moas  // List of all unique MOAs targeting this target
ORDER BY drug_count DESC
LIMIT $limit
```

### **Option 3: Get Most Common MOA (Aggregated)**
```cypher
MATCH (d:Drug)-[:TARGETS]->(t:Target)
WHERE d.moa IS NOT NULL
WITH t, d.moa as moa, count(*) as moa_count
ORDER BY moa_count DESC
WITH t, collect({moa: moa, count: moa_count})[0] as top_moa
MATCH (d2:Drug)-[:TARGETS]->(t)
WITH t, top_moa, count(d2) as drug_count
RETURN t.name as target,
       drug_count,
       top_moa.moa as most_common_moa,
       top_moa.count as moa_frequency
ORDER BY drug_count DESC
LIMIT $limit
```

---

## 🎯 Recommended Solution

**For the "Top Targets by Drug Count" query, use:**

```cypher
MATCH (d:Drug)-[:TARGETS]->(t:Target)
RETURN t.name as target, 
       count(d) as drug_count
ORDER BY drug_count DESC
LIMIT $limit
```

**This matches what's actually implemented in `streamlit_app.py`.**

---

## 📝 Summary

1. **Target nodes don't have `moa` property** - only `name`
2. **Drug nodes have `moa` property**
3. **Current query is correct** - it doesn't include `t.moa`
4. **If you need MOA info** - aggregate from drugs targeting that target

---

## 🔍 Verification

You can verify the Target node structure:
```cypher
MATCH (t:Target)
RETURN t LIMIT 1
```

You'll see it only has a `name` property.

---

**Files Checked:**
- `streamlit_app.py` - Line 3037-3047 (actual implementation)
- `Queries.md` - Query #22 (documentation)
- `NEO4J_SCHEMA.md` - Target node schema

**Status:** ✅ Query in code is correct - `t.moa` should not be in the query


