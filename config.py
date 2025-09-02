import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Neo4j Database Configuration
NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://127.0.0.1:7687')
NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', '11223344')
NEO4J_DATABASE = os.getenv('NEO4J_DATABASE', 'neo4j')  # Specify the database name

# Data file path
DRUG_DATA_FILE = r"C:\Users\saad.waseem\Downloads\Repurposing_Hub_export.txt"

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
