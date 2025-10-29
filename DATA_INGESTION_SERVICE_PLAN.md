# Data Ingestion Service Plan

**Project:** Flexible Neo4j Data Ingestion Service  
**Date:** October 15, 2025  
**Purpose:** Build an intelligent data ingestion pipeline that adapts to different input schemas and automatically maps to Neo4j database structure

---

## 📋 Overview

### **Problem Statement:**
- Multiple data sources with different schemas (CSV, JSON, TSV, Excel, etc.)
- Need to automatically map varying column names to Neo4j node types and properties
- Support for relationship detection and creation
- Handle schema evolution over time
- Validate data quality during ingestion

### **Solution:**
An intelligent data ingestion service with:
1. **Schema Detection** - Auto-detect structure of input data
2. **Schema Mapping** - Map input columns to Neo4j properties
3. **Relationship Inference** - Detect and create relationships
4. **Data Validation** - Quality checks and error handling
5. **Batch Processing** - Efficient bulk operations

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Data Ingestion Service                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────┐  │
│  │   Input      │───>│   Schema     │───>│  Mapping │  │
│  │  Detection   │    │  Inference   │    │  Engine  │  │
│  └──────────────┘    └──────────────┘    └──────────┘  │
│         │                    │                 │        │
│         └────────────────────┼─────────────────┘        │
│                              │                          │
│                      ┌───────▼────────┐                 │
│                      │   Validation   │                 │
│                      │    & Cleanup   │                 │
│                      └───────┬────────┘                 │
│                              │                          │
│                      ┌───────▼────────┐                 │
│                      │   Batch        │                 │
│                      │   Processor    │                 │
│                      └───────┬────────┘                 │
│                              │                          │
│                      ┌───────▼────────┐                 │
│                      │    Neo4j       │                 │
│                      │   Database     │                 │
│                      └────────────────┘                 │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 Core Components

### **1. Schema Detection Module**
**Purpose:** Automatically detect structure and type of input data

**Input Types Supported:**
- CSV/TSV files
- JSON files/streams
- Excel files
- Database exports (SQL)
- API responses

**Detection Logic:**
```python
class SchemaDetector:
    def detect_format(self, file_path: str) -> str:
        """Detect file format (CSV, JSON, TSV, etc.)"""
        
    def analyze_columns(self, data: pd.DataFrame) -> Dict:
        """Analyze column names, types, and patterns"""
        # Detect:
        # - Node identifiers (name, id, code)
        # - Property candidates (moa, phase, etc.)
        # - Relationship indicators (targets, treated_by, etc.)
        # - Data types (string, int, float, datetime)
        
    def infer_entity_types(self, columns: List[str]) -> Dict:
        """Infer possible Neo4j node types"""
        # Pattern matching:
        # "drug_*" -> Drug properties
        # "target_*" -> Target properties
        # "cascade_*" -> Cascade entity properties
```

---

### **2. Schema Mapping Engine**
**Purpose:** Map input schema to target Neo4j schema

**Mapping Rules:**
```python
class SchemaMapper:
    def __init__(self):
        self.mapping_rules = {
            # Node type detection
            'Drug': {
                'identifier_patterns': ['drug_name', 'name', 'compound', 'molecule'],
                'property_mappings': {
                    'moa': ['mechanism_of_action', 'moa', 'mode_of_action'],
                    'phase': ['phase', 'development_stage', 'clinical_phase'],
                    'smiles': ['smiles', 'canonical_smiles', 'structure'],
                }
            },
            'Target': {
                'identifier_patterns': ['target', 'protein', 'gene', 'receptor'],
                'property_mappings': {
                    'name': ['target_name', 'name', 'gene_symbol'],
                }
            },
            # ... more mappings
        }
        
    def create_mapping(self, input_columns: List[str], 
                       target_schema: Dict) -> Mapping:
        """Create mapping between input columns and Neo4j schema"""
        
    def apply_mapping(self, data: pd.DataFrame, 
                     mapping: Mapping) -> pd.DataFrame:
        """Transform data according to mapping"""
```

**Mapping Configuration:**
```json
{
  "input_source": "new_drug_dataset.csv",
  "mappings": [
    {
      "source_column": "compound_name",
      "target_node": "Drug",
      "target_property": "name"
    },
    {
      "source_column": "mechanism",
      "target_node": "Drug",
      "target_property": "moa"
    },
    {
      "source_column": "targets",
      "target_node": "Target",
      "target_property": "name",
      "relationship_type": "TARGETS"
    }
  ]
}
```

---

### **3. Relationship Detection Module**
**Purpose:** Detect and create relationships from data

**Detection Patterns:**
```python
class RelationshipDetector:
    def detect_relationships(self, data: pd.DataFrame) -> List[Relationship]:
        """
        Detect relationship patterns:
        - Foreign key patterns (drug_id -> Drug)
        - Multi-value columns ("Target1, Target2" -> multiple TARGETS)
        - Junction tables (drug_id, target_id -> relationship)
        """
        
    def parse_multi_value(self, value: str) -> List[str]:
        """Parse comma-separated values"""
        # "Target1, Target2, Target3" -> ["Target1", "Target2", "Target3"]
        
    def infer_relationship_type(self, source_type: str, 
                               target_type: str) -> str:
        """Infer relationship type from node types"""
        # Drug -> Target: TARGETS
        # Target -> Pathway: AFFECTS_DOWNSTREAM
```

---

### **4. Data Validation Layer**
**Purpose:** Validate data quality before ingestion

**Validation Rules:**
```python
class DataValidator:
    def validate_node_data(self, node_type: str, 
                          properties: Dict) -> ValidationResult:
        """Validate node data against schema"""
        # Check:
        # - Required properties present
        # - Data types correct
        # - Value ranges valid
        # - No nulls in required fields
        
    def validate_relationship(self, rel_type: str,
                             source_id: str, target_id: str) -> bool:
        """Validate relationship data"""
        # Check:
        # - Source and target nodes exist
        # - Relationship type is valid
        # - No duplicate relationships
        
    def sanitize_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """Clean and sanitize data"""
        # - Remove duplicates
        # - Trim whitespace
        # - Normalize text (lowercase, etc.)
        # - Handle missing values
        # - Validate email/URL formats
```

---

### **5. Batch Processor**
**Purpose:** Efficiently load large datasets into Neo4j

**Batching Strategy:**
```python
class BatchProcessor:
    def __init__(self, batch_size=1000, parallelism=4):
        self.batch_size = batch_size
        self.parallelism = parallelism
        
    def ingest_nodes(self, nodes: List[Dict], node_type: str):
        """
        Batch create nodes using UNWIND pattern:
        
        UNWIND $nodes AS node
        CREATE (n:NodeType)
        SET n = node
        """
        
    def ingest_relationships(self, relationships: List[Dict]):
        """
        Batch create relationships:
        
        UNWIND $rels AS rel
        MATCH (a {id: rel.source_id})
        MATCH (b {id: rel.target_id})
        CREATE (a)-[:RELATIONSHIP_TYPE]->(b)
        """
        
    def process_with_transactions(self, data: pd.DataFrame):
        """Process data in transactions for rollback support"""
```

---

## 📋 Implementation Plan

### **Phase 1: Core Framework (Week 1-2)**

**Deliverables:**
1. `schema_detector.py` - Detect file format and analyze structure
2. `schema_mapper.py` - Map input schema to Neo4j schema
3. `relationship_detector.py` - Detect relationships
4. `validator.py` - Data validation
5. `batch_processor.py` - Batch processing

**Key Functions:**
```python
def detect_schema(file_path: str) -> Schema:
    """Auto-detect input schema"""
    
def create_mapping(input_schema: Schema, 
                   target_schema: Schema) -> Mapping:
    """Create mapping between schemas"""
    
def ingest_data(file_path: str, mapping: Mapping) -> Result:
    """Ingest data using mapping"""
```

---

### **Phase 2: Flexible Mapping (Week 3)**

**Deliverables:**
1. Configuration-based mapping (JSON/YAML configs)
2. Heuristic-based auto-mapping
3. Manual mapping override capability
4. Mapping templates for common use cases

**Configuration Example:**
```yaml
# ingestion_config.yaml
data_source:
  file: "new_drugs.csv"
  format: "csv"
  
mappings:
  nodes:
    - type: "Drug"
      identifier_column: "name"
      property_mappings:
        "moa": "mechanism_of_action"
        "phase": "clinical_phase"
        "smiles": "canonical_smiles"
      
    - type: "Target"
      identifier_column: "target_name"
      
  relationships:
    - type: "TARGETS"
      source: "Drug.name"
      target: "Target.target_name"
      delimiter: ","
```

---

### **Phase 3: Advanced Features (Week 4)**

**Deliverables:**
1. **Schema evolution** - Handle schema changes over time
2. **Incremental updates** - Update existing nodes vs create new
3. **Data enrichment** - Merge with existing data
4. **Conflict resolution** - Handle duplicates and conflicts
5. **Audit logging** - Track all changes

**Conflict Resolution:**
```python
class ConflictResolver:
    def resolve_duplicates(self, node: Dict, existing_node: Node):
        """
        Strategies:
        - Skip (ignore new data)
        - Overwrite (replace old data)
        - Merge (combine properties)
        - Timestamp-based (keep latest)
        """
```

---

### **Phase 4: UI & Monitoring (Week 5)**

**Deliverables:**
1. Web interface for file upload and mapping
2. Real-time ingestion progress monitoring
3. Error reporting and handling
4. Preview functionality before ingestion
5. Rollback capability

---

## 🔧 Technical Stack

### **Backend:**
- **Language:** Python 3.9+
- **Framework:** FastAPI (for REST API)
- **Libraries:**
  - `neo4j` - Neo4j driver
  - `pandas` - Data processing
  - `pydantic` - Data validation
  - `pyyaml` - Configuration parsing

### **Frontend:**
- **Framework:** Streamlit (quick prototype) or React (production)
- **Components:** File upload, mapping editor, progress tracker

### **Database:**
- **Neo4j:** Target database
- **PostgreSQL** (optional): Store ingestion logs and mappings

---

## 📊 Data Flow Example

### **Input: Different Schema**
```csv
# compounds_v2.csv (different column names)
chemical_name,mode_of_action,clinical_stage,structure,biological_targets
aspirin,cyclooxygenase inhibitor,Approved,CC(=O)O...,PTGS1|PTGS2
```

### **Processing:**
1. **Detect format:** CSV
2. **Analyze columns:** Map to Drug schema
3. **Detect relationships:** biological_targets -> TARGETS
4. **Validate data:** Check required fields
5. **Transform:** Rename columns, parse multi-value
6. **Batch load:** Insert in batches of 1000

### **Output: Neo4j**
```cypher
(Drug {name: "aspirin", moa: "cyclooxygenase inhibitor", ...})
  -[:TARGETS]-> (Target {name: "PTGS1"})
  -[:TARGETS]-> (Target {name: "PTGS2"})
```

---

## 🎯 Key Features

### **1. Auto-Mapping Intelligence**
```python
# Intelligent column name matching
auto_mappings = {
    'drug_name': 'Drug.name',
    'mechanism_of_action': 'Drug.moa',
    'targets': 'Target.name (via TARGETS)',
    'disease_area': 'DiseaseArea.name (via BELONGS_TO)'
}
```

### **2. Multi-Value Field Handling**
```python
# Input: "Target1, Target2, Target3"
# Output: 3 separate TARGETS relationships
parse_and_create_relationships(source="aspirin", 
                               targets="PTGS1,PTGS2,PTGS3")
```

### **3. Schema Validation**
```python
# Validate against known schema
validator = SchemaValidator(neo4j_schema)
errors = validator.validate(data)
# Returns: Missing fields, type mismatches, etc.
```

### **4. Incremental Updates**
```python
# Update vs Create strategy
ingestion_mode = "update"  # or "create"
if node_exists:
    update_existing_node(node, new_properties)
else:
    create_new_node(node)
```

---

## 🔄 Ingestion Workflow

```
1. Upload File
   ↓
2. Auto-Detect Schema
   ↓
3. Show Preview & Mapping
   ↓
4. User Confirms/Adjusts Mapping
   ↓
5. Validate Data
   ↓
6. Show Validation Report
   ↓
7. Process in Batches
   ↓
8. Show Progress & Errors
   ↓
9. Generate Ingestion Report
   ↓
10. Done!
```

---

## 📝 Configuration Template

### **Simple Schema Mapping Config:**
```json
{
  "version": "1.0",
  "source": {
    "file": "data/new_drugs.csv",
    "format": "csv"
  },
  "nodes": [
    {
      "type": "Drug",
      "id_column": "name",
      "properties": {
        "moa": "mechanism_of_action",
        "phase": "clinical_phase"
      }
    }
  ],
  "relationships": [
    {
      "type": "TARGETS",
      "source_type": "Drug",
      "target_type": "Target",
      "mapping": "targets_column",  // Multi-value column
      "delimiter": "|"
    }
  ]
}
```

---

## 🚨 Error Handling

### **Types of Errors:**
1. **Schema Mismatch** - Columns don't match expected schema
2. **Validation Errors** - Invalid data values
3. **Relationship Errors** - Missing source/target nodes
4. **Constraint Violations** - Unique constraint failures
5. **Network Errors** - Neo4j connection issues

### **Error Handling Strategy:**
```python
try:
    result = batch_processor.ingest_batch(batch)
except ValidationError as e:
    log_error(e)
    continue_with_next_batch()  # Skip invalid records
except ConstraintViolation as e:
    resolve_conflict(e)  # Apply conflict resolution strategy
except DatabaseError as e:
    retry_with_backoff(e)  # Retry with exponential backoff
```

---

## 📈 Performance Optimization

### **1. Batch Processing**
- Process in batches of 1000 records
- Use `UNWIND` for efficient bulk operations
- Parallel processing for multiple batches

### **2. Indexing**
- Ensure indexes exist before ingestion
- Create temporary indexes if needed

### **3. Memory Management**
- Stream large files instead of loading into memory
- Process in chunks

### **4. Transaction Management**
- Batch transactions for atomicity
- Rollback on critical errors

---

## 🔐 Security Considerations

1. **Input Validation** - Sanitize all inputs
2. **SQL Injection** - Use parameterized queries
3. **Rate Limiting** - Prevent database overload
4. **Authentication** - Secure API endpoints
5. **Audit Logging** - Track all data changes

---

## 🧪 Testing Strategy

### **Unit Tests:**
- Schema detection accuracy
- Mapping correctness
- Validation rules
- Relationship detection

### **Integration Tests:**
- End-to-end ingestion flows
- Error handling
- Batch processing
- Rollback scenarios

### **Performance Tests:**
- Large file ingestion (100K+ records)
- Concurrent requests
- Memory usage
- Query performance

---

## 📊 Expected Capabilities

### **Input Formats:**
- ✅ CSV/TSV
- ✅ JSON
- ✅ Excel
- ✅ Parquet
- ✅ API responses

### **Mapping Modes:**
- ✅ Auto-detect (zero config)
- ✅ Config-based (YAML/JSON)
- ✅ Manual override (UI)

### **Data Transformations:**
- ✅ Column renaming
- ✅ Data type conversion
- ✅ Value normalization
- ✅ Multi-value splitting
- ✅ Default value assignment

---

## 🎯 Success Criteria

1. ✅ Handle 90% of use cases with zero configuration
2. ✅ Support schema evolution without code changes
3. ✅ Process 100K records in < 5 minutes
4. ✅ < 1% error rate on valid data
5. ✅ Clear error messages and recovery suggestions

---

## 📚 Documentation Requirements

1. **User Guide** - How to use the service
2. **Configuration Reference** - All options explained
3. **Mapping Templates** - Common use case examples
4. **API Documentation** - REST API specs
5. **Troubleshooting Guide** - Common issues and solutions

---

## 🚀 Implementation Timeline

**Week 1-2:** Core Framework
- Schema detection and mapping
- Basic ingestion pipeline

**Week 3:** Advanced Mapping
- Configuration-based mapping
- Auto-mapping heuristics

**Week 4:** Features & Polish
- Conflict resolution
- Audit logging
- Performance optimization

**Week 5:** UI & Testing
- Web interface
- Comprehensive testing
- Documentation

**Total:** 5 weeks for MVP

---

**Last Updated:** October 15, 2025  
**Status:** Planning phase - Ready for implementation

