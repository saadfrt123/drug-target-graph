#!/usr/bin/env python3
"""
Minimal Data Ingestion Service - Tonight Implementation
Purpose: Basic schema-agnostic data ingestion into Neo4j
"""

import pandas as pd
import json
import yaml
import logging
import sys
import codecs
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE

# Fix Unicode encoding on Windows
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MinimalDataIngestion:
    """Minimal data ingestion service for tonight implementation"""
    
    def __init__(self):
        """Initialize with Neo4j connection"""
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        self.database = NEO4J_DATABASE
        
        # Auto-mapping patterns
        self.mapping_patterns = {
            'Drug': {
                'identifiers': ['name', 'drug_name', 'compound', 'molecule', 'chemical_name'],
                'properties': {
                    'moa': ['moa', 'mechanism', 'mechanism_of_action', 'mode_of_action'],
                    'phase': ['phase', 'clinical_phase', 'development_stage', 'stage'],
                    'smiles': ['smiles', 'canonical_smiles', 'structure', 'smiles_string'],
                    'purity': ['purity', 'purity_percent', 'purity_%'],
                    'disease_area': ['disease_area', 'disease', 'therapeutic_area'],
                    'indication': ['indication', 'medical_indication', 'use'],
                    'vendor': ['vendor', 'supplier', 'company']
                }
            },
            'Target': {
                'identifiers': ['target', 'target_name', 'protein', 'gene', 'receptor', 'enzyme'],
                'properties': {
                    'name': ['name', 'target_name', 'gene_symbol', 'protein_name']
                }
            },
            'DiseaseArea': {
                'identifiers': ['disease_area', 'disease', 'therapeutic_area', 'area'],
                'properties': {
                    'name': ['name', 'disease_area', 'area_name']
                }
            },
            'Indication': {
                'identifiers': ['indication', 'medical_indication', 'use', 'condition'],
                'properties': {
                    'name': ['name', 'indication', 'condition']
                }
            },
            'Vendor': {
                'identifiers': ['vendor', 'supplier', 'company', 'manufacturer'],
                'properties': {
                    'name': ['name', 'vendor', 'company_name']
                }
            }
        }
        
        # Relationship patterns
        self.relationship_patterns = {
            'TARGETS': ['targets', 'target', 'biological_targets', 'target_list'],
            'TREATS': ['treats', 'indication', 'medical_indication'],
            'BELONGS_TO': ['disease_area', 'therapeutic_area', 'area'],
            'SUPPLIED_BY': ['vendor', 'supplier', 'supplied_by']
        }
    
    def detect_file_format(self, file_path: str) -> str:
        """Detect file format"""
        path = Path(file_path)
        suffix = path.suffix.lower()
        
        if suffix in ['.csv', '.tsv']:
            return 'csv'
        elif suffix == '.json':
            return 'json'
        elif suffix in ['.xlsx', '.xls']:
            return 'excel'
        else:
            return 'unknown'
    
    def load_data(self, file_path: str) -> pd.DataFrame:
        """Load data from file"""
        format_type = self.detect_file_format(file_path)
        
        try:
            if format_type == 'csv':
                # Try different separators
                for sep in [',', '\t', ';', '|']:
                    try:
                        df = pd.read_csv(file_path, sep=sep)
                        if len(df.columns) > 1:
                            logger.info(f"Successfully loaded CSV with separator '{sep}'")
                            return df
                    except:
                        continue
                raise ValueError("Could not determine CSV separator")
                
            elif format_type == 'json':
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    df = pd.DataFrame(data)
                elif isinstance(data, dict):
                    df = pd.DataFrame([data])
                else:
                    raise ValueError("JSON format not supported")
                    
                logger.info("Successfully loaded JSON")
                return df
                
            elif format_type == 'excel':
                df = pd.read_excel(file_path)
                logger.info("Successfully loaded Excel")
                return df
                
            else:
                raise ValueError(f"Unsupported file format: {format_type}")
                
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {e}")
            raise
    
    def auto_detect_mapping(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Auto-detect mapping from DataFrame columns"""
        columns = [col.lower().strip() for col in df.columns]
        mapping = {
            'nodes': {},
            'relationships': []
        }
        
        # Detect node types and their identifier columns
        for node_type, patterns in self.mapping_patterns.items():
            identifier_col = None
            
            # Find identifier column
            for pattern in patterns['identifiers']:
                for col in columns:
                    if pattern in col or col in pattern:
                        identifier_col = col
                        break
                if identifier_col:
                    break
            
            if identifier_col:
                # Find property mappings
                properties = {}
                for prop_name, prop_patterns in patterns['properties'].items():
                    for pattern in prop_patterns:
                        for col in columns:
                            if pattern in col or col in pattern:
                                properties[prop_name] = col
                                break
                        if prop_name in properties:
                            break
                
                mapping['nodes'][node_type] = {
                    'identifier_column': identifier_col,
                    'properties': properties
                }
        
        # Detect relationships
        for rel_type, patterns in self.relationship_patterns.items():
            for pattern in patterns:
                for col in columns:
                    if pattern in col or col in pattern:
                        # Determine source and target types
                        source_type = None
                        target_type = None
                        
                        if rel_type == 'TARGETS':
                            source_type = 'Drug'
                            target_type = 'Target'
                        elif rel_type == 'TREATS':
                            source_type = 'Drug'
                            target_type = 'Indication'
                        elif rel_type == 'BELONGS_TO':
                            source_type = 'Drug'
                            target_type = 'DiseaseArea'
                        elif rel_type == 'SUPPLIED_BY':
                            source_type = 'Drug'
                            target_type = 'Vendor'
                        
                        if source_type and target_type:
                            mapping['relationships'].append({
                                'type': rel_type,
                                'source_type': source_type,
                                'target_type': target_type,
                                'column': col,
                                'delimiter': ','  # Default delimiter
                            })
                        break
        
        return mapping
    
    def parse_multi_value(self, value: str, delimiter: str = ',') -> List[str]:
        """Parse multi-value fields"""
        if pd.isna(value) or value == '':
            return []
        
        # Split and clean
        values = [v.strip() for v in str(value).split(delimiter)]
        return [v for v in values if v]
    
    def validate_mapping(self, df: pd.DataFrame, mapping: Dict[str, Any]) -> List[str]:
        """Validate mapping against data"""
        errors = []
        
        # Check if identifier columns exist
        for node_type, node_config in mapping['nodes'].items():
            id_col = node_config['identifier_column']
            if id_col not in df.columns:
                errors.append(f"Identifier column '{id_col}' not found for {node_type}")
            
            # Check property columns
            for prop_name, prop_col in node_config['properties'].items():
                if prop_col not in df.columns:
                    errors.append(f"Property column '{prop_col}' not found for {node_type}.{prop_name}")
        
        # Check relationship columns
        for rel in mapping['relationships']:
            if rel['column'] not in df.columns:
                errors.append(f"Relationship column '{rel['column']}' not found")
        
        return errors
    
    def ingest_data(self, file_path: str, mapping: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Main ingestion function"""
        logger.info(f"Starting ingestion of {file_path}")
        
        # Load data
        df = self.load_data(file_path)
        logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")
        
        # Auto-detect mapping if not provided
        if mapping is None:
            mapping = self.auto_detect_mapping(df)
            logger.info("Auto-detected mapping:")
            logger.info(json.dumps(mapping, indent=2))
        
        # Validate mapping
        errors = self.validate_mapping(df, mapping)
        if errors:
            logger.error("Mapping validation errors:")
            for error in errors:
                logger.error(f"  - {error}")
            raise ValueError("Mapping validation failed")
        
        # Process data
        results = {
            'nodes_created': 0,
            'relationships_created': 0,
            'errors': []
        }
        
        with self.driver.session(database=self.database) as session:
            # Create nodes first
            for node_type, node_config in mapping['nodes'].items():
                nodes_created = self._create_nodes(session, df, node_type, node_config)
                results['nodes_created'] += nodes_created
                logger.info(f"Created {nodes_created} {node_type} nodes")
            
            # Create relationships
            for rel_config in mapping['relationships']:
                rels_created = self._create_relationships(session, df, rel_config)
                results['relationships_created'] += rels_created
                logger.info(f"Created {rels_created} {rel_config['type']} relationships")
        
        logger.info(f"Ingestion complete: {results}")
        return results
    
    def _create_nodes(self, session, df: pd.DataFrame, node_type: str, node_config: Dict[str, Any]) -> int:
        """Create nodes in batch"""
        id_col = node_config['identifier_column']
        properties = node_config['properties']
        
        # Prepare node data
        nodes_data = []
        for _, row in df.iterrows():
            node_data = {'name': row[id_col]}
            
            # Add properties
            for prop_name, prop_col in properties.items():
                if prop_col in df.columns and not pd.isna(row[prop_col]):
                    node_data[prop_name] = row[prop_col]
            
            nodes_data.append(node_data)
        
        # Remove duplicates
        unique_nodes = []
        seen = set()
        for node in nodes_data:
            key = node['name']
            if key not in seen:
                unique_nodes.append(node)
                seen.add(key)
        
        if not unique_nodes:
            return 0
        
        # Batch create nodes
        query = f"""
        UNWIND $nodes AS node
        MERGE (n:{node_type} {{name: node.name}})
        SET n += node
        """
        
        result = session.run(query, nodes=unique_nodes)
        return len(unique_nodes)
    
    def _create_relationships(self, session, df: pd.DataFrame, rel_config: Dict[str, Any]) -> int:
        """Create relationships in batch"""
        rel_type = rel_config['type']
        source_type = rel_config['source_type']
        target_type = rel_config['target_type']
        column = rel_config['column']
        delimiter = rel_config.get('delimiter', ',')
        
        relationships_data = []
        
        for _, row in df.iterrows():
            source_name = row.get(source_type.lower() + '_name', None)
            if pd.isna(source_name):
                continue
            
            # Parse multi-value targets
            targets = self.parse_multi_value(row[column], delimiter)
            
            for target in targets:
                relationships_data.append({
                    'source_name': source_name,
                    'target_name': target
                })
        
        if not relationships_data:
            return 0
        
        # Batch create relationships
        query = f"""
        UNWIND $rels AS rel
        MATCH (source:{source_type} {{name: rel.source_name}})
        MATCH (target:{target_type} {{name: rel.target_name}})
        MERGE (source)-[:{rel_type}]->(target)
        """
        
        result = session.run(query, rels=relationships_data)
        return len(relationships_data)
    
    def save_mapping_template(self, mapping: Dict[str, Any], output_path: str):
        """Save mapping as template for reuse"""
        template = {
            'version': '1.0',
            'description': 'Auto-generated mapping template',
            'mapping': mapping
        }
        
        with open(output_path, 'w') as f:
            yaml.dump(template, f, default_flow_style=False)
        
        logger.info(f"Mapping template saved to {output_path}")
    
    def load_mapping_template(self, template_path: str) -> Dict[str, Any]:
        """Load mapping from template"""
        with open(template_path, 'r') as f:
            template = yaml.safe_load(f)
        
        return template['mapping']
    
    def close(self):
        """Close database connection"""
        self.driver.close()

def main():
    """CLI interface for minimal ingestion"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Minimal Data Ingestion Service')
    parser.add_argument('file', help='Input file path')
    parser.add_argument('--mapping', help='Mapping template file (optional)')
    parser.add_argument('--save-template', help='Save auto-detected mapping as template')
    parser.add_argument('--preview', action='store_true', help='Preview mapping without ingesting')
    
    args = parser.parse_args()
    
    # Initialize service
    service = MinimalDataIngestion()
    
    try:
        if args.preview:
            # Preview mode
            df = service.load_data(args.file)
            mapping = service.auto_detect_mapping(df)
            
            print("\n=== AUTO-DETECTED MAPPING ===")
            print(json.dumps(mapping, indent=2))
            
            errors = service.validate_mapping(df, mapping)
            if errors:
                print("\n=== VALIDATION ERRORS ===")
                for error in errors:
                    print(f"  - {error}")
            else:
                print("\n✅ Mapping validation passed!")
        
        else:
            # Load mapping if provided
            mapping = None
            if args.mapping:
                mapping = service.load_mapping_template(args.mapping)
                print(f"Loaded mapping from {args.mapping}")
            
            # Ingest data
            results = service.ingest_data(args.file, mapping)
            
            print("\n=== INGESTION RESULTS ===")
            print(f"Nodes created: {results['nodes_created']}")
            print(f"Relationships created: {results['relationships_created']}")
            if results['errors']:
                print(f"Errors: {len(results['errors'])}")
                for error in results['errors']:
                    print(f"  - {error}")
            
            # Save template if requested
            if args.save_template:
                auto_mapping = service.auto_detect_mapping(service.load_data(args.file))
                service.save_mapping_template(auto_mapping, args.save_template)
    
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        return 1
    
    finally:
        service.close()
    
    return 0

if __name__ == "__main__":
    exit(main())
