# Query Solution: Adding MOA to Top Targets by Drug Count

**Issue:** Current query doesn't return MOA, but dashboard needs it  
**Location:** `streamlit_app.py` - `get_top_targets_by_drugs()` method (line 3023-3052)

---

## 🔍 Current Query (Line 3037-3047)

```cypher
MATCH (d:Drug)-[:TARGETS]->(t:Target)
RETURN t.name as target, count(d) as drug_count
ORDER BY drug_count DESC
LIMIT $limit
```

**Returns:** Only `target` and `drug_count` - **NO MOA**

---

## ✅ Solution Options

### **Option 1: Most Common MOA per Target** (Recommended)

Shows the most frequently occurring MOA for each target:

```cypher
MATCH (d:Drug)-[:TARGETS]->(t:Target)
WHERE d.moa IS NOT NULL
WITH t, d.moa as moa, count(d) as moa_count
ORDER BY moa_count DESC
WITH t, collect({moa: moa, count: moa_count})[0] as top_moa_data
MATCH (d2:Drug)-[:TARGETS]->(t)
WITH t, top_moa_data, count(d2) as drug_count
RETURN t.name as target, 
       drug_count,
       top_moa_data.moa as most_common_moa,
       top_moa_data.count as moa_frequency
ORDER BY drug_count DESC
LIMIT $limit
```

**Output:**
```json
[
  {
    "target": "PTGS2",
    "drug_count": 45,
    "most_common_moa": "cyclooxygenase inhibitor",
    "moa_frequency": 30
  }
]
```

---

### **Option 2: All Unique MOAs as List** (More Details)

Shows all unique MOAs for each target:

```cypher
MATCH (d:Drug)-[:TARGETS]->(t:Target)
WITH t, count(d) as drug_count, collect(DISTINCT d.moa) as moas
WHERE size(moas) > 0
RETURN t.name as target,
       drug_count,
       moas as all_moas,
       moas[0] as primary_moa
ORDER BY drug_count DESC
LIMIT $limit
```

**Output:**
```json
[
  {
    "target": "PTGS2",
    "drug_count": 45,
    "all_moas": ["cyclooxygenase inhibitor", "NSAID", "anti-inflammatory"],
    "primary_moa": "cyclooxygenase inhibitor"
  }
]
```

---

### **Option 3: Simplified - First MOA Found** (Fastest)

Simple approach showing first MOA encountered:

```cypher
MATCH (d:Drug)-[:TARGETS]->(t:Target)
WHERE d.moa IS NOT NULL
WITH t, collect(DISTINCT d.moa) as moas, count(d) as drug_count
RETURN t.name as target,
       drug_count,
       moas[0] as moa,
       size(moas) as unique_moa_count
ORDER BY drug_count DESC
LIMIT $limit
```

**Output:**
```json
[
  {
    "target": "PTGS2",
    "drug_count": 45,
    "moa": "cyclooxygenase inhibitor",
    "unique_moa_count": 3
  }
]
```

---

### **Option 4: Simplified with Fallback** (Best for Dashboard)

Most efficient with fallback for targets with no MOA data:

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

**Output:**
```json
[
  {
    "target": "PTGS2",
    "drug_count": 45,
    "moa": "cyclooxygenase inhibitor",
    "unique_moas": 3
  }
]
```

---

## 🎯 Recommended Implementation

**For Streamlit dashboard, use Option 4** - it's the cleanest and most efficient:

### **Updated Function:**

```python
def get_top_targets_by_drugs(self, limit: int = 10) -> List[Dict]:
    """Get targets with most drugs, including MOA information"""
    
    if not self.driver:
        return []
    
    try:
        with self.driver.session(database=self.database) as session:
            result = session.run("""
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
            """, limit=limit)
            
            return result.data()
            
    except Exception as e:
        st.error(f"Error getting top targets: {e}")
        return []
```

---

## 📊 Display in Streamlit

After updating the function, you can display MOA in the dashboard:

```python
top_targets = app.get_top_targets_by_drugs(5)

if top_targets:
    for target in top_targets:
        with st.container():
            st.markdown(f"**{target['target']}**")
            st.write(f"**Drugs:** {target['drug_count']}")
            st.write(f"**MOA:** {target.get('moa', 'Unknown')}")
            if target.get('unique_moas', 0) > 1:
                st.write(f"*({target['unique_moas']} different MOAs)*")
            st.divider()
```

---

## 🔍 Why This Works

1. **MOA is on Drug nodes**, not Target nodes
2. **Aggregate from drugs** that target each target
3. **Collect distinct MOAs** to see variety
4. **Show first/primary MOA** for quick reference
5. **Handle null values** gracefully

---

## ⚡ Performance

- **Option 4 (Recommended):** ~Same performance as current query
- Uses `collect()` for aggregation (efficient in Neo4j)
- Filters nulls with list comprehension
- Single query execution

---

**Status:** ✅ Ready to implement - Update `streamlit_app.py` line 3037-3047


