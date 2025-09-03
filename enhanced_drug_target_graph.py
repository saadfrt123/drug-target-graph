#!/usr/bin/env python3
"""
Enhanced Drug-Target Graph Database with Complete Data
- Uses ALL columns from Repurposing_Hub_export (1).txt
- Includes Disease Area, Indication, Vendor, Purity, SMILES
- Better data modeling and richer relationships
"""

from neo4j import GraphDatabase
import csv
import logging
import time
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedDrugTargetGraph:
    def __init__(self):
        """Initialize the enhanced drug-target graph"""
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        self.database = NEO4J_DATABASE
        logger.info("Connected to Neo4j database")

    def clear_database(self):
        """Clear the existing database"""
        logger.info("Clearing existing database...")
        with self.driver.session(database=self.database) as session:
            # Delete all relationships first
            session.run("MATCH ()-[r]->() DELETE r")
            # Delete all nodes
            session.run("MATCH (n) DELETE n")
        logger.info("Database cleared successfully")

    def create_constraints(self):
        """Create constraints and indexes for better performance"""
        logger.info("Creating constraints and indexes...")
        with self.driver.session(database=self.database) as session:
            try:
                # Create constraints for unique nodes
                session.run("CREATE CONSTRAINT drug_name IF NOT EXISTS FOR (d:Drug) REQUIRE d.name IS UNIQUE")
                session.run("CREATE CONSTRAINT target_name IF NOT EXISTS FOR (t:Target) REQUIRE t.name IS UNIQUE")
                session.run("CREATE CONSTRAINT disease_area_name IF NOT EXISTS FOR (da:DiseaseArea) REQUIRE da.name IS UNIQUE")
                session.run("CREATE CONSTRAINT indication_name IF NOT EXISTS FOR (i:Indication) REQUIRE i.name IS UNIQUE")
                session.run("CREATE CONSTRAINT vendor_name IF NOT EXISTS FOR (v:Vendor) REQUIRE v.name IS UNIQUE")
                
                # Create indexes for better search performance
                session.run("CREATE INDEX drug_moa IF NOT EXISTS FOR (d:Drug) ON (d.moa)")
                session.run("CREATE INDEX drug_phase IF NOT EXISTS FOR (d:Drug) ON (d.phase)")
                session.run("CREATE INDEX drug_smiles IF NOT EXISTS FOR (d:Drug) ON (d.smiles)")
                
                logger.info("Constraints and indexes created successfully")
            except Exception as e:
                logger.warning(f"Some constraints/indexes may already exist: {e}")

    def load_enhanced_data(self, filename="Repurposing_Hub_export (1).txt"):
        """Load the complete dataset with all columns"""
        logger.info(f"Loading enhanced data from {filename}...")
        
        drugs_data = []
        targets_data = []
        disease_areas_data = []
        indications_data = []
        vendors_data = []
        
        # Read and parse the data
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter='\t')
            
            for row_num, row in enumerate(reader, 1):
                if row_num % 1000 == 0:
                    logger.info(f"Processing row {row_num}...")
                
                # Extract drug information
                drug_name = row['Name'].strip()
                moa = row['MOA'].strip() if row['MOA'] else "Unknown"
                disease_area = row['Disease Area'].strip() if row['Disease Area'] else "Unknown"
                indication = row['Indication'].strip() if row['Indication'] else "Unknown"
                vendor = row['Vendor'].strip() if row['Vendor'] else "Unknown"
                purity = row['Purity'].strip() if row['Purity'] else None
                smiles = row['SMILES'].strip() if row['SMILES'] else None
                phase = row['Phase'].strip() if row['Phase'] else "Unknown"
                
                # Parse targets (comma-separated)
                target_list = [t.strip() for t in row['Target'].split(',') if t.strip()]
                
                # Store drug data
                drug_data = {
                    'name': drug_name,
                    'moa': moa,
                    'disease_area': disease_area,
                    'indication': indication,
                    'vendor': vendor,
                    'purity': purity,
                    'smiles': smiles,
                    'phase': phase,
                    'targets': target_list
                }
                drugs_data.append(drug_data)
                
                # Collect unique entities
                targets_data.extend(target_list)
                if disease_area != "Unknown":
                    disease_areas_data.append(disease_area)
                if indication != "Unknown":
                    indications_data.append(indication)
                if vendor != "Unknown":
                    vendors_data.extend([v.strip() for v in vendor.split(',') if v.strip()])
        
        # Remove duplicates
        unique_targets = list(set(targets_data))
        unique_disease_areas = list(set(disease_areas_data))
        unique_indications = list(set(indications_data))
        unique_vendors = list(set(vendors_data))
        
        logger.info(f"Parsed {len(drugs_data)} drugs, {len(unique_targets)} targets, "
                   f"{len(unique_disease_areas)} disease areas, {len(unique_indications)} indications, "
                   f"{len(unique_vendors)} vendors")
        
        return drugs_data, unique_targets, unique_disease_areas, unique_indications, unique_vendors

    def create_enhanced_nodes(self, drugs_data, targets, disease_areas, indications, vendors):
        """Create all nodes with enhanced properties"""
        logger.info("Creating enhanced nodes...")
        
        with self.driver.session(database=self.database) as session:
            # Create Drug nodes with all properties
            logger.info("Creating Drug nodes...")
            for i, drug in enumerate(drugs_data):
                if i % 100 == 0:
                    logger.info(f"Created {i}/{len(drugs_data)} drug nodes...")
                
                # Convert purity to float if possible
                purity_val = None
                if drug['purity']:
                    try:
                        purity_val = float(drug['purity'])
                    except:
                        pass
                
                session.run("""
                    CREATE (d:Drug {
                        name: $name,
                        moa: $moa,
                        disease_area: $disease_area,
                        indication: $indication,
                        vendor: $vendor,
                        purity: $purity,
                        smiles: $smiles,
                        phase: $phase
                    })
                """, 
                name=drug['name'],
                moa=drug['moa'],
                disease_area=drug['disease_area'],
                indication=drug['indication'],
                vendor=drug['vendor'],
                purity=purity_val,
                smiles=drug['smiles'],
                phase=drug['phase'])
            
            # Create Target nodes
            logger.info("Creating Target nodes...")
            for i, target in enumerate(targets):
                if i % 100 == 0:
                    logger.info(f"Created {i}/{len(targets)} target nodes...")
                session.run("CREATE (t:Target {name: $name})", name=target)
            
            # Create Disease Area nodes
            logger.info("Creating Disease Area nodes...")
            for disease_area in disease_areas:
                session.run("CREATE (da:DiseaseArea {name: $name})", name=disease_area)
            
            # Create Indication nodes
            logger.info("Creating Indication nodes...")
            for indication in indications:
                session.run("CREATE (i:Indication {name: $name})", name=indication)
            
            # Create Vendor nodes
            logger.info("Creating Vendor nodes...")
            for vendor in vendors:
                session.run("CREATE (v:Vendor {name: $name})", name=vendor)
        
        logger.info("All nodes created successfully")

    def create_enhanced_relationships(self, drugs_data):
        """Create relationships between all entities"""
        logger.info("Creating enhanced relationships...")
        
        with self.driver.session(database=self.database) as session:
            for i, drug in enumerate(drugs_data):
                if i % 100 == 0:
                    logger.info(f"Created relationships for {i}/{len(drugs_data)} drugs...")
                
                drug_name = drug['name']
                
                # Drug TARGETS Target relationships
                for target in drug['targets']:
                    session.run("""
                        MATCH (d:Drug {name: $drug_name})
                        MATCH (t:Target {name: $target_name})
                        CREATE (d)-[:TARGETS]->(t)
                    """, drug_name=drug_name, target_name=target)
                
                # Drug TREATS Indication relationships
                if drug['indication'] != "Unknown":
                    session.run("""
                        MATCH (d:Drug {name: $drug_name})
                        MATCH (i:Indication {name: $indication})
                        CREATE (d)-[:TREATS]->(i)
                    """, drug_name=drug_name, indication=drug['indication'])
                
                # Drug BELONGS_TO DiseaseArea relationships
                if drug['disease_area'] != "Unknown":
                    session.run("""
                        MATCH (d:Drug {name: $drug_name})
                        MATCH (da:DiseaseArea {name: $disease_area})
                        CREATE (d)-[:BELONGS_TO]->(da)
                    """, drug_name=drug_name, disease_area=drug['disease_area'])
                
                # Drug SUPPLIED_BY Vendor relationships
                if drug['vendor'] != "Unknown":
                    vendor_list = [v.strip() for v in drug['vendor'].split(',') if v.strip()]
                    for vendor in vendor_list:
                        session.run("""
                            MATCH (d:Drug {name: $drug_name})
                            MATCH (v:Vendor {name: $vendor})
                            CREATE (d)-[:SUPPLIED_BY]->(v)
                        """, drug_name=drug_name, vendor=vendor)
        
        logger.info("All relationships created successfully")

    def get_database_statistics(self):
        """Get comprehensive statistics about the enhanced database"""
        with self.driver.session(database=self.database) as session:
            stats = {}
            
            # Count nodes
            stats['drugs'] = session.run("MATCH (d:Drug) RETURN count(d) as count").single()["count"]
            stats['targets'] = session.run("MATCH (t:Target) RETURN count(t) as count").single()["count"]
            stats['disease_areas'] = session.run("MATCH (da:DiseaseArea) RETURN count(da) as count").single()["count"]
            stats['indications'] = session.run("MATCH (i:Indication) RETURN count(i) as count").single()["count"]
            stats['vendors'] = session.run("MATCH (v:Vendor) RETURN count(v) as count").single()["count"]
            
            # Count relationships
            stats['drug_target_rels'] = session.run("MATCH ()-[r:TARGETS]->() RETURN count(r) as count").single()["count"]
            stats['drug_indication_rels'] = session.run("MATCH ()-[r:TREATS]->() RETURN count(r) as count").single()["count"]
            stats['drug_disease_rels'] = session.run("MATCH ()-[r:BELONGS_TO]->() RETURN count(r) as count").single()["count"]
            stats['drug_vendor_rels'] = session.run("MATCH ()-[r:SUPPLIED_BY]->() RETURN count(r) as count").single()["count"]
            
            return stats

    def close(self):
        """Close the database connection"""
        self.driver.close()
        logger.info("Database connection closed")

def main():
    """Main function to rebuild the enhanced database"""
    print("🚀 Building Enhanced Drug-Target Graph Database...")
    print("📁 Using complete Repurposing_Hub_export (1).txt file with ALL columns")
    
    # Initialize the graph
    graph = EnhancedDrugTargetGraph()
    
    try:
        # Clear existing data
        graph.clear_database()
        
        # Create constraints and indexes
        graph.create_constraints()
        
        # Load enhanced data
        drugs_data, targets, disease_areas, indications, vendors = graph.load_enhanced_data()
        
        # Create all nodes
        graph.create_enhanced_nodes(drugs_data, targets, disease_areas, indications, vendors)
        
        # Create all relationships
        graph.create_enhanced_relationships(drugs_data)
        
        # Get final statistics
        stats = graph.get_database_statistics()
        
        print("\n🎉 Enhanced Database Built Successfully!")
        print(f"📊 Drugs: {stats['drugs']}")
        print(f"🎯 Targets: {stats['targets']}")
        print(f"🏥 Disease Areas: {stats['disease_areas']}")
        print(f"💊 Indications: {stats['indications']}")
        print(f"🏪 Vendors: {stats['vendors']}")
        print(f"🔗 Drug-Target Relationships: {stats['drug_target_rels']}")
        print(f"🔗 Drug-Indication Relationships: {stats['drug_indication_rels']}")
        print(f"🔗 Drug-Disease Area Relationships: {stats['drug_disease_rels']}")
        print(f"🔗 Drug-Vendor Relationships: {stats['drug_vendor_rels']}")
        
    finally:
        graph.close()

if __name__ == "__main__":
    main()
