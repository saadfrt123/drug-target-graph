#!/usr/bin/env python3
"""
Test script to verify Neo4j connection and data file access
"""

import os
import pandas as pd
from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE, DRUG_DATA_FILE

def test_neo4j_connection():
    """Test Neo4j database connection"""
    print("Testing Neo4j connection...")
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        # Test connection
        with driver.session(database=NEO4J_DATABASE) as session:
            result = session.run("RETURN 'Hello from Neo4j!' as message")
            message = result.single()["message"]
            print(f"✓ Neo4j connection successful: {message}")
        
        driver.close()
        return True
    except Exception as e:
        print(f"✗ Neo4j connection failed: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure Neo4j Desktop is running")
        print("2. Check that your database is started")
        print("3. Verify your password in config.py")
        print("4. Ensure the URI is correct (usually bolt://localhost:7687)")
        return False

def test_data_file():
    """Test data file access"""
    print("\nTesting data file access...")
    try:
        if not os.path.exists(DRUG_DATA_FILE):
            print(f"✗ Data file not found: {DRUG_DATA_FILE}")
            return False
        
        # Try to read the first few lines
        df = pd.read_csv(DRUG_DATA_FILE, sep='\t', encoding='utf-8', nrows=5)
        print(f"✓ Data file accessible: {DRUG_DATA_FILE}")
        print(f"✓ File contains {len(df)} sample rows")
        print(f"✓ Columns: {list(df.columns)}")
        
        # Show sample data
        print("\nSample data:")
        print(df.head())
        
        return True
    except Exception as e:
        print(f"✗ Data file access failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("DRUG-TARGET GRAPH SETUP TEST")
    print("=" * 50)
    
    # Test Neo4j connection
    neo4j_ok = test_neo4j_connection()
    
    # Test data file
    data_ok = test_data_file()
    
    print("\n" + "=" * 50)
    print("TEST RESULTS")
    print("=" * 50)
    
    if neo4j_ok and data_ok:
        print("🎉 All tests passed! You're ready to build the graph database.")
        print("\nNext steps:")
        print("1. Run: python drug_target_graph.py")
        print("2. Then: python query_interface.py")
    else:
        print("❌ Some tests failed. Please fix the issues above before proceeding.")
        
        if not neo4j_ok:
            print("\nTo fix Neo4j connection:")
            print("1. Open Neo4j Desktop")
            print("2. Start your database")
            print("3. Update the password in config.py")
            
        if not data_ok:
            print("\nTo fix data file access:")
            print("1. Check that the file path in config.py is correct")
            print("2. Ensure the file exists and is readable")

if __name__ == "__main__":
    main()
