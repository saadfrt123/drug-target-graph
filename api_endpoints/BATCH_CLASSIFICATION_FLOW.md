# Batch Classification - Code Flow Explained

**Date:** October 16, 2025  
**Purpose:** Explain how batch classification works in the code

---

## 🎯 Key Answer to Your Question

**NO, Gemini API is NOT called in a way that all targets are classified in one go.**

The code **loops through each target individually** and calls Gemini API **separately for each one**.

---

## 📊 Code Structure Flow

### **Step 1: User Clicks "Classify All" Button**

**Location:** `streamlit_app.py` line 18816

```python
if st.button("🚀 Classify All Targets", type="primary"):
    with st.spinner(f"Batch classifying targets for {drug_for_batch}..."):
        results = app.classifier.batch_classify_drug_targets(drug_for_batch, limit=10)
```

---

### **Step 2: batch_classify_drug_targets() Method Called**

**Location:** `mechanism_classifier.py` lines 384-427

```python
def batch_classify_drug_targets(self, drug_name: str, limit: int = 5) -> List[Dict]:
    """Classify multiple targets for a single drug"""
    
    # Step 2a: Get unclassified targets from Neo4j
    with self.driver.session(database=self.database) as session:
        result = session.run("""
            MATCH (d:Drug {name: $drug_name})-[r:TARGETS]->(t:Target)
            WHERE r.classified IS NULL OR r.classified = false
            RETURN t.name as target_name
            LIMIT $limit
        """, drug_name=drug_name, limit=limit)
        
        targets = [record['target_name'] for record in result]
    
    # Step 2b: Loop through each target and classify ONE BY ONE
    classifications = []
    for target_name in targets:
        classification = self.classify_and_store(drug_name, target_name)
        if classification:
            classifications.append({
                'drug_name': drug_name,
                'target_name': target_name,
                **classification
            })
        
        # Add delay to respect API rate limits
        time.sleep(1)
    
    return classifications
```

**CRITICAL:** Line 411-412 shows a `for` loop that processes each target **individually**.

---

### **Step 3: classify_and_store() Called for Each Target**

**Location:** `mechanism_classifier.py` lines 336-368

```python
def classify_and_store(self, drug_name: str, target_name: str, 
                      additional_context: str = "", force_reclassify: bool = False):
    """Complete workflow: check existing, classify if needed, store results"""
    
    # Check if classification already exists
    existing = self.get_existing_classification(drug_name, target_name)
    if existing:
        return existing
    
    # Classify using Gemini API (ONE target at a time!)
    classification = self.classify_drug_target_relationship(drug_name, target_name, additional_context)
    
    # Store in Neo4j
    success = self.store_classification_in_neo4j(drug_name, target_name, classification)
    
    return classification
```

---

### **Step 4: classify_drug_target_relationship() Calls Gemini API**

**Location:** `mechanism_classifier.py` lines 167-256

```python
def classify_drug_target_relationship(self, drug_name: str, target_name: str, 
                                    additional_context: str = "") -> Optional[MechanismClassification]:
    """Classify a drug-target relationship using Gemini API"""
    
    # Prepare the prompt
    prompt = self.classification_prompt.format(
        drug_name=drug_name,      # ← Only ONE drug
        target_name=target_name,  # ← Only ONE target
        additional_context=additional_context
    )
    
    # Query Gemini API (ONE call per drug-target pair)
    response = self.gemini_model.generate_content(prompt)
    
    # Parse response
    classification_data = json.loads(response.text)
    
    # Return result
    return MechanismClassification(...)
```

---

## 🔄 Complete Execution Flow

### **Example: Classifying 5 Targets for Aspirin**

```
User clicks "Classify All Targets"
    ↓
batch_classify_drug_targets("aspirin", limit=5)
    ↓
Query Neo4j: Find 5 unclassified targets
Result: ["PTGS2", "NFKBIA", "TGFBR1", "PPARA", "MAPK14"]
    ↓
┌─────────────────────────────────────────────────────┐
│ LOOP: Target #1 = "PTGS2"                          │
│   ↓                                                 │
│ classify_and_store("aspirin", "PTGS2")             │
│   ↓                                                 │
│ classify_drug_target_relationship("aspirin", "PTGS2")│
│   ↓                                                 │
│ Gemini API Call #1 ← FIRST API CALL                │
│   ↓                                                 │
│ Parse JSON response                                 │
│   ↓                                                 │
│ Store in Neo4j                                      │
│   ↓                                                 │
│ time.sleep(1)  ← 1 second delay                    │
└─────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────┐
│ LOOP: Target #2 = "NFKBIA"                         │
│   ↓                                                 │
│ classify_and_store("aspirin", "NFKBIA")            │
│   ↓                                                 │
│ classify_drug_target_relationship("aspirin", "NFKBIA")│
│   ↓                                                 │
│ Gemini API Call #2 ← SECOND API CALL               │
│   ↓                                                 │
│ Parse JSON response                                 │
│   ↓                                                 │
│ Store in Neo4j                                      │
│   ↓                                                 │
│ time.sleep(1)  ← 1 second delay                    │
└─────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────┐
│ LOOP: Target #3 = "TGFBR1"                         │
│   ↓                                                 │
│ Gemini API Call #3 ← THIRD API CALL                │
│   ↓                                                 │
│ time.sleep(1)  ← 1 second delay                    │
└─────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────┐
│ LOOP: Target #4 = "PPARA"                          │
│   ↓                                                 │
│ Gemini API Call #4 ← FOURTH API CALL               │
│   ↓                                                 │
│ time.sleep(1)  ← 1 second delay                    │
└─────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────┐
│ LOOP: Target #5 = "MAPK14"                         │
│   ↓                                                 │
│ Gemini API Call #5 ← FIFTH API CALL                │
│   ↓                                                 │
│ time.sleep(1)  ← 1 second delay                    │
└─────────────────────────────────────────────────────┘
    ↓
Return results list with 5 classifications
```

**Result:** 5 separate Gemini API calls, one per target.

---

## 🔍 Why This Design?

### **Current Implementation (Sequential Calls):**

✅ **Pros:**
- Simple and predictable
- Each call is independent
- Easy error handling (one fails, others continue)
- Can track progress per target
- Works with current Gemini prompt structure

❌ **Cons:**
- Slow (5 targets = 5 × 2 seconds = 10 seconds + delays)
- More expensive (5 API calls instead of 1)
- Hits rate limits faster

---

### **Potential Alternative (Single Multi-Target Call):**

❓ **Could we design it differently?**

**Hypothetically, yes, but it would require:**

1. **New prompt structure:**
```python
prompt = f"""
Classify these drug-target relationships for drug "{drug_name}":

1. Target: PTGS2
2. Target: NFKBIA
3. Target: TGFBR1
4. Target: PPARA
5. Target: MAPK14

Return JSON array of classifications...
"""
```

2. **Modified Gemini response parsing:**
```python
# Expect array instead of single object
[
    {"target_name": "PTGS2", "mechanism": "Inhibitor", ...},
    {"target_name": "NFKBIA", "mechanism": "Modulator", ...},
    ...
]
```

3. **More complex error handling** (what if 1 of 5 fails?)

**Why it's not implemented:**
- Current prompt is designed for single drug-target pair
- Gemini might have trouble classifying 5 at once accurately
- Simpler to maintain sequential approach
- Rate limits are manageable with delays

---

## 📊 Performance Comparison

### **Aspirin Example: 12 Unclassified Targets**

**Current Sequential Approach:**
```
12 targets × 2 seconds per Gemini call = 24 seconds
+ 12 × 1 second delays = 12 seconds
= 36 seconds total
```

**Hypothetical Batch Approach:**
```
1 call with all 12 targets = 8-10 seconds
No delays needed
= 8-10 seconds total
```

**Trade-off:** Speed vs Complexity vs Reliability

---

## 🎯 Summary

**Answer:** NO, the code does NOT call Gemini once for all targets.

**How it actually works:**
1. Loop through each target individually
2. Call Gemini API separately for each one
3. Store each result in Neo4j
4. Add 1-second delay between calls
5. Return all results as a list

**Why:**
- Simpler implementation
- Better error handling
- More predictable behavior
- Works reliably with current Gemini prompt

**Could it be optimized?**
- Yes, but would require redesigning the prompt and response handling
- Current approach is "good enough" and reliable

