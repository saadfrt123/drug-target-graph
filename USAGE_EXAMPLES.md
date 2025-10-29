
# Minimal Data Ingestion Service - Usage Examples

## Basic Usage

### 1. Preview mapping (no data ingestion)
python minimal_data_ingestion.py sample_drugs.csv --preview

### 2. Ingest data with auto-detection
python minimal_data_ingestion.py sample_drugs.csv

### 3. Save auto-detected mapping as template
python minimal_data_ingestion.py sample_drugs.csv --save-template my_mapping.yaml

### 4. Use saved mapping template
python minimal_data_ingestion.py new_data.csv --mapping my_mapping.yaml

## Supported File Formats
- CSV (.csv)
- TSV (.tsv) 
- JSON (.json)
- Excel (.xlsx, .xls)

## Auto-Detection Patterns

The service automatically detects:
- Drug nodes: columns like 'drug_name', 'compound', 'molecule'
- Target nodes: columns like 'target', 'protein', 'gene'
- Properties: 'moa', 'phase', 'smiles', 'purity', etc.
- Relationships: 'targets', 'treats', 'disease_area', 'vendor'

## Multi-Value Fields
Use pipe (|) or comma (,) separators:
- targets: "PTGS1|PTGS2" or "PTGS1,PTGS2"

## Example Data Structure
```csv
drug_name,moa,phase,targets,disease_area,vendor
aspirin,cyclooxygenase inhibitor,Approved,PTGS1|PTGS2,Pain Management,Selleck Chemicals
```

## Troubleshooting
- Use --preview to check mapping before ingestion
- Check Neo4j connection in config.py
- Ensure file format is supported
- Check column names match patterns
