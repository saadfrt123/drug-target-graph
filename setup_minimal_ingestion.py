#!/usr/bin/env python3
"""
Quick Setup Script for Minimal Data Ingestion Service
Run this to install dependencies and test the service
"""

import subprocess
import sys
import os
import codecs
from pathlib import Path

# Fix Unicode encoding on Windows
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

def install_dependencies():
    """Install required packages"""
    packages = [
        'pandas',
        'neo4j',
        'pyyaml',
        'openpyxl'  # For Excel support
    ]
    
    print("Installing dependencies...")
    for package in packages:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            print(f"[OK] {package} installed")
        except subprocess.CalledProcessError:
            print(f"[FAIL] Failed to install {package}")
            return False
    
    return True

def create_sample_data():
    """Create sample data files for testing"""
    
    # Sample CSV data
    csv_data = """drug_name,moa,phase,targets,disease_area,vendor
aspirin,cyclooxygenase inhibitor,Approved,PTGS1|PTGS2,Pain Management,Selleck Chemicals
ibuprofen,NSAID,Approved,PTGS1|PTGS2,Pain Management,Tocris
acetaminophen,COX inhibitor,Approved,PTGS2,Pain Management,Sigma-Aldrich"""
    
    with open('sample_drugs.csv', 'w') as f:
        f.write(csv_data)
    
    # Sample JSON data
    json_data = [
        {
            "compound_name": "metformin",
            "mechanism_of_action": "AMPK activator",
            "clinical_stage": "Approved",
            "biological_targets": "AMPK,GLUT4",
            "therapeutic_area": "Diabetes",
            "supplier": "MedChem Express"
        },
        {
            "compound_name": "warfarin",
            "mechanism_of_action": "Vitamin K antagonist",
            "clinical_stage": "Approved", 
            "biological_targets": "VKORC1,CYP2C9",
            "therapeutic_area": "Cardiovascular",
            "supplier": "Cayman Chemical"
        }
    ]
    
    import json
    with open('sample_drugs.json', 'w') as f:
        json.dump(json_data, f, indent=2)
    
    print("[OK] Sample data files created:")
    print("  - sample_drugs.csv")
    print("  - sample_drugs.json")

def test_service():
    """Test the ingestion service"""
    print("\n=== Testing Minimal Data Ingestion Service ===")
    
    # Test preview mode
    print("\n1. Testing preview mode with CSV:")
    try:
        result = subprocess.run([
            sys.executable, 'minimal_data_ingestion.py', 
            'sample_drugs.csv', '--preview'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[OK] Preview test passed")
            print(result.stdout)
        else:
            print("[FAIL] Preview test failed")
            print(result.stderr)
    except Exception as e:
        print(f"[ERROR] Preview test error: {e}")
    
    # Test JSON preview
    print("\n2. Testing preview mode with JSON:")
    try:
        result = subprocess.run([
            sys.executable, 'minimal_data_ingestion.py',
            'sample_drugs.json', '--preview'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("[OK] JSON preview test passed")
        else:
            print("[FAIL] JSON preview test failed")
            print(result.stderr)
    except Exception as e:
        print(f"[ERROR] JSON preview test error: {e}")

def create_usage_examples():
    """Create usage examples"""
    examples = """
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
"""
    
    with open('USAGE_EXAMPLES.md', 'w') as f:
        f.write(examples)
    
    print("[OK] Usage examples created: USAGE_EXAMPLES.md")

def main():
    """Main setup function"""
    print("Setting up Minimal Data Ingestion Service")
    
    # Check if config.py exists
    if not Path('config.py').exists():
        print("[ERROR] config.py not found. Please ensure Neo4j configuration exists.")
        return 1
    
    # Install dependencies
    if not install_dependencies():
        print("[ERROR] Dependency installation failed")
        return 1
    
    # Create sample data
    create_sample_data()
    
    # Create usage examples
    create_usage_examples()
    
    # Test service
    test_service()
    
    print("\n[SUCCESS] Setup complete!")
    print("\nNext steps:")
    print("1. Check Neo4j connection in config.py")
    print("2. Run: python minimal_data_ingestion.py sample_drugs.csv --preview")
    print("3. If preview looks good, run: python minimal_data_ingestion.py sample_drugs.csv")
    
    return 0

if __name__ == "__main__":
    exit(main())
