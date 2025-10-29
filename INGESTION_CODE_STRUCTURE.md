# Data Ingestion Service - Code Structure Explanation

**File:** `minimal_data_ingestion.py`  
**Lines:** 453  
**Purpose:** Schema-agnostic data ingestion into Neo4j

---

## 📋 Overall Architecture

```
┌─────────────────────────────────────────────────────────┐
│              MinimalDataIngestion Class                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Initialization (__init__)                              │
│  ├── Neo4j Connection                                   │
│  ├── Mapping Patterns (node detection)                  │
│  └── Relationship Patterns                              │
│                                                          │
│  Data Loading Layer                                     │
│  ├── detect_file_format()                               │
│  └── load_data()                                        │
│                                                          │
│  Schema Detection Layer                                 │
│  ├── auto_detect_mapping()                              │
│  └── parse_multi_value()                                │
│                                                          │
│  Validation Layer                                       │
│  └── validate_mapping()                                 │
│                                                          │
│  Ingestion Layer                                        │
│  ├── ingest_data() [MAIN ORCHESTRATOR]                  │
│  ├── _create_nodes()                                    │
│  └── _create_relationships()                            │
│                                                          │
│  Template System                                        │
│  ├── save_mapping_template()                            │
│  └── load_mapping_template()                            │
│                                                          │
└─────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│              CLI Interface (main())                      │
│  ├── Argument Parsing                                   │
│  ├── Preview Mode                                       │
│  └── Ingestion Mode                                     │
└─────────────────────────────────────────────────────────┘
```

---

## 🏗️ Component Breakdown

### **1. Class Initialization (Lines 28-79)**

```python
def __init__(self):
    # Neo4j Connection
    self.driver = GraphDatabase.driver(...)
    self.database = NEO4J_DATABASE
    
    # Mapping Patterns Dictionary
    self.mapping_patterns = {
        'Drug': {
            'identifiers': [...],      # Column patterns that identify Drug nodes
            'properties': {...}        # Property name → column pattern mappings
        },
        'Target': {...},
        ...
    }
    
    # Relationship Patterns Dictionary
    self.relationship_patterns = {
        'TARGETS': ['targets', 'target', ...],  # Column patterns
        'TREATS': [...],
        ...
    }
```

**Purpose:**
- Establishes Neo4j connection
- Defines patterns for auto-detection
- Stores configuration in class attributes

**Key Design:**
- **Pattern-based matching** - Uses keyword lists instead of exact matches
- **Extensible** - Easy to add new node types or patterns
- **Separation of concerns** - Patterns separate from logic

---

### **2. File Format Detection (Lines 81-93)**

```python
def detect_file_format(self, file_path: str) -> str:
    suffix = Path(file_path).suffix.lower()
    
    if suffix in ['.csv', '.tsv']:
        return 'csv'
    elif suffix == '.json':
        return 'json'
    elif suffix in ['.xlsx', '.xls']:
        return 'excel'
    else:
        return 'unknown'
```

**Purpose:** Identify file type from extension

**Flow:**
1. Extract file extension
2. Map to format type
3. Return format string

**Returns:** `'csv'`, `'json'`, `'excel'`, or `'unknown'`

---

### **3. Data Loading (Lines 95-136)**

```python
def load_data(self, file_path: str) -> pd.DataFrame:
    format_type = self.detect_file_format(file_path)
    
    if format_type == 'csv':
        # Try different separators: ',', '\t', ';', '|'
        for sep in [...]:
            try:
                df = pd.read_csv(file_path, sep=sep)
                if len(df.columns) > 1:  # Success check
                    return df
            except:
                continue
                
    elif format_type == 'json':
        data = json.load(f)
        if isinstance(data, list):
            df = pd.DataFrame(data)  # Array of objects
        elif isinstance(data, dict):
            df = pd.DataFrame([data])  # Single object → array
        
    elif format_type == 'excel':
        df = pd.read_excel(file_path)
```

**Purpose:** Load file into pandas DataFrame

**Key Features:**
- **Auto-separator detection** for CSV (tries 4 separators)
- **JSON flexibility** - handles arrays and single objects
- **Error handling** - tries multiple approaches before failing
- **Returns:** Standardized pandas DataFrame for all formats

**Data Flow:**
```
File (various formats)
    ↓
detect_file_format() → 'csv'
    ↓
Try separators → Success with ','
    ↓
pd.read_csv() → DataFrame
    ↓
Return DataFrame
```

---

### **4. Auto-Mapping Detection (Lines 138-208)**

```python
def auto_detect_mapping(self, df: pd.DataFrame) -> Dict[str, Any]:
    columns = [col.lower().strip() for col in df.columns]
    mapping = {'nodes': {}, 'relationships': []}
    
    # Step 1: Detect Node Types
    for node_type, patterns in self.mapping_patterns.items():
        # Find identifier column
        for pattern in patterns['identifiers']:
            for col in columns:
                if pattern in col or col in pattern:
                    identifier_col = col  # Found!
                    break
        
        # Find property mappings
        for prop_name, prop_patterns in patterns['properties'].items():
            for pattern in prop_patterns:
                for col in columns:
                    if pattern in col or col in pattern:
                        properties[prop_name] = col  # Mapped!
                        break
    
    # Step 2: Detect Relationships
    for rel_type, patterns in self.relationship_patterns.items():
        for pattern in patterns:
            for col in columns:
                if pattern in col or col in pattern:
                    # Determine source/target types
                    mapping['relationships'].append({...})
```

**Purpose:** Automatically map input columns to Neo4j schema

**Algorithm:**

```
For each Node Type (Drug, Target, etc.):
   1. Search columns for identifier patterns
      Example: "drug_name", "compound" → matches "Drug"
   
   2. Search columns for property patterns
      Example: "moa", "mechanism_of_action" → maps to Drug.moa
   
   3. If identifier found → add to mapping['nodes']

For each Relationship Type:
   1. Search columns for relationship patterns
      Example: "targets", "biological_targets" → TARGETS relationship
   
   2. Determine source/target from relationship type
      TARGETS → (Drug → Target)
   
   3. Add to mapping['relationships']
```

**Output Structure:**
```json
{
  "nodes": {
    "Drug": {
      "identifier_column": "drug_name",
      "properties": {
        "moa": "mechanism_of_action",
        "phase": "clinical_phase"
      }
    }
  },
  "relationships": [
    {
      "type": "TARGETS",
      "source_type": "Drug",
      "target_type": "Target",
      "column": "targets",
      "delimiter": ","
    }
  ]
}
```

---

### **5. Multi-Value Parsing (Lines 210-217)**

```python
def parse_multi_value(self, value: str, delimiter: str = ',') -> List[str]:
    if pd.isna(value) or value == '':
        return []
    
    values = [v.strip() for v in str(value).split(delimiter)]
    return [v for v in values if v]  # Remove empty strings
```

**Purpose:** Parse delimited strings into lists

**Example:**
```
Input:  "PTGS1|PTGS2|PTGS3"
Output: ["PTGS1", "PTGS2", "PTGS3"]
```

**Used For:** Relationships with multiple targets in one column

---

### **6. Validation (Lines 219-239)**

```python
def validate_mapping(self, df: pd.DataFrame, mapping: Dict) -> List[str]:
    errors = []
    
    # Check identifier columns exist
    for node_type, node_config in mapping['nodes'].items():
        if id_col not in df.columns:
            errors.append(f"Identifier column '{id_col}' not found")
    
    # Check property columns exist
    for prop_name, prop_col in node_config['properties'].items():
        if prop_col not in df.columns:
            errors.append(f"Property column '{prop_col}' not found")
    
    return errors  # Empty list = valid
```

**Purpose:** Verify mapping references valid columns

**Flow:**
1. Check all identifier columns exist in DataFrame
2. Check all property columns exist in DataFrame
3. Check all relationship columns exist
4. Return list of errors (empty if valid)

---

### **7. Main Ingestion Orchestrator (Lines 241-284)**

```python
def ingest_data(self, file_path: str, mapping: Optional[Dict] = None):
    # Step 1: Load Data
    df = self.load_data(file_path)
    
    # Step 2: Auto-detect or use provided mapping
    if mapping is None:
        mapping = self.auto_detect_mapping(df)
    
    # Step 3: Validate
    errors = self.validate_mapping(df, mapping)
    if errors:
        raise ValueError("Mapping validation failed")
    
    # Step 4: Process in Neo4j session
    with self.driver.session() as session:
        # Create nodes first
        for node_type, node_config in mapping['nodes'].items():
            nodes_created = self._create_nodes(session, df, node_type, node_config)
        
        # Then create relationships
        for rel_config in mapping['relationships']:
            rels_created = self._create_relationships(session, df, rel_config)
    
    return results
```

**Purpose:** Main workflow orchestrator

**Execution Flow:**
```
ingest_data()
    ↓
load_data() → DataFrame
    ↓
auto_detect_mapping() → Mapping dict
    ↓
validate_mapping() → [errors] (empty if OK)
    ↓
Neo4j Session
    ├── _create_nodes() → Creates all node types
    └── _create_relationships() → Creates all relationships
    ↓
Return results
```

**Design Pattern:** **Template Method** - Orchestrates sub-methods

---

### **8. Node Creation (Lines 286-323)**

```python
def _create_nodes(self, session, df, node_type: str, node_config: Dict):
    # Step 1: Prepare node data from DataFrame
    nodes_data = []
    for _, row in df.iterrows():
        node_data = {'name': row[id_col]}  # Required identifier
        
        # Add optional properties
        for prop_name, prop_col in properties.items():
            if prop_col in df.columns and not pd.isna(row[prop_col]):
                node_data[prop_name] = row[prop_col]
        
        nodes_data.append(node_data)
    
    # Step 2: Remove duplicates (by name)
    unique_nodes = []
    seen = set()
    for node in nodes_data:
        if node['name'] not in seen:
            unique_nodes.append(node)
            seen.add(node['name'])
    
    # Step 3: Batch create in Neo4j
    query = """
    UNWIND $nodes AS node
    MERGE (n:NodeType {name: node.name})
    SET n += node
    """
    session.run(query, nodes=unique_nodes)
```

**Purpose:** Create nodes in batch using Neo4j UNWIND

**Key Features:**
- **Batch processing** - All nodes in one query
- **Duplicate handling** - Removes duplicates in Python, MERGE handles DB duplicates
- **Property filtering** - Only adds non-null values
- **MERGE pattern** - Updates existing, creates if new

**Cypher Query Explained:**
```cypher
UNWIND $nodes AS node          -- Iterate over node list
MERGE (n:Drug {name: node.name})  -- Find or create node
SET n += node                  -- Add/update properties
```

---

### **9. Relationship Creation (Lines 325-361)**

```python
def _create_relationships(self, session, df, rel_config: Dict):
    relationships_data = []
    
    # Step 1: Extract relationship data from DataFrame
    for _, row in df.iterrows():
        source_name = row.get('drug_name', None)  # From source_type
        targets = self.parse_multi_value(row['targets'], delimiter='|')
        
        # Create one relationship per target
        for target in targets:
            relationships_data.append({
                'source_name': source_name,
                'target_name': target
            })
    
    # Step 2: Batch create relationships
    query = """
    UNWIND $rels AS rel
    MATCH (source:Drug {name: rel.source_name})
    MATCH (target:Target {name: rel.target_name})
    MERGE (source)-[:TARGETS]->(target)
    """
    session.run(query, rels=relationships_data)
```

**Purpose:** Create relationships in batch

**Key Features:**
- **Multi-value expansion** - One column → multiple relationships
- **Batch processing** - All relationships in one query
- **MERGE prevents duplicates** - Safe to re-run

**Example:**
```
Row: {drug_name: "aspirin", targets: "PTGS1|PTGS2"}
    ↓
Expands to:
  [
    {source_name: "aspirin", target_name: "PTGS1"},
    {source_name: "aspirin", target_name: "PTGS2"}
  ]
    ↓
Creates 2 TARGETS relationships
```

---

### **10. Template System (Lines 363-381)**

```python
def save_mapping_template(self, mapping: Dict, output_path: str):
    template = {
        'version': '1.0',
        'description': 'Auto-generated mapping template',
        'mapping': mapping
    }
    yaml.dump(template, f)

def load_mapping_template(self, template_path: str) -> Dict:
    template = yaml.safe_load(f)
    return template['mapping']
```

**Purpose:** Save/load mappings for reuse

**Use Case:**
- Save auto-detected mapping
- Reuse for similar files
- Manual mapping override

---

### **11. CLI Interface (Lines 387-452)**

```python
def main():
    parser = argparse.ArgumentParser(...)
    parser.add_argument('file', help='Input file')
    parser.add_argument('--mapping', help='Mapping template')
    parser.add_argument('--preview', action='store_true')
    parser.add_argument('--save-template', help='Save template')
    
    args = parser.parse_args()
    service = MinimalDataIngestion()
    
    if args.preview:
        # Preview mode - no ingestion
        df = service.load_data(args.file)
        mapping = service.auto_detect_mapping(df)
        print(json.dumps(mapping, indent=2))
        
    else:
        # Ingestion mode
        mapping = service.load_mapping_template(args.mapping) if args.mapping else None
        results = service.ingest_data(args.file, mapping)
        print(f"Nodes: {results['nodes_created']}")
```

**Purpose:** Command-line interface

**Modes:**
1. **Preview** (`--preview`) - Show mapping without ingesting
2. **Ingest** (default) - Load and ingest data
3. **Template** (`--save-template`) - Save mapping for reuse
4. **Custom Mapping** (`--mapping`) - Use saved template

---

## 🔄 Complete Data Flow

```
User runs: python minimal_data_ingestion.py data.csv --preview
    ↓
main() → Parse arguments
    ↓
MinimalDataIngestion() → Initialize (patterns, Neo4j connection)
    ↓
service.load_data("data.csv")
    ├── detect_file_format() → "csv"
    └── pd.read_csv() → DataFrame
    ↓
service.auto_detect_mapping(df)
    ├── Match columns to patterns
    ├── Build node mappings
    └── Build relationship mappings
    ↓
service.validate_mapping(df, mapping)
    └── Check all columns exist
    ↓
[Preview Mode] → Print mapping
    OR
[Ingest Mode] → service.ingest_data()
    ├── _create_nodes() → MERGE nodes
    └── _create_relationships() → MERGE relationships
    ↓
Return results
```

---

## 🎯 Key Design Patterns

### **1. Strategy Pattern**
- **Pattern-based matching** - Different strategies for different node types
- **Extensible** - Add new patterns without changing code

### **2. Template Method Pattern**
- **ingest_data()** orchestrates sub-methods
- **Consistent workflow** - Always: load → detect → validate → ingest

### **3. Batch Processing Pattern**
- **UNWIND in Neo4j** - Process all records in one transaction
- **Efficient** - Single query vs. multiple queries

### **4. Separation of Concerns**
- **File loading** - Separate from mapping
- **Mapping** - Separate from ingestion
- **Validation** - Separate check step

---

## 📊 Data Structures

### **Mapping Dictionary:**
```python
{
    'nodes': {
        'Drug': {
            'identifier_column': 'drug_name',
            'properties': {
                'moa': 'mechanism_of_action',
                'phase': 'clinical_phase'
            }
        }
    },
    'relationships': [
        {
            'type': 'TARGETS',
            'source_type': 'Drug',
            'target_type': 'Target',
            'column': 'targets',
            'delimiter': '|'
        }
    ]
}
```

### **Results Dictionary:**
```python
{
    'nodes_created': 12,
    'relationships_created': 18,
    'errors': []
}
```

---

## 🔑 Key Methods Summary

| Method | Purpose | Input | Output |
|--------|---------|-------|--------|
| `detect_file_format()` | Identify file type | File path | Format string |
| `load_data()` | Load file to DataFrame | File path | DataFrame |
| `auto_detect_mapping()` | Map columns to schema | DataFrame | Mapping dict |
| `validate_mapping()` | Check mapping validity | DataFrame, Mapping | Error list |
| `ingest_data()` | **MAIN** - Orchestrate ingestion | File path, Mapping | Results dict |
| `_create_nodes()` | Batch create nodes | Session, DataFrame, Config | Count |
| `_create_relationships()` | Batch create relationships | Session, DataFrame, Config | Count |
| `parse_multi_value()` | Split delimited strings | String, Delimiter | List |

---

## 🎯 Extensibility Points

**To add new node type:**
1. Add to `mapping_patterns` in `__init__()`
2. Add identifier and property patterns
3. Done! (no code changes needed)

**To add new file format:**
1. Add format detection in `detect_file_format()`
2. Add loading logic in `load_data()`
3. Convert to DataFrame (standard format)

**To change duplicate handling:**
1. Modify MERGE query in `_create_nodes()`
2. Could change to CREATE (fail on duplicates)
3. Could add ON CREATE/ON MATCH clauses

---

**Last Updated:** October 16, 2025  
**Total Lines:** 453  
**Classes:** 1 (MinimalDataIngestion)  
**Main Methods:** 10  
**CLI Commands:** 4


