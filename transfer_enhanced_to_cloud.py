#!/usr/bin/env python3
"""
Transfer enhanced database from local Neo4j to Neo4j Aura cloud database
- Includes all new columns: Disease Area, Indication, Vendor, Purity, SMILES
- Preserves all new relationship types
"""

from neo4j import GraphDatabase
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Local database configuration
LOCAL_URI = "bolt://127.0.0.1:7687"
LOCAL_USER = "neo4j"
LOCAL_PASSWORD = "11223344"
LOCAL_DATABASE = "neo4j"

# Cloud database configuration (Neo4j Aura)
CLOUD_URI = "neo4j+s://c8287756.databases.neo4j.io"
CLOUD_USER = "neo4j"
CLOUD_PASSWORD = "bsSvDn8Kh-qVZrtwwAH2t3yhLf0pGjDKzCL8Bs5jqkM"
CLOUD_DATABASE = "neo4j"

def connect_to_databases():
    """Connect to both local and cloud databases"""
    try:
        # Connect to local database
        local_driver = GraphDatabase.driver(LOCAL_URI, auth=(LOCAL_USER, LOCAL_PASSWORD))
        logger.info("✅ Connected to local Neo4j database")
        
        # Connect to cloud database
        cloud_driver = GraphDatabase.driver(CLOUD_URI, auth=(CLOUD_USER, CLOUD_PASSWORD))
        logger.info("✅ Connected to Neo4j Aura cloud database")
        
        return local_driver, cloud_driver
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return None, None

def clear_cloud_database(cloud_driver):
    """Clear the cloud database to start fresh"""
    try:
        with cloud_driver.session(database=CLOUD_DATABASE) as session:
            # Delete all relationships first
            session.run("MATCH ()-[r]->() DELETE r")
            
            # Delete all nodes
            session.run("MATCH (n) DELETE n")
            
            logger.info("🗑️ Cloud database cleared")
    except Exception as e:
        logger.error(f"❌ Failed to clear cloud database: {e}")

def export_enhanced_drugs(local_driver):
    """Export enhanced drugs with all properties from local database"""
    try:
        with local_driver.session(database=LOCAL_DATABASE) as session:
            result = session.run("""
                MATCH (d:Drug)
                RETURN d.name as name, d.moa as moa, d.phase as phase,
                       d.disease_area as disease_area, d.indication as indication,
                       d.vendor as vendor, d.purity as purity, d.smiles as smiles
                ORDER BY d.name
            """)
            drugs = result.data()
            logger.info(f"📊 Exported {len(drugs)} enhanced drugs from local database")
            return drugs
    except Exception as e:
        logger.error(f"❌ Failed to export drugs: {e}")
        return []

def export_all_entities(local_driver):
    """Export all entity types"""
    try:
        with local_driver.session(database=LOCAL_DATABASE) as session:
            # Export targets
            targets = session.run("MATCH (t:Target) RETURN DISTINCT t.name as name ORDER BY t.name").data()
            
            # Export disease areas
            disease_areas = session.run("MATCH (da:DiseaseArea) RETURN DISTINCT da.name as name ORDER BY da.name").data()
            
            # Export indications
            indications = session.run("MATCH (i:Indication) RETURN DISTINCT i.name as name ORDER BY i.name").data()
            
            # Export vendors
            vendors = session.run("MATCH (v:Vendor) RETURN DISTINCT v.name as name ORDER BY v.name").data()
            
            logger.info(f"🎯 Exported {len(targets)} targets")
            logger.info(f"🏥 Exported {len(disease_areas)} disease areas")
            logger.info(f"💊 Exported {len(indications)} indications")
            logger.info(f"🏪 Exported {len(vendors)} vendors")
            
            return targets, disease_areas, indications, vendors
    except Exception as e:
        logger.error(f"❌ Failed to export entities: {e}")
        return [], [], [], []

def export_all_relationships(local_driver):
    """Export all relationship types"""
    try:
        with local_driver.session(database=LOCAL_DATABASE) as session:
            # Drug-Target relationships
            drug_target_rels = session.run("""
                MATCH (d:Drug)-[:TARGETS]->(t:Target)
                RETURN d.name as drug, t.name as target
            """).data()
            
            # Drug-Indication relationships
            drug_indication_rels = session.run("""
                MATCH (d:Drug)-[:TREATS]->(i:Indication)
                RETURN d.name as drug, i.name as indication
            """).data()
            
            # Drug-DiseaseArea relationships
            drug_disease_rels = session.run("""
                MATCH (d:Drug)-[:BELONGS_TO]->(da:DiseaseArea)
                RETURN d.name as drug, da.name as disease_area
            """).data()
            
            # Drug-Vendor relationships
            drug_vendor_rels = session.run("""
                MATCH (d:Drug)-[:SUPPLIED_BY]->(v:Vendor)
                RETURN d.name as drug, v.name as vendor
            """).data()
            
            logger.info(f"🔗 Exported {len(drug_target_rels)} drug-target relationships")
            logger.info(f"🔗 Exported {len(drug_indication_rels)} drug-indication relationships")
            logger.info(f"🔗 Exported {len(drug_disease_rels)} drug-disease area relationships")
            logger.info(f"🔗 Exported {len(drug_vendor_rels)} drug-vendor relationships")
            
            return drug_target_rels, drug_indication_rels, drug_disease_rels, drug_vendor_rels
    except Exception as e:
        logger.error(f"❌ Failed to export relationships: {e}")
        return [], [], [], []

def import_enhanced_drugs(cloud_driver, drugs):
    """Import enhanced drugs to cloud database"""
    try:
        with cloud_driver.session(database=CLOUD_DATABASE) as session:
            # Batch create drugs with all properties
            for i in range(0, len(drugs), 100):  # Process in batches of 100
                batch = drugs[i:i+100]
                session.run("""
                    UNWIND $drugs as drug
                    CREATE (d:Drug {
                        name: drug.name, 
                        moa: drug.moa, 
                        phase: drug.phase,
                        disease_area: drug.disease_area,
                        indication: drug.indication,
                        vendor: drug.vendor,
                        purity: drug.purity,
                        smiles: drug.smiles
                    })
                """, drugs=batch)
                logger.info(f"📊 Imported {min(i+100, len(drugs))}/{len(drugs)} enhanced drugs to cloud")
                time.sleep(0.1)  # Small delay to avoid overwhelming the cloud DB
            
            logger.info(f"✅ Successfully imported {len(drugs)} enhanced drugs to cloud database")
    except Exception as e:
        logger.error(f"❌ Failed to import drugs: {e}")

def import_all_entities(cloud_driver, targets, disease_areas, indications, vendors):
    """Import all entity types to cloud database"""
    try:
        with cloud_driver.session(database=CLOUD_DATABASE) as session:
            # Import targets
            for i in range(0, len(targets), 100):
                batch = targets[i:i+100]
                session.run("UNWIND $targets as target CREATE (t:Target {name: target.name})", targets=batch)
                logger.info(f"🎯 Imported {min(i+100, len(targets))}/{len(targets)} targets to cloud")
                time.sleep(0.1)
            
            # Import disease areas
            for i in range(0, len(disease_areas), 100):
                batch = disease_areas[i:i+100]
                session.run("UNWIND $disease_areas as da CREATE (d:DiseaseArea {name: da.name})", disease_areas=batch)
                logger.info(f"🏥 Imported {min(i+100, len(disease_areas))}/{len(disease_areas)} disease areas to cloud")
                time.sleep(0.1)
            
            # Import indications
            for i in range(0, len(indications), 100):
                batch = indications[i:i+100]
                session.run("UNWIND $indications as ind CREATE (i:Indication {name: ind.name})", indications=batch)
                logger.info(f"💊 Imported {min(i+100, len(indications))}/{len(indications)} indications to cloud")
                time.sleep(0.1)
            
            # Import vendors
            for i in range(0, len(vendors), 100):
                batch = vendors[i:i+100]
                session.run("UNWIND $vendors as vendor CREATE (v:Vendor {name: vendor.name})", vendors=batch)
                logger.info(f"🏪 Imported {min(i+100, len(vendors))}/{len(vendors)} vendors to cloud")
                time.sleep(0.1)
            
            logger.info("✅ Successfully imported all entities to cloud database")
    except Exception as e:
        logger.error(f"❌ Failed to import entities: {e}")

def import_all_relationships(cloud_driver, drug_target_rels, drug_indication_rels, drug_disease_rels, drug_vendor_rels):
    """Import all relationship types to cloud database"""
    try:
        with cloud_driver.session(database=CLOUD_DATABASE) as session:
            # Import drug-target relationships
            for i in range(0, len(drug_target_rels), 50):
                batch = drug_target_rels[i:i+50]
                session.run("""
                    UNWIND $relationships as rel
                    MATCH (d:Drug {name: rel.drug})
                    MATCH (t:Target {name: rel.target})
                    CREATE (d)-[:TARGETS]->(t)
                """, relationships=batch)
                logger.info(f"🔗 Imported {min(i+50, len(drug_target_rels))}/{len(drug_target_rels)} drug-target relationships")
                time.sleep(0.2)
            
            # Import drug-indication relationships
            for i in range(0, len(drug_indication_rels), 50):
                batch = drug_indication_rels[i:i+50]
                session.run("""
                    UNWIND $relationships as rel
                    MATCH (d:Drug {name: rel.drug})
                    MATCH (i:Indication {name: rel.indication})
                    CREATE (d)-[:TREATS]->(i)
                """, relationships=batch)
                logger.info(f"🔗 Imported {min(i+50, len(drug_indication_rels))}/{len(drug_indication_rels)} drug-indication relationships")
                time.sleep(0.2)
            
            # Import drug-disease area relationships
            for i in range(0, len(drug_disease_rels), 50):
                batch = drug_disease_rels[i:i+50]
                session.run("""
                    UNWIND $relationships as rel
                    MATCH (d:Drug {name: rel.drug})
                    MATCH (da:DiseaseArea {name: rel.disease_area})
                    CREATE (d)-[:BELONGS_TO]->(da)
                """, relationships=batch)
                logger.info(f"🔗 Imported {min(i+50, len(drug_disease_rels))}/{len(drug_disease_rels)} drug-disease area relationships")
                time.sleep(0.2)
            
            # Import drug-vendor relationships
            for i in range(0, len(drug_vendor_rels), 50):
                batch = drug_vendor_rels[i:i+50]
                session.run("""
                    UNWIND $relationships as rel
                    MATCH (d:Drug {name: rel.drug})
                    MATCH (v:Vendor {name: rel.vendor})
                    CREATE (d)-[:SUPPLIED_BY]->(v)
                """, relationships=batch)
                logger.info(f"🔗 Imported {min(i+50, len(drug_vendor_rels))}/{len(drug_vendor_rels)} drug-vendor relationships")
                time.sleep(0.2)
            
            logger.info("✅ Successfully imported all relationships to cloud database")
    except Exception as e:
        logger.error(f"❌ Failed to import relationships: {e}")

def verify_enhanced_transfer(cloud_driver):
    """Verify the enhanced data transfer was successful"""
    try:
        with cloud_driver.session(database=CLOUD_DATABASE) as session:
            # Count all node types
            drug_count = session.run("MATCH (d:Drug) RETURN count(d) as count").single()["count"]
            target_count = session.run("MATCH (t:Target) RETURN count(t) as count").single()["count"]
            disease_area_count = session.run("MATCH (da:DiseaseArea) RETURN count(da) as count").single()["count"]
            indication_count = session.run("MATCH (i:Indication) RETURN count(i) as count").single()["count"]
            vendor_count = session.run("MATCH (v:Vendor) RETURN count(v) as count").single()["count"]
            
            # Count all relationship types
            drug_target_rel_count = session.run("MATCH ()-[r:TARGETS]->() RETURN count(r) as count").single()["count"]
            drug_indication_rel_count = session.run("MATCH ()-[r:TREATS]->() RETURN count(r) as count").single()["count"]
            drug_disease_rel_count = session.run("MATCH ()-[r:BELONGS_TO]->() RETURN count(r) as count").single()["count"]
            drug_vendor_rel_count = session.run("MATCH ()-[r:SUPPLIED_BY]->() RETURN count(r) as count").single()["count"]
            
            logger.info(f"✅ Enhanced cloud database verification:")
            logger.info(f"   📊 Drugs: {drug_count}")
            logger.info(f"   🎯 Targets: {target_count}")
            logger.info(f"   🏥 Disease Areas: {disease_area_count}")
            logger.info(f"   💊 Indications: {indication_count}")
            logger.info(f"   🏪 Vendors: {vendor_count}")
            logger.info(f"   🔗 Drug-Target Relationships: {drug_target_rel_count}")
            logger.info(f"   🔗 Drug-Indication Relationships: {drug_indication_rel_count}")
            logger.info(f"   🔗 Drug-Disease Area Relationships: {drug_disease_rel_count}")
            logger.info(f"   🔗 Drug-Vendor Relationships: {drug_vendor_rel_count}")
            
            return (drug_count, target_count, disease_area_count, indication_count, vendor_count,
                   drug_target_rel_count, drug_indication_rel_count, drug_disease_rel_count, drug_vendor_rel_count)
    except Exception as e:
        logger.error(f"❌ Failed to verify transfer: {e}")
        return (0, 0, 0, 0, 0, 0, 0, 0, 0)

def main():
    """Main enhanced transfer function"""
    logger.info("🚀 Starting enhanced data transfer from local to cloud database...")
    
    # Connect to databases
    local_driver, cloud_driver = connect_to_databases()
    if not local_driver or not cloud_driver:
        logger.error("❌ Database connection failed. Exiting.")
        return
    
    try:
        # Step 1: Clear cloud database
        logger.info("🗑️ Clearing cloud database...")
        clear_cloud_database(cloud_driver)
        
        # Step 2: Export enhanced data from local database
        logger.info("📤 Exporting enhanced data from local database...")
        drugs = export_enhanced_drugs(local_driver)
        targets, disease_areas, indications, vendors = export_all_entities(local_driver)
        drug_target_rels, drug_indication_rels, drug_disease_rels, drug_vendor_rels = export_all_relationships(local_driver)
        
        if not drugs:
            logger.error("❌ Failed to export data. Exiting.")
            return
        
        # Step 3: Import enhanced data to cloud database
        logger.info("📥 Importing enhanced data to cloud database...")
        import_enhanced_drugs(cloud_driver, drugs)
        import_all_entities(cloud_driver, targets, disease_areas, indications, vendors)
        import_all_relationships(cloud_driver, drug_target_rels, drug_indication_rels, drug_disease_rels, drug_vendor_rels)
        
        # Step 4: Verify enhanced transfer
        logger.info("🔍 Verifying enhanced data transfer...")
        verify_enhanced_transfer(cloud_driver)
        
        logger.info("🎉 Enhanced data transfer completed successfully!")
        logger.info("✅ Your cloud database now has ALL enhanced features!")
        
    finally:
        # Close connections
        local_driver.close()
        cloud_driver.close()
        logger.info("🔌 Database connections closed")

if __name__ == "__main__":
    main()
