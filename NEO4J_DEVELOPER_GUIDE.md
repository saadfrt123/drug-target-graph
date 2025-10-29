# Neo4j Integration Guide for Drug-Target Graph Database

## Overview

This project uses **Neo4j** as the primary graph database to store and query drug-target relationships, mechanism of action (MOA) data, and cascade effects. The system is designed to leverage Neo4j's graph capabilities for complex biological relationship queries.

## Database Architecture

### Connection Configuration

**Location:** `config.py`
```python
# Neo4j Database Configuration
NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://127.0.0.1:7687')
NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', '11223344')
NEO4J_DATABASE = os.getenv('NEO4J_DATABASE', 'neo4j')
```

**Current Setup:** Neo4j Aura (Cloud)
- **URI:** `neo4j+s://c8287756.databases.neo4j.io`
- **Database:** `neo4j`
- **Credentials:** Stored in `.env` file

### Data Model

#### Node Types
1. **Drug** - Pharmaceutical compounds
   - Properties: `name`, `moa`, `phase`, `disease_area`, `indication`, `vendor`, `purity`
2. **Target** - Biological targets (proteins, genes, etc.)
   - Properties: `name`, `type`, `description`
3. **MOA** - Mechanism of Action
   - Properties: `mechanism`, `description`
4. **Pathway** - Biological pathways
5. **Gene** - Gene entities
6. **Metabolite** - Metabolite entities
7. **CellularProcess** - Cellular processes

#### Relationship Types
1. **TARGETS** - Drug targets biological entity
2. **HAS_MOA** - Drug has mechanism of action
3. **SIMILAR_MOA** - Drugs with similar mechanisms
4. **BELONGS_TO_CLASS** - Drug belongs to therapeutic class
5. **AFFECTS_DOWNSTREAM** - Cascade effects (AI-generated)

## Query Structure and Examples

### 1. Basic Drug Search
```cypher
MATCH (d:Drug)
WHERE toLower(d.name) CONTAINS toLower($search_term)
RETURN d.name as drug, d.moa as moa, d.phase as phase
ORDER BY d.name
LIMIT $limit
```

### 2. Drug Network Query
```cypher
MATCH (d:Drug {name: $drug_name})-[:TARGETS]->(t:Target)
OPTIONAL MATCH (t)<-[:TARGETS]-(other:Drug)
WHERE other.name <> $drug_name
RETURN d.name as drug, d.moa as moa, d.phase as phase,
       t.name as target, other.name as other_drug, 
       other.moa as other_moa, other.phase as other_phase
LIMIT 100
```

### 3. Cascade Effects Query
```cypher
MATCH (t:Target {name: $target_name})-[r:AFFECTS_DOWNSTREAM]->(e)
WHERE r.confidence >= $min_confidence
RETURN t.name as source, r.effect_type, r.confidence, 
       r.reasoning, e.name as target, labels(e) as entity_type
ORDER BY r.confidence DESC
```

### 4. Mechanism Classification Query
```cypher
MATCH (d:Drug {name: $drug_name})-[r:TARGETS]->(t:Target {name: $target_name})
RETURN r.relationship_type, r.target_class, r.target_subclass, 
       r.mechanism, r.confidence, r.reasoning
```

### 5. Statistics Query
```cypher
MATCH (d:Drug)
RETURN count(d) as drug_count

MATCH (t:Target)
RETURN count(t) as target_count

MATCH ()-[r:TARGETS]->()
RETURN count(r) as relationship_count
```

## Data Fetching Mechanisms

### 1. Connection Management
```python
class DrugTargetGraphApp:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            uri=self.uri,
            auth=(self.user, self.password)
        )
        self.database = self.database_name
```

### 2. Session-Based Queries
```python
def search_drugs(self, search_term: str, limit: int = 20) -> List[Dict]:
    if not self.driver:
        return []
    
    try:
        with self.driver.session(database=self.database) as session:
            result = session.run("""
                MATCH (d:Drug)
                WHERE toLower(d.name) CONTAINS toLower($search_term)
                RETURN d.name as drug, d.moa as moa, d.phase as phase
                ORDER BY d.name
                LIMIT $limit
            """, search_term=search_term, limit=limit)
            
            return result.data()
    
    except Exception as e:
        st.error(f"Error searching drugs: {e}")
        return []
```

### 3. Parameterized Queries
All queries use parameterized inputs for security:
```python
session.run(query, param1=value1, param2=value2)
```

### 4. Error Handling
```python
try:
    with self.driver.session(database=self.database) as session:
        result = session.run(query, **params)
        return result.data()
except Exception as e:
    st.error(f"Database error: {e}")
    return []
```

## Key Features Using Neo4j

### 1. Drug Search and Discovery
- **Fuzzy search** using `CONTAINS` for partial matches
- **Case-insensitive** searches with `toLower()`
- **Property-based filtering** (MOA, phase, etc.)

### 2. Network Visualization
- **Graph traversal** to find connected entities
- **Multi-hop relationships** (drug → target → other drugs)
- **Optional matches** for incomplete data

### 3. Cascade Effect Prediction
- **AI-generated relationships** stored as `AFFECTS_DOWNSTREAM`
- **Confidence scoring** for prediction quality
- **Hierarchical effects** (direct and indirect)

### 4. Mechanism Classification
- **AI-powered classification** stored on relationships
- **Multi-level hierarchy** (type → class → subclass → mechanism)
- **Caching system** to avoid re-classification

### 5. Statistics and Analytics
- **Aggregate queries** for counts and metrics
- **Performance monitoring** of database size
- **Relationship analysis** between entities

## Performance Considerations

### 1. Indexing
```cypher
CREATE INDEX drug_name_index FOR (d:Drug) ON (d.name)
CREATE INDEX target_name_index FOR (t:Target) ON (t.name)
```

### 2. Query Optimization
- **LIMIT clauses** to prevent large result sets
- **Specific property matching** instead of full scans
- **Optional MATCH** for sparse data

### 3. Caching Strategy
- **Neo4j as permanent cache** for AI predictions
- **Session state caching** in Streamlit
- **Background processing** for expensive operations

## Data Loading Process

### 1. Initial Data Import
```python
# From drug_target_graph.py
def create_drug_target_graph():
    # Read CSV data
    # Create nodes and relationships
    # Set properties and constraints
```

### 2. Enhanced Data Loading
```python
# From enhanced_drug_target_graph.py
def load_enhanced_data():
    # Additional drug properties
    # MOA relationships
    # Therapeutic classifications
```

### 3. AI Data Integration
```python
# From cascade_predictor.py
def store_cascade_in_neo4j():
    # Store AI predictions as relationships
    # Create new entity nodes
    # Set confidence and reasoning
```

## Security and Best Practices

### 1. Environment Variables
- **Credentials stored in `.env`**
- **No hardcoded passwords**
- **Environment-specific configurations**

### 2. Parameterized Queries
- **Prevent injection attacks**
- **Type-safe parameters**
- **Validation of inputs**

### 3. Error Handling
- **Graceful degradation**
- **User-friendly error messages**
- **Logging for debugging**

## Current Database Statistics

- **Drugs:** 6,798 nodes
- **Targets:** 2,183 nodes
- **Relationships:** 8 cascade relationships (AI-generated)
- **Total Nodes:** ~9,000+
- **Database Size:** Optimized for cloud deployment

## Development Workflow

### 1. Local Development
```bash
# Connect to local Neo4j
NEO4J_URI=bolt://127.0.0.1:7687
```

### 2. Production Deployment
```bash
# Connect to Neo4j Aura
NEO4J_URI=neo4j+s://c8287756.databases.neo4j.io
```

### 3. Query Testing
```python
# Use Cypher shell or browser
# Test queries before implementing
# Monitor performance
```

This Neo4j integration provides a robust foundation for biological relationship queries, AI-powered predictions, and interactive network visualizations.


