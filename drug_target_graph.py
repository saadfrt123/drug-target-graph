import pandas as pd
import numpy as np
from neo4j import GraphDatabase
import logging
from typing import List, Dict, Any
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DrugTargetGraphBuilder:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password", database="neo4j"):
        """
        Initialize the graph builder with Neo4j connection parameters
        
        Args:
            uri: Neo4j database URI
            user: Neo4j username
            password: Neo4j password
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database
        
    def close(self):
        """Close the database connection"""
        self.driver.close()
        
    def read_drug_data(self, file_path: str) -> pd.DataFrame:
        """
        Read the drug data from the text file
        
        Args:
            file_path: Path to the drug data file
            
        Returns:
            DataFrame containing the drug data
        """
        try:
            # Read the tab-separated file
            df = pd.read_csv(file_path, sep='\t', encoding='utf-8')
            logger.info(f"Successfully read {len(df)} drug records from {file_path}")
            return df
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise
            
    def clean_targets(self, targets_str: str) -> List[str]:
        """
        Clean and parse the targets string into a list of individual targets
        
        Args:
            targets_str: Comma-separated string of targets
            
        Returns:
            List of cleaned target names
        """
        if pd.isna(targets_str) or targets_str == '':
            return []
            
        # Split by comma and clean each target
        targets = [target.strip() for target in str(targets_str).split(',')]
        # Remove empty strings and duplicates
        targets = [target for target in targets if target and target != '']
        return list(set(targets))  # Remove duplicates
        
    def create_constraints(self):
        """Create unique constraints for nodes"""
        with self.driver.session(database=self.database) as session:
            # Create unique constraints for Drug and Target nodes
            session.run("CREATE CONSTRAINT drug_name IF NOT EXISTS FOR (d:Drug) REQUIRE d.name IS UNIQUE")
            session.run("CREATE CONSTRAINT target_name IF NOT EXISTS FOR (t:Target) REQUIRE t.name IS UNIQUE")
            logger.info("Created unique constraints for Drug and Target nodes")
            
    def clear_database(self):
        """Clear all existing data from the database"""
        with self.driver.session(database=self.database) as session:
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("Cleared all existing data from the database")
            
    def create_drug_target_graph(self, df: pd.DataFrame):
        """
        Create the drug-target graph in Neo4j
        
        Args:
            df: DataFrame containing drug data
        """
        with self.driver.session(database=self.database) as session:
            # Process each drug
            for idx, row in df.iterrows():
                drug_name = row['Name']
                moa = row['MOA'] if pd.notna(row['MOA']) else ''
                phase = row['Phase'] if pd.notna(row['Phase']) else ''
                targets = self.clean_targets(row['Target'])
                
                # Create drug node
                session.run("""
                    MERGE (d:Drug {name: $drug_name})
                    SET d.moa = $moa, d.phase = $phase
                """, drug_name=drug_name, moa=moa, phase=phase)
                
                # Create target nodes and relationships
                for target in targets:
                    session.run("""
                        MERGE (t:Target {name: $target_name})
                    """, target_name=target)
                    
                    session.run("""
                        MATCH (d:Drug {name: $drug_name})
                        MATCH (t:Target {name: $target_name})
                        MERGE (d)-[:TARGETS]->(t)
                    """, drug_name=drug_name, target_name=target)
                    
            logger.info(f"Successfully created graph with {len(df)} drugs")
            
    def get_graph_statistics(self) -> Dict[str, Any]:
        """Get statistics about the created graph"""
        with self.driver.session(database=self.database) as session:
            # Count nodes
            drug_count = session.run("MATCH (d:Drug) RETURN count(d) as count").single()["count"]
            target_count = session.run("MATCH (t:Target) RETURN count(t) as count").single()["count"]
            
            # Count relationships
            relationship_count = session.run("MATCH ()-[r:TARGETS]->() RETURN count(r) as count").single()["count"]
            
            # Get drugs with most targets
            top_drugs = session.run("""
                MATCH (d:Drug)-[:TARGETS]->(t:Target)
                RETURN d.name as drug, count(t) as target_count
                ORDER BY target_count DESC
                LIMIT 10
            """).data()
            
            # Get targets with most drugs
            top_targets = session.run("""
                MATCH (d:Drug)-[:TARGETS]->(t:Target)
                RETURN t.name as target, count(d) as drug_count
                ORDER BY drug_count DESC
                LIMIT 10
            """).data()
            
            return {
                "drug_count": drug_count,
                "target_count": target_count,
                "relationship_count": relationship_count,
                "top_drugs": top_drugs,
                "top_targets": top_targets
            }
            
    def find_drugs_by_target(self, target_name: str) -> List[Dict]:
        """Find all drugs that target a specific target"""
        with self.driver.session(database=self.database) as session:
            result = session.run("""
                MATCH (d:Drug)-[:TARGETS]->(t:Target {name: $target_name})
                RETURN d.name as drug, d.moa as moa, d.phase as phase
                ORDER BY d.name
            """, target_name=target_name)
            return result.data()
            
    def find_targets_by_drug(self, drug_name: str) -> List[Dict]:
        """Find all targets for a specific drug"""
        with self.driver.session(database=self.database) as session:
            result = session.run("""
                MATCH (d:Drug {name: $drug_name})-[:TARGETS]->(t:Target)
                RETURN t.name as target
                ORDER BY t.name
            """, drug_name=drug_name)
            return result.data()
            
    def find_common_targets(self, drug1: str, drug2: str) -> List[Dict]:
        """Find common targets between two drugs"""
        with self.driver.session(database=self.database) as session:
            result = session.run("""
                MATCH (d1:Drug {name: $drug1})-[:TARGETS]->(t:Target)<-[:TARGETS]-(d2:Drug {name: $drug2})
                RETURN t.name as target
                ORDER BY t.name
            """, drug1=drug1, drug2=drug2)
            return result.data()

def main():
    """Main function to build the drug-target graph"""
    # Import configuration
    from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE
    
    # Initialize the graph builder
    graph_builder = DrugTargetGraphBuilder(
        uri=NEO4J_URI,
        user=NEO4J_USER, 
        password=NEO4J_PASSWORD,
        database=NEO4J_DATABASE
    )
    
    try:
        # Read the drug data
        from config import DRUG_DATA_FILE
        df = graph_builder.read_drug_data(DRUG_DATA_FILE)
        
        # Clear existing data and create constraints
        graph_builder.clear_database()
        graph_builder.create_constraints()
        
        # Build the graph
        graph_builder.create_drug_target_graph(df)
        
        # Get and display statistics
        stats = graph_builder.get_graph_statistics()
        
        print("\n=== Drug-Target Graph Statistics ===")
        print(f"Total Drugs: {stats['drug_count']}")
        print(f"Total Targets: {stats['target_count']}")
        print(f"Total Drug-Target Relationships: {stats['relationship_count']}")
        
        print("\n=== Top 10 Drugs by Number of Targets ===")
        for i, drug in enumerate(stats['top_drugs'], 1):
            print(f"{i}. {drug['drug']}: {drug['target_count']} targets")
            
        print("\n=== Top 10 Targets by Number of Drugs ===")
        for i, target in enumerate(stats['top_targets'], 1):
            print(f"{i}. {target['target']}: {target['drug_count']} drugs")
            
        # Example queries
        print("\n=== Example Queries ===")
        
        # Find drugs targeting a specific target
        example_target = "DRD2"
        drugs_for_target = graph_builder.find_drugs_by_target(example_target)
        print(f"\nDrugs targeting {example_target}:")
        for drug in drugs_for_target[:5]:  # Show first 5
            print(f"- {drug['drug']} (MOA: {drug['moa']}, Phase: {drug['phase']})")
            
        # Find targets for a specific drug
        example_drug = "abacavir"
        targets_for_drug = graph_builder.find_targets_by_drug(example_drug)
        print(f"\nTargets for {example_drug}:")
        for target in targets_for_drug:
            print(f"- {target['target']}")
            
    except Exception as e:
        logger.error(f"Error building graph: {e}")
    finally:
        graph_builder.close()

if __name__ == "__main__":
    main()
