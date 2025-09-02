#!/usr/bin/env python3
"""
Debug script to diagnose Neo4j connection issues
"""

import os
from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

def test_connection_details():
    """Test connection with detailed error reporting"""
    print("=" * 60)
    print("NEO4J CONNECTION DEBUG")
    print("=" * 60)
    
    print(f"URI: {NEO4J_URI}")
    print(f"Username: {NEO4J_USER}")
    print(f"Password: {NEO4J_PASSWORD[:8]}..." if len(NEO4J_PASSWORD) > 8 else f"Password: {NEO4J_PASSWORD}")
    
    print("\nAttempting connection...")
    
    try:
        # Try to create driver
        print("1. Creating driver...")
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        print("   ✓ Driver created successfully")
        
        # Try to verify connection
        print("2. Verifying connection...")
        driver.verify_connectivity()
        print("   ✓ Connection verified successfully")
        
        # Try to run a simple query
        print("3. Running test query...")
        with driver.session() as session:
            result = session.run("RETURN 'Connection successful!' as message")
            message = result.single()["message"]
            print(f"   ✓ Query executed: {message}")
        
        driver.close()
        print("\n🎉 All connection tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Connection failed: {type(e).__name__}: {e}")
        
        # Provide specific troubleshooting advice
        if "Unauthorized" in str(e):
            print("\n🔍 AUTHENTICATION ISSUE DETECTED")
            print("Possible solutions:")
            print("1. Check if the password is correct")
            print("2. Verify the username is 'neo4j'")
            print("3. Make sure the database is started in Neo4j Desktop")
            print("4. Try resetting the password in Neo4j Desktop")
            
        elif "Connection refused" in str(e):
            print("\n🔍 CONNECTION REFUSED")
            print("Possible solutions:")
            print("1. Make sure Neo4j Desktop is running")
            print("2. Check that your database is started")
            print("3. Verify the port number (7687)")
            
        elif "Name or service not known" in str(e):
            print("\n🔍 HOSTNAME ISSUE")
            print("Try changing the URI to:")
            print("- bolt://localhost:7687")
            print("- bolt://127.0.0.1:7687")
            
        return False

def test_alternative_uris():
    """Test alternative URI formats"""
    print("\n" + "=" * 60)
    print("TESTING ALTERNATIVE URI FORMATS")
    print("=" * 60)
    
    alternative_uris = [
        "bolt://localhost:7687",
        "bolt://127.0.0.1:7687",
        "neo4j://localhost:7687",
        "neo4j://127.0.0.1:7687"
    ]
    
    for uri in alternative_uris:
        print(f"\nTesting URI: {uri}")
        try:
            driver = GraphDatabase.driver(uri, auth=(NEO4J_USER, NEO4J_PASSWORD))
            driver.verify_connectivity()
            print(f"   ✓ SUCCESS with {uri}")
            driver.close()
            return uri
        except Exception as e:
            print(f"   ✗ Failed: {type(e).__name__}")
    
    return None

def main():
    """Main debug function"""
    # Test with current configuration
    success = test_connection_details()
    
    if not success:
        # Try alternative URIs
        working_uri = test_alternative_uris()
        
        if working_uri:
            print(f"\n🎉 Found working URI: {working_uri}")
            print("Update your config.py with this URI:")
            print(f"NEO4J_URI = os.getenv('NEO4J_URI', '{working_uri}')")
        else:
            print("\n❌ No working connection found")
            print("\nPlease check:")
            print("1. Neo4j Desktop is running")
            print("2. Database is started")
            print("3. Password is correct")
            print("4. Try opening Neo4j Browser to test login manually")

if __name__ == "__main__":
    main()
