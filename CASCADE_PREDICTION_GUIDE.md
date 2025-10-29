# 🌊 Cascade Effect Prediction - User Guide

## Overview

The **Cascade Effect Prediction System** uses AI to predict downstream biological effects when drugs interact with their targets. This powerful feature helps identify:

- 🎯 Off-target effects and side effects
- 🧬 Pathway disruptions
- 📊 Gene expression changes
- 💊 Metabolite alterations
- ⚠️ Potential safety concerns

## Quick Start

### 1. Set Up Environment

Make sure you have a **GEMINI_API_KEY** set:

```bash
# Option 1: Add to .env file
echo "GEMINI_API_KEY=your-api-key-here" >> .env

# Option 2: Set environment variable
export GEMINI_API_KEY=your-api-key-here  # Linux/Mac
set GEMINI_API_KEY=your-api-key-here     # Windows
```

### 2. Initialize Schema (One-Time Setup)

Run the cascade predictor once to create the required database schema:

```bash
python cascade_predictor.py
```

Or use the Streamlit UI:
1. Navigate to **🌊 Cascade Analysis**
2. Go to **⚙️ Settings** tab
3. Click **🔧 Create/Update Cascade Schema**

### 3. Predict Your First Cascade

#### Using the Web Interface:

1. **Open Streamlit App:**
   ```bash
   streamlit run streamlit_app.py
   ```

2. **Navigate to 🌊 Cascade Analysis**

3. **Select Drug & Target:**
   - Choose a drug from the dropdown (e.g., "aspirin")
   - Select one of its targets (e.g., "PTGS2" for COX-2)

4. **Configure Settings:**
   - **Depth:** How many hops (1-3)
     - 1 = Direct effects only
     - 2 = Direct + Secondary effects (recommended)
     - 3 = Deep cascade (slower)
   - **Min Confidence:** Filter predictions (0.6 recommended)
   - **Force Repredict:** Check to override cached predictions

5. **Click 🤖 Predict Cascade Effects**

6. **View Results:**
   - Summary metrics (direct, secondary, tertiary effects)
   - Detailed effects grouped by depth
   - Confidence distribution chart
   - Entity type distribution

#### Using Python:

```python
from cascade_predictor import BiologicalCascadePredictor
import os

# Initialize
predictor = BiologicalCascadePredictor(
    gemini_api_key=os.getenv('GEMINI_API_KEY'),
    neo4j_uri="bolt://127.0.0.1:7687",
    neo4j_user="neo4j",
    neo4j_password="11223344",
    neo4j_database="neo4j"
)

# Create schema (first time only)
predictor.create_cascade_schema()

# Predict cascade
cascade = predictor.predict_and_store(
    drug_name="aspirin",
    target_name="PTGS2",
    depth=2,
    additional_context="Aspirin irreversibly inhibits COX-2"
)

# Print results
if cascade:
    print(f"✅ Prediction complete!")
    print(f"Direct effects: {len(cascade.direct_effects)}")
    print(f"Secondary effects: {len(cascade.secondary_effects)}")
    print(f"Average confidence: {cascade.total_confidence:.2f}")
    
    print("\nDirect Effects:")
    for effect in cascade.direct_effects:
        print(f"  • {effect.entity_name} ({effect.entity_type})")
        print(f"    Effect: {effect.effect_type}")
        print(f"    Confidence: {effect.confidence:.2%}")
        print(f"    Reasoning: {effect.reasoning}")
        print()

# Close connection
predictor.close()
```

## Understanding Results

### Effect Levels

**🟢 Direct Effects (1-hop):**
- Immediate consequences of drug-target interaction
- Highest confidence
- Example: "Aspirin inhibits COX-2" → "Prostaglandin synthesis reduced"

**🟡 Secondary Effects (2-hop):**
- Downstream consequences of direct effects
- Medium confidence
- Example: "Prostaglandin synthesis reduced" → "Inflammation pathway downregulated"

**🟠 Tertiary Effects (3-hop):**
- Further downstream effects
- Lower confidence (more speculative)
- Example: "Inflammation pathway downregulated" → "Gene expression changes"

### Confidence Scores

- **0.9 - 1.0:** Very high confidence (well-established relationships)
- **0.7 - 0.9:** High confidence (strong evidence)
- **0.5 - 0.7:** Medium confidence (moderate evidence)
- **< 0.5:** Low confidence (speculative/uncertain)

### Entity Types

- **Pathway:** Biological pathways (e.g., "Prostaglandin synthesis pathway")
- **Gene:** Genes with expression changes (e.g., "PTGS1")
- **Metabolite:** Metabolic products (e.g., "PGE2")
- **CellularProcess:** Cellular processes (e.g., "Inflammation response")
- **Protein:** Other proteins affected (e.g., "NF-κB")

## Features

### 1. Predict Cascade (Tab 1)

Main prediction interface with:
- Drug and target selection
- Configurable depth and confidence threshold
- Results visualization
- Detailed effect breakdown

### 2. View Existing (Tab 2)

Search and browse previously predicted cascades:
- Search by drug name
- View all targets with predictions
- Quick access to stored cascades

### 3. Statistics (Tab 3)

Analytics dashboard showing:
- Total cascade relationships
- Unique drug-target pairs analyzed
- Average prediction confidence
- Distribution of affected entities

### 4. Settings (Tab 4)

Management and configuration:
- Schema creation/update
- Batch prediction for multiple pairs
- Documentation and help

## Advanced Usage

### Batch Prediction

Predict cascades for multiple drug-target pairs:

```python
# Define pairs
pairs = [
    ("aspirin", "PTGS2"),
    ("morphine", "OPRM1"),
    ("insulin", "INSR")
]

# Batch predict
results = predictor.batch_predict_cascades(
    drug_target_pairs=pairs,
    depth=2,
    delay_seconds=2  # Respect API rate limits
)

print(f"Completed {len(results)}/{len(pairs)} predictions")
```

Or use the UI:
1. Go to **⚙️ Settings** tab
2. Set number of pairs (1-50)
3. Click **🚀 Batch Predict Top Pairs**

### Retrieve Existing Cascade

```python
# Get cached cascade (no API call)
cascade = predictor.get_existing_cascade(
    drug_name="aspirin",
    target_name="PTGS2",
    min_confidence=0.7  # Only high-confidence effects
)

if cascade:
    print("Found existing cascade!")
else:
    print("No cascade found in database")
```

### Force Reprediction

Update outdated predictions:

```python
# Force new prediction even if cached
cascade = predictor.predict_and_store(
    drug_name="aspirin",
    target_name="PTGS2",
    depth=2,
    force_repredict=True  # Ignore cache
)
```

## Data Storage

### Where Data is Stored

All predictions are stored in your **existing Neo4j database**:

- **Nodes Created:**
  - `(:Pathway {name: "..."})`
  - `(:Gene {symbol: "..."})`
  - `(:Metabolite {name: "..."})`
  - `(:CellularProcess {name: "..."})`

- **Relationships Created:**
  - `(:Target)-[:AFFECTS_DOWNSTREAM]->(:Pathway)`
  - Properties: effect_type, confidence, reasoning, depth, etc.

### Querying in Neo4j

```cypher
// Find all downstream effects for a target
MATCH (t:Target {name: "PTGS2"})-[r:AFFECTS_DOWNSTREAM]->(e)
WHERE r.confidence > 0.8
RETURN e, r
ORDER BY r.confidence DESC

// Find drugs affecting same pathway
MATCH (d1:Drug)-[:TARGETS]->(t1)-[:AFFECTS_DOWNSTREAM]->(p:Pathway)
MATCH (d2:Drug)-[:TARGETS]->(t2)-[:AFFECTS_DOWNSTREAM]->(p)
WHERE d1 <> d2
RETURN d1.name, d2.name, p.name

// Multi-hop cascade query
MATCH path = (t:Target {name: "PTGS2"})-[:AFFECTS_DOWNSTREAM*1..3]->(e)
RETURN path, length(path) as depth
ORDER BY depth
```

## Best Practices

### 1. Start with Direct Effects

Begin with depth=1 to understand immediate effects before exploring deeper cascades.

### 2. Use Confidence Filtering

Set min_confidence to 0.7 or higher for initial analysis, then lower if needed.

### 3. Provide Context

Add relevant information in the "Additional Context" field:
- "Irreversible inhibitor"
- "Competitive antagonist"
- "Allosteric modulator"

This improves AI prediction accuracy.

### 4. Validate Predictions

Cross-reference high-confidence predictions with literature or databases like:
- KEGG Pathway
- Reactome
- STRING
- PubMed

### 5. Cache Wisely

- Use cached predictions for consistent results
- Force repredict when:
  - New information is available
  - AI models have been updated
  - You need different depth or context

## Troubleshooting

### "GEMINI_API_KEY not set"

**Solution:**
```bash
# Create .env file
echo "GEMINI_API_KEY=your-actual-api-key" > .env
```

### "No drugs found in database"

**Solution:**
1. Ensure Neo4j database is populated
2. Check connection settings
3. Run `enhanced_drug_target_graph.py` to populate database

### "Cascade predictor module not found"

**Solution:**
```bash
# Verify file exists
ls cascade_predictor.py

# If missing, ensure you're in project directory
cd /path/to/drug-target-graph
```

### Slow Predictions

**Causes:**
- Gemini API rate limits
- Depth=3 predictions (more complex)
- Network latency

**Solutions:**
- Use depth=2 for faster results
- Enable caching (check "Use cached prediction")
- Batch predict during off-hours

### Low Confidence Predictions

**Causes:**
- Uncommon drug-target pairs
- Limited biological knowledge
- Complex downstream effects

**Solutions:**
- Provide more context
- Consult literature for validation
- Use as hypothesis-generating tool

## API Rate Limits

**Gemini API Free Tier:**
- 60 requests per minute
- 1,500 requests per day

**System Safeguards:**
- Automatic delays between batch predictions (1-2 seconds)
- Retry logic for transient failures
- Caching to minimize API calls

## Examples

### Example 1: Aspirin → COX-2

```python
cascade = predictor.predict_and_store(
    drug_name="aspirin",
    target_name="PTGS2",
    depth=2
)

# Expected results:
# Direct: Prostaglandin synthesis ↓, PGE2 ↓
# Secondary: Inflammation ↓, Pain signaling ↓
```

### Example 2: Morphine → Mu Opioid Receptor

```python
cascade = predictor.predict_and_store(
    drug_name="morphine",
    target_name="OPRM1",
    depth=2,
    additional_context="Morphine is a mu-opioid receptor agonist"
)

# Expected results:
# Direct: G-protein signaling ↑, cAMP ↓
# Secondary: Pain pathway ↓, Respiratory depression ↑
```

## FAQ

**Q: How accurate are the predictions?**
A: Predictions are based on Gemini AI's biological knowledge. High-confidence predictions (>0.8) are generally well-established. Always validate critical findings with literature.

**Q: Can I predict cascades for new drugs?**
A: Yes! The AI can predict for any drug-target pair, even if not in the database. Just provide good context.

**Q: How long do predictions take?**
A: 
- Single prediction: 5-15 seconds
- Batch (10 pairs): 2-4 minutes (with delays)

**Q: Are predictions permanent?**
A: Yes, stored in Neo4j. You can repredict anytime with force_repredict=True.

**Q: Can I export predictions?**
A: Yes, query Neo4j or use the Streamlit UI to view and copy results.

**Q: What if the AI makes a mistake?**
A: Cascade prediction is hypothesis-generating. Use confidence scores, validate with literature, and treat predictions as starting points for investigation.

## Support & Feedback

For issues or questions:
1. Check this guide
2. Review progress.md for technical details
3. Examine cascade_predictor.py source code
4. Test with known drug-target pairs
5. Validate predictions with biological databases

## Next Steps

Once comfortable with cascade prediction:
1. ✅ Test with your drug-target pairs
2. ✅ Validate high-confidence predictions
3. ✅ Use for hypothesis generation
4. ✅ Integrate with network visualization
5. ✅ Build custom analysis workflows

---

**Happy Cascade Predicting! 🌊🧬**


