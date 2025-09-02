#!/usr/bin/env python3
"""
Setup script for Drug-Target Graph Database
"""

import os
import sys
import subprocess
import getpass

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_dependencies():
    """Install required Python packages"""
    print("\nInstalling Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing dependencies: {e}")
        sys.exit(1)

def create_env_file():
    """Create .env file with Neo4j configuration"""
    print("\nConfiguring Neo4j connection...")
    
    # Check if .env file already exists
    if os.path.exists('.env'):
        overwrite = input("A .env file already exists. Overwrite? (y/n): ").lower()
        if overwrite != 'y':
            print("Skipping .env file creation")
            return
    
    # Get Neo4j connection details
    print("Please provide your Neo4j connection details:")
    uri = input("Neo4j URI (default: bolt://localhost:7687): ").strip()
    if not uri:
        uri = "bolt://localhost:7687"
    
    user = input("Neo4j username (default: neo4j): ").strip()
    if not user:
        user = "neo4j"
    
    password = getpass.getpass("Neo4j password: ")
    if not password:
        print("Warning: No password provided")
    
    # Create .env file
    env_content = f"""# Neo4j Database Configuration
NEO4J_URI={uri}
NEO4J_USER={user}
NEO4J_PASSWORD={password}

# Logging configuration
LOG_LEVEL=INFO
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✓ .env file created successfully")

def update_data_file_path():
    """Update the data file path in config.py"""
    print("\nConfiguring data file path...")
    
    current_path = r"C:\Users\saad.waseem\Downloads\Repurposing_Hub_export.txt"
    new_path = input(f"Drug data file path (default: {current_path}): ").strip()
    
    if not new_path:
        new_path = current_path
    
    # Update config.py
    try:
        with open('config.py', 'r') as f:
            content = f.read()
        
        # Replace the data file path
        import re
        content = re.sub(
            r'DRUG_DATA_FILE = r".*"',
            f'DRUG_DATA_FILE = r"{new_path}"',
            content
        )
        
        with open('config.py', 'w') as f:
            f.write(content)
        
        print(f"✓ Data file path updated to: {new_path}")
    except Exception as e:
        print(f"✗ Error updating config.py: {e}")

def test_neo4j_connection():
    """Test the Neo4j connection"""
    print("\nTesting Neo4j connection...")
    
    try:
        from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
        from neo4j import GraphDatabase
        
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        # Test connection
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            result.single()
        
        driver.close()
        print("✓ Neo4j connection successful")
        return True
    except Exception as e:
        print(f"✗ Neo4j connection failed: {e}")
        print("Please check your Neo4j credentials and ensure Neo4j is running")
        return False

def main():
    """Main setup function"""
    print("=" * 50)
    print("Drug-Target Graph Database Setup")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Install dependencies
    install_dependencies()
    
    # Create .env file
    create_env_file()
    
    # Update data file path
    update_data_file_path()
    
    # Test Neo4j connection
    connection_success = test_neo4j_connection()
    
    print("\n" + "=" * 50)
    print("Setup Complete!")
    print("=" * 50)
    
    if connection_success:
        print("\nNext steps:")
        print("1. Run 'python drug_target_graph.py' to build the graph database")
        print("2. Run 'python query_interface.py' to explore the graph")
    else:
        print("\nSetup completed with warnings:")
        print("- Neo4j connection failed. Please check your configuration")
        print("- You can still run the scripts once Neo4j is properly configured")
    
    print("\nFor more information, see README.md")

if __name__ == "__main__":
    main()
