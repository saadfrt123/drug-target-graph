#!/usr/bin/env python3
"""
Simple test script to verify Neo4j connection and data access
"""

from neo4j import GraphDatabase
import pandas as pd

def test_connection():
    """Test Neo4j connection and basic data access"""
    print("🔗 Testing Neo4j connection...")
    
    # Connection details
    uri = "bolt://127.0.0.1:7687"
    user = "neo4j"
    password = "11223344"
    database = "neo4j"
    
    try:
        # Create driver
        print(f"Creating driver with URI: {uri}")
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        # Test basic connection
        print("Testing basic connection...")
        with driver.session(database=database) as session:
            result = session.run("RETURN 'Hello from Neo4j!' as message")
            message = result.single()["message"]
            print(f"✅ Basic connection successful: {message}")
        
        # Test data access
        print("\n📊 Testing data access...")
        with driver.session(database=database) as session:
            # Count drugs
            drug_count = session.run("MATCH (d:Drug) RETURN count(d) as count").single()["count"]
            print(f"✅ Found {drug_count} drugs")
            
            # Count targets
            target_count = session.run("MATCH (t:Target) RETURN count(t) as count").single()["count"]
            print(f"✅ Found {target_count} targets")
            
            # Count relationships
            rel_count = session.run("MATCH ()-[r:TARGETS]->() RETURN count(r) as count").single()["count"]
            print(f"✅ Found {rel_count} relationships")
            
            # Get sample drug
            sample_drug = session.run("MATCH (d:Drug) RETURN d.name as name, d.moa as moa LIMIT 1").single()
            print(f"✅ Sample drug: {sample_drug['name']} (MOA: {sample_drug['moa']})")
            
            # Get sample target
            sample_target = session.run("MATCH (t:Target) RETURN t.name as name LIMIT 1").single()
            print(f"✅ Sample target: {sample_target['name']}")
        
        driver.close()
        print("\n🎉 All tests passed! Neo4j connection is working perfectly.")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    test_connection()
