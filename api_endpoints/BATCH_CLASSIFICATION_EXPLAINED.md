# Batch Classification Explained

**Date:** October 16, 2025  
**Purpose:** Explain what batch classification is and why it's needed

---

## 🎯 What is Batch Classification?

**Batch classification** is a process that classifies **multiple drug-target relationships at once** using the AI classifier (Gemini API).

Instead of calling the API 10 times for 10 different targets (slow and expensive), batch classification:
- Fetches all unclassified targets for a drug
- Classifies them in sequence
- Returns all results at once
- Reduces API overhead and improves efficiency

---

## 📊 Example Scenario

### **Real-World Use Case:**

**Aspirin** has **19 targets** in the database:
- PTGS1, PTGS2, NFKBIA, TGFBR1, PPARA, etc.

**Current State:**
- Only 7 targets are classified ✅
- 12 targets need classification ❌

**Without Batch Classification:**
```python
# User has to click "Classify" 12 times manually 😩
# Or backend makes 12 separate API calls

for target in ["PTGS2", "NFKBIA", "TGFBR1", ...]:
    result = requests.post("/classification/classify", json={
        "drug_name": "aspirin",
        "target_name": target
    })
    # Wait 2-3 seconds per call
    # Total: 24-36 seconds + API rate limits
```

**With Batch Classification:**
```python
# Single API call classifies all 12 targets at once! 🚀

result = requests.post("/classification/batch", json={
    "drug_name": "aspirin",
    "targets": ["PTGS2", "NFKBIA", "TGFBR1", "PPARA", ...]  # All 12
})
# Takes ~30 seconds but only 1 API call
# Results stored automatically in Neo4j
```

---

## 🔍 How It Works

### **Step 1: Backend Identifies Unclassified Targets**

Your backend queries Neo4j to find which targets need classification:

```cypher
MATCH (d:Drug {name: $drug_name})-[r:TARGETS]->(t:Target)
WHERE r.classified IS NULL OR r.classified = false
RETURN t.name as target_name
```

**Result:**
```
target_name
-----------
PTGS2
NFKBIA
TGFBR1
PPARA
... (12 targets total)
```

### **Step 2: Backend Calls Batch API**

```python
# POST /classification/batch
{
    "drug_name": "aspirin",
    "targets": ["PTGS2", "NFKBIA", "TGFBR1", "PPARA", ...]
}
```

### **Step 3: API Processes Each Target**

The API internally:
1. Loops through each target
2. Calls Gemini AI for classification
3. Stores result in Neo4j immediately
4. Adds 1-second delay to respect rate limits
5. Collects all results

```python
# Simplified logic inside the API
for target_name in targets:
    classification = classify_single(drug_name, target_name)
    store_in_neo4j(classification)
    time.sleep(1)  # Rate limit protection
```

### **Step 4: Returns Summary**

```json
{
    "success": true,
    "data": {
        "drug_name": "aspirin",
        "total": 12,
        "successful": 11,  // 1 might fail
        "failed": 1,
        "results": [
            {
                "target_name": "PTGS2",
                "status": "success",
                "classification": {
                    "relationship_type": "Primary/On-Target",
                    "mechanism": "Inhibitor",
                    "confidence": 0.92
                }
            },
            // ... 10 more results
        ]
    }
}
```

---

## 💡 Why Batch Classification is Important

### **1. User Experience** ✨

**Without Batch:**
- User sees "Classify" button next to each unclassified target
- Has to click 12 times manually
- Waits 2-3 seconds per click
- Frustrating and time-consuming

**With Batch:**
- One "Classify All Remaining Targets" button
- Single click triggers automatic processing
- Progress shown in real-time
- Much better UX!

**Example from Streamlit App:**
```python
# User sees this button:
if remaining_count > 0 and st.button(f"🚀 Classify All {remaining_count} Remaining Targets"):
    with st.spinner(f"Classifying {remaining_count} remaining targets..."):
        # Batch classification happens here
        results = app.classifier.batch_classify_drug_targets(drug_name, limit=10)
        
    if results:
        st.success(f"✅ Successfully classified {len(results)} additional targets!")
        st.rerun()  # Refresh UI with new data
```

### **2. Efficiency** ⚡

**Time Savings:**
- **Individual calls:** 12 calls × 2 seconds = 24 seconds
- **Batch call:** 12 targets × 2 seconds = 24 seconds (same time, less overhead)
- **API overhead:** Reduced from 12 requests to 1 request

**Rate Limit Management:**
- Gemini API has rate limits (e.g., 60 requests/min)
- Batch endpoint handles delays internally
- Avoids hitting rate limits

### **3. Cost Control** 💰

**API Costs:**
- Each Gemini API call costs money (tokens × price)
- Batch reduces HTTP overhead, retries, and connection setup
- More efficient token usage

### **4. Data Consistency** 📊

**Atomic Operations:**
- All classifications stored together
- Better transaction handling in Neo4j
- Easier to track progress
- Failed classifications don't block others

---

## 🔄 When is Batch Classification Used?

### **Scenario 1: User Requests Drug Details**

```python
# 1. User searches for "aspirin"
drug_info = query_neo4j("MATCH (d:Drug {name: 'aspirin'}) RETURN d")

# 2. Backend fetches all targets
targets = query_neo4j("""
    MATCH (d:Drug {name: 'aspirin'})-[r:TARGETS]->(t:Target)
    RETURN t.name, r.classified
""")

# 3. Backend finds 12 unclassified targets
unclassified = [t for t in targets if not t['classified']]

# 4. Backend automatically triggers batch classification
if len(unclassified) > 0:
    batch_api_response = call_batch_api("aspirin", unclassified[:10])

# 5. Backend queries Neo4j again - now has 10 new classifications!
updated_targets = query_neo4j("""
    MATCH (d:Drug {name: 'aspirin'})-[r:TARGETS]->(t:Target)
    WHERE r.classified = true
    RETURN t.name, r.mechanism, r.confidence
""")
```

### **Scenario 2: Data Ingestion Pipeline**

```python
# Bulk import of new drugs
new_drugs = ["aspirin", "ibuprofen", "morphine", ...]

for drug_name in new_drugs:
    # Import drug and targets from CSV
    import_from_csv(drug_name)
    
    # Find unclassified relationships
    targets = get_unclassified_targets(drug_name)
    
    # Batch classify
    if targets:
        batch_classify(drug_name, targets)
```

### **Scenario 3: Regular Maintenance Job**

```python
# Scheduled job runs nightly
def nightly_classification_update():
    # Find all unclassified relationships
    unclassified = query_neo4j("""
        MATCH (d:Drug)-[r:TARGETS]->(t:Target)
        WHERE r.classified IS NULL
        RETURN d.name as drug, t.name as target
        LIMIT 100
    """)
    
    # Group by drug
    by_drug = group_by_drug(unclassified)
    
    # Batch classify each drug's targets
    for drug_name, targets in by_drug.items():
        batch_classify(drug_name, targets)
```

---

## 🆚 Single vs Batch Classification

### **Single Classification**

**Endpoint:** `POST /classification/classify`  
**Use Case:** Classify one specific drug-target pair

**Request:**
```json
{
    "drug_name": "aspirin",
    "target_name": "PTGS1"
}
```

**When to Use:**
- User manually requests classification for specific target
- Real-time classification needed
- Testing/debugging
- High-priority target

---

### **Batch Classification**

**Endpoint:** `POST /classification/batch`  
**Use Case:** Classify multiple targets for one drug

**Request:**
```json
{
    "drug_name": "aspirin",
    "targets": ["PTGS2", "NFKBIA", "TGFBR1", "PPARA"]
}
```

**When to Use:**
- Bulk import/update of drug data
- User requests "Classify All" button
- Scheduled maintenance jobs
- Initial population of database

---

## 📝 Code Example: Full Workflow

### **Backend Implementation:**

```python
from neo4j import GraphDatabase
import requests

# Neo4j connection
driver = GraphDatabase.driver(uri, auth=(user, password))

def get_drug_with_classification(drug_name: str):
    """Get drug details, auto-classifying missing targets"""
    
    # Step 1: Query Neo4j for drug and targets
    with driver.session() as session:
        result = session.run("""
            MATCH (d:Drug {name: $drug_name})-[r:TARGETS]->(t:Target)
            RETURN t.name as target,
                   r.classified as is_classified,
                   r.mechanism as mechanism,
                   r.relationship_type as type
        """, drug_name=drug_name)
        
        targets = result.data()
    
    # Step 2: Identify unclassified targets
    unclassified = [
        t['target'] for t in targets 
        if not t.get('is_classified', False)
    ]
    
    # Step 3: Call batch API if needed
    if unclassified:
        batch_classify(drug_name, unclassified)
        
        # Step 4: Query again for updated data
        with driver.session() as session:
            result = session.run("""
                MATCH (d:Drug {name: $drug_name})-[r:TARGETS]->(t:Target)
                WHERE r.classified = true
                RETURN t.name as target,
                       r.mechanism as mechanism,
                       r.relationship_type as type
            """, drug_name=drug_name)
            
            targets = result.data()
    
    return targets

def batch_classify(drug_name: str, targets: list):
    """Call batch classification API"""
    
    response = requests.post(
        "http://api:8000/classification/batch",
        json={
            "drug_name": drug_name,
            "targets": targets[:10]  # Limit to 10 per batch
        },
        headers={"X-API-Key": api_key}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Classified {result['data']['successful']} targets")
        return result
    else:
        print(f"❌ Batch classification failed: {response.status_code}")
        return None

# Usage
targets = get_drug_with_classification("aspirin")
for t in targets:
    print(f"{t['target']}: {t['mechanism']}")
```

---

## 🔍 Inside the API: Implementation

### **Batch Classification Method:**

```python
def batch_classify_drug_targets(self, drug_name: str, limit: int = 5):
    """Classify multiple targets for a drug"""
    
    # Step 1: Get unclassified targets from Neo4j
    with self.driver.session() as session:
        result = session.run("""
            MATCH (d:Drug {name: $drug_name})-[r:TARGETS]->(t:Target)
            WHERE r.classified IS NULL OR r.classified = false
            RETURN t.name as target_name
            LIMIT $limit
        """, drug_name=drug_name, limit=limit)
        
        targets = [record['target_name'] for record in result]
    
    if not targets:
        return []
    
    # Step 2: Classify each target sequentially
    classifications = []
    for target_name in targets:
        # Call Gemini API
        classification = self.classify_and_store(drug_name, target_name)
        
        if classification:
            classifications.append({
                'drug_name': drug_name,
                'target_name': target_name,
                **classification
            })
        
        # Respect API rate limits
        time.sleep(1)
    
    return classifications
```

---

## 📊 Benefits Summary

| Benefit | Single Classification | Batch Classification |
|---------|---------------------|---------------------|
| **User Experience** | Good (manual, targeted) | Excellent (bulk, automated) |
| **Efficiency** | 1 target per call | Multiple targets per call |
| **Rate Limits** | User manages | API manages automatically |
| **Cost** | Higher (more overhead) | Lower (less overhead) |
| **Error Handling** | Per-request | Aggregate across batch |
| **Progress Tracking** | Individual | Summary statistics |

---

## 🎯 Real Example from Streamlit

**Location:** `streamlit_app.py` lines 11516-11577

```python
# User sees button: "🚀 Classify All 12 Remaining Targets"
if remaining_count > 0 and st.button(f"🚀 Classify All {remaining_count} Remaining Targets"):
    with st.spinner(f"Classifying {remaining_count} remaining targets..."):
        batch_count = 0
        
        for target in drug_details['targets']:
            # Check if already classified
            existing = app.classifier.get_existing_classification(selected_drug, target)
            
            if not existing or not existing.get('classified', False):
                try:
                    # Classify this target
                    classification = app.get_drug_target_classification(selected_drug, target)
                    
                    if classification:
                        batch_count += 1
                        
                except Exception as e:
                    logger.warning(f"Batch classification failed for {selected_drug} → {target}: {e}")
        
        if batch_count > 0:
            st.success(f"✅ Successfully classified {batch_count} additional targets!")
            st.rerun()  # Refresh UI
```

---

## ✅ Summary

**Batch classification** is essential for:
1. **Better UX** - "Classify All" button instead of clicking 12 times
2. **Efficiency** - Single API call instead of many
3. **Cost Control** - Reduced overhead and better rate limit management
4. **Automation** - Scheduled jobs can bulk-classify unclassified data
5. **Data Consistency** - All classifications stored together atomically

**When to Use:**
- ✅ Bulk operations (importing new drugs)
- ✅ User-initiated "Classify All" actions
- ✅ Scheduled maintenance jobs
- ✅ Initial database population

**When NOT to Use:**
- ❌ Single specific target requested by user
- ❌ Real-time critical classification
- ❌ Testing/debugging

---

**🎉 That's why batch classification exists!**

