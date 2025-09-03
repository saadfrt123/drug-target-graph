#!/usr/bin/env python3
"""
Transfer data from local Neo4j to Neo4j Aura cloud database
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

def export_drugs(local_driver):
    """Export drugs from local database"""
    try:
        with local_driver.session(database=LOCAL_DATABASE) as session:
            result = session.run("""
                MATCH (d:Drug)
                RETURN d.name as name, d.moa as moa, d.phase as phase
                ORDER BY d.name
            """)
            drugs = result.data()
            logger.info(f"📊 Exported {len(drugs)} drugs from local database")
            return drugs
    except Exception as e:
        logger.error(f"❌ Failed to export drugs: {e}")
        return []

def export_targets(local_driver):
    """Export targets from local database"""
    try:
        with local_driver.session(database=LOCAL_DATABASE) as session:
            result = session.run("""
                MATCH (t:Target)
                RETURN DISTINCT t.name as name
                ORDER BY t.name
            """)
            targets = result.data()
            logger.info(f"🎯 Exported {len(targets)} targets from local database")
            return targets
    except Exception as e:
        logger.error(f"❌ Failed to export targets: {e}")
        return []

def export_relationships(local_driver):
    """Export drug-target relationships from local database"""
    try:
        with local_driver.session(database=LOCAL_DATABASE) as session:
            result = session.run("""
                MATCH (d:Drug)-[:TARGETS]->(t:Target)
                RETURN d.name as drug, t.name as target
                ORDER BY d.name, t.name
            """)
            relationships = result.data()
            logger.info(f"🔗 Exported {len(relationships)} relationships from local database")
            return relationships
    except Exception as e:
        logger.error(f"❌ Failed to export relationships: {e}")
        return []

def import_drugs(cloud_driver, drugs):
    """Import drugs to cloud database"""
    try:
        with cloud_driver.session(database=CLOUD_DATABASE) as session:
            # Batch create drugs
            for i in range(0, len(drugs), 100):  # Process in batches of 100
                batch = drugs[i:i+100]
                session.run("""
                    UNWIND $drugs as drug
                    CREATE (d:Drug {
                        name: drug.name, 
                        moa: drug.moa, 
                        phase: drug.phase
                    })
                """, drugs=batch)
                logger.info(f"📊 Imported {min(i+100, len(drugs))}/{len(drugs)} drugs to cloud")
                time.sleep(0.1)  # Small delay to avoid overwhelming the cloud DB
            
            logger.info(f"✅ Successfully imported {len(drugs)} drugs to cloud database")
    except Exception as e:
        logger.error(f"❌ Failed to import drugs: {e}")

def import_targets(cloud_driver, targets):
    """Import targets to cloud database"""
    try:
        with cloud_driver.session(database=CLOUD_DATABASE) as session:
            # Batch create targets
            for i in range(0, len(targets), 100):  # Process in batches of 100
                batch = targets[i:i+100]
                session.run("""
                    UNWIND $targets as target
                    CREATE (t:Target {name: target.name})
                """, targets=batch)
                logger.info(f"🎯 Imported {min(i+100, len(targets))}/{len(targets)} targets to cloud")
                time.sleep(0.1)  # Small delay
            
            logger.info(f"✅ Successfully imported {len(targets)} targets to cloud database")
    except Exception as e:
        logger.error(f"❌ Failed to import targets: {e}")

def import_relationships(cloud_driver, relationships):
    """Import drug-target relationships to cloud database"""
    try:
        with cloud_driver.session(database=CLOUD_DATABASE) as session:
            # Batch create relationships
            for i in range(0, len(relationships), 50):  # Smaller batches for relationships
                batch = relationships[i:i+50]
                session.run("""
                    UNWIND $relationships as rel
                    MATCH (d:Drug {name: rel.drug})
                    MATCH (t:Target {name: rel.target})
                    CREATE (d)-[:TARGETS]->(t)
                """, relationships=batch)
                logger.info(f"🔗 Imported {min(i+50, len(relationships))}/{len(relationships)} relationships to cloud")
                time.sleep(0.2)  # Slightly longer delay for relationships
            
            logger.info(f"✅ Successfully imported {len(relationships)} relationships to cloud database")
    except Exception as e:
        logger.error(f"❌ Failed to import relationships: {e}")

def verify_transfer(cloud_driver):
    """Verify the data transfer was successful"""
    try:
        with cloud_driver.session(database=CLOUD_DATABASE) as session:
            # Count drugs
            drug_count = session.run("MATCH (d:Drug) RETURN count(d) as count").single()["count"]
            
            # Count targets
            target_count = session.run("MATCH (t:Target) RETURN count(t) as count").single()["count"]
            
            # Count relationships
            rel_count = session.run("MATCH ()-[r:TARGETS]->() RETURN count(r) as count").single()["count"]
            
            logger.info(f"✅ Cloud database verification:")
            logger.info(f"   📊 Drugs: {drug_count}")
            logger.info(f"   🎯 Targets: {target_count}")
            logger.info(f"   🔗 Relationships: {rel_count}")
            
            return drug_count, target_count, rel_count
    except Exception as e:
        logger.error(f"❌ Failed to verify transfer: {e}")
        return 0, 0, 0

def main():
    """Main transfer function"""
    logger.info("🚀 Starting data transfer from local to cloud database...")
    
    # Connect to databases
    local_driver, cloud_driver = connect_to_databases()
    if not local_driver or not cloud_driver:
        logger.error("❌ Database connection failed. Exiting.")
        return
    
    try:
        # Step 1: Clear cloud database
        logger.info("🗑️ Clearing cloud database...")
        clear_cloud_database(cloud_driver)
        
        # Step 2: Export data from local database
        logger.info("📤 Exporting data from local database...")
        drugs = export_drugs(local_driver)
        targets = export_targets(local_driver)
        relationships = export_relationships(local_driver)
        
        if not drugs or not targets or not relationships:
            logger.error("❌ Failed to export data. Exiting.")
            return
        
        # Step 3: Import data to cloud database
        logger.info("📥 Importing data to cloud database...")
        import_drugs(cloud_driver, drugs)
        import_targets(cloud_driver, targets)
        import_relationships(cloud_driver, relationships)
        
        # Step 4: Verify transfer
        logger.info("🔍 Verifying data transfer...")
        drug_count, target_count, rel_count = verify_transfer(cloud_driver)
        
        if drug_count > 0 and target_count > 0 and rel_count > 0:
            logger.info("🎉 Data transfer completed successfully!")
            logger.info("✅ Your cloud database is now ready for demos!")
        else:
            logger.error("❌ Data transfer verification failed.")
        
    finally:
        # Close connections
        local_driver.close()
        cloud_driver.close()
        logger.info("🔌 Database connections closed")

if __name__ == "__main__":
    main()
