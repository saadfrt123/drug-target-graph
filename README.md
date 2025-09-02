# Drug-Target Graph Database

This project creates a Neo4j graph database from drug-target relationship data, allowing you to explore and analyze drug-target interactions, find similar drugs, and discover potential drug repurposing opportunities.

## Features

- **Graph Database**: Uses Neo4j to model drug-target relationships
- **Data Import**: Automatically imports drug data from tab-separated text files
- **Query Interface**: Interactive command-line interface for exploring the graph
- **Advanced Analytics**: Find similar drugs, common targets, and drug combinations
- **Statistics**: Comprehensive statistics on drugs, targets, and relationships

## Prerequisites

1. **Neo4j Database**: You need Neo4j installed and running
   - Download from: https://neo4j.com/download/
   - Or use Neo4j Desktop: https://neo4j.com/download-center/#desktop
   - Or use Neo4j AuraDB (cloud): https://neo4j.com/cloud/platform/aura-graph-database/

2. **Python 3.7+**: Required for running the scripts

## Installation

1. **Clone or download this project**

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Neo4j connection**:
   - Edit `config.py` to set your Neo4j credentials
   - Or create a `.env` file with:
     ```
     NEO4J_URI=bolt://localhost:7687
     NEO4J_USER=neo4j
     NEO4J_PASSWORD=your_password
     ```

4. **Update the data file path**:
   - Edit `config.py` and update `DRUG_DATA_FILE` to point to your data file

## Usage

### 1. Build the Graph Database

Run the main script to import your drug data and build the graph:

```bash
python drug_target_graph.py
```

This will:
- Read your drug data file
- Create Drug and Target nodes
- Create TARGETS relationships between drugs and targets
- Display statistics about the created graph

### 2. Explore the Graph

Use the interactive query interface:

```bash
python query_interface.py
```

Available options:
- **Search drugs**: Find drugs by name (partial match)
- **Search targets**: Find targets by name (partial match)
- **Get drug details**: View detailed information about a specific drug
- **Get target details**: View detailed information about a specific target
- **Find drug combinations**: Discover targets with multiple drugs
- **Phase statistics**: View drugs by development phase
- **MOA statistics**: View drugs by mechanism of action

### 3. Example Queries

The system provides several useful queries:

#### Find drugs targeting a specific target:
```python
drugs = graph_builder.find_drugs_by_target("DRD2")
```

#### Find targets for a specific drug:
```python
targets = graph_builder.find_targets_by_drug("abacavir")
```

#### Find common targets between two drugs:
```python
common_targets = graph_builder.find_common_targets("drug1", "drug2")
```

## Data Format

The system expects a tab-separated text file with the following columns:
- **Name**: Drug name
- **MOA**: Mechanism of Action
- **Target**: Comma-separated list of target genes/proteins
- **Phase**: Drug development phase

Example:
```
Name	MOA	Target	Phase
abacavir	nucleoside reverse transcriptase inhibitor		Launched
acetaminophen	cyclooxygenase inhibitor	PTGS1, PTGS2	Launched
```

## Graph Schema

The Neo4j graph uses the following schema:

### Nodes
- **Drug**: Represents a drug with properties:
  - `name`: Drug name
  - `moa`: Mechanism of action
  - `phase`: Development phase

- **Target**: Represents a biological target with properties:
  - `name`: Target name (gene/protein)

### Relationships
- **TARGETS**: Relationship from Drug to Target
  - Direction: `(Drug)-[:TARGETS]->(Target)`

## Advanced Features

### Drug Similarity
The system can find similar drugs based on shared targets, which is useful for:
- Drug repurposing opportunities
- Understanding drug mechanisms
- Finding alternative treatments

### Target Analysis
Analyze targets to understand:
- Which targets are most commonly targeted
- Which drugs target multiple targets
- Potential drug combination strategies

### Development Phase Analysis
Track drugs across different development phases to understand:
- Drug development pipeline
- Success rates by mechanism of action
- Market availability

## Troubleshooting

### Connection Issues
- Ensure Neo4j is running and accessible
- Check your connection credentials in `config.py`
- Verify the Neo4j port (default: 7687)

### Data Import Issues
- Check that your data file path is correct
- Ensure the file format matches the expected tab-separated format
- Verify file encoding (UTF-8 recommended)

### Performance Issues
- For large datasets, consider using Neo4j's batch import tools
- Index frequently queried properties
- Use appropriate Cypher query optimization

## Contributing

Feel free to extend this project with:
- Additional data sources
- More sophisticated analytics
- Web interface
- Machine learning models for drug discovery

## License

This project is open source. Feel free to use and modify as needed.
