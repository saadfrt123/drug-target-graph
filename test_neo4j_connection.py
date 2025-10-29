#!/usr/bin/env python3
"""
Simple Neo4j connection test
"""
from neo4j import GraphDatabase
import sys

# Test different common URIs
test_configs = [
    {"uri": "bolt://127.0.0.1:7687", "user": "neo4j", "password": "11223344"},
    {"uri": "bolt://localhost:7687", "user": "neo4j", "password": "11223344"},
    {"uri": "neo4j://localhost:7687", "user": "neo4j", "password": "11223344"},
    {"uri": "bolt://127.0.0.1:7688", "user": "neo4j", "password": "11223344"},
]

print("Testing Neo4j connections...\n")

for i, config in enumerate(test_configs, 1):
    print(f"Test {i}: {config['uri']}")
    try:
        driver = GraphDatabase.driver(config['uri'], auth=(config['user'], config['password']))
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            value = result.single()["test"]
            if value == 1:
                print(f"  ✅ SUCCESS! Neo4j is running at {config['uri']}")
                print(f"     User: {config['user']}")
                print(f"     Password: {config['password']}")
                
                # Test a query
                db_count = session.run("MATCH (n) RETURN count(n) as count").single()["count"]
                print(f"     Total nodes in database: {db_count}")
                
                driver.close()
                
                print(f"\n✅ WORKING CONFIGURATION FOUND!")
                print(f"\nUpdate your .env file with:")
                print(f"NEO4J_URI={config['uri']}")
                print(f"NEO4J_USER={config['user']}")
                print(f"NEO4J_PASSWORD={config['password']}")
                sys.exit(0)
    except Exception as e:
        print(f"  ❌ Failed: {str(e)[:100]}")
    print()

print("❌ No working Neo4j connection found!")
print("\nPlease:")
print("1. Open Neo4j Desktop")
print("2. Start your database")
print("3. Check the Bolt URL in database details")
print("4. Verify password is: 11223344")
print("5. Run this test again")


