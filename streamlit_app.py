import streamlit as st

import pandas as pd

import plotly.express as px

import plotly.graph_objects as go

from neo4j import GraphDatabase

import logging

import numpy as np

import math

import os

import json

import hashlib

import pickle

import threading

import time

from typing import List, Dict, Any



# Cache management for fast network interactions
CACHE_DIR = "network_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def get_cache_key(drug_name: str, target_name: str = None) -> str:
    """Generate a unique cache key for drug-target classification"""
    if target_name:
        return hashlib.md5(f"{drug_name}_{target_name}".encode()).hexdigest()
    return hashlib.md5(f"drug_{drug_name}".encode()).hexdigest()

def save_to_cache(key: str, data: Any) -> None:
    """Save data to cache file"""
    try:
        cache_file = os.path.join(CACHE_DIR, f"{key}.pkl")
        with open(cache_file, 'wb') as f:
            pickle.dump(data, f)
    except Exception as e:
        st.error(f"Error saving to cache: {e}")

def load_from_cache(key: str) -> Any:
    """Load data from cache file"""
    try:
        cache_file = os.path.join(CACHE_DIR, f"{key}.pkl")
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
    except Exception as e:
        st.error(f"Error loading from cache: {e}")
    return None

def is_cached(key: str) -> bool:
    """Check if data is cached"""
    cache_file = os.path.join(CACHE_DIR, f"{key}.pkl")
    return os.path.exists(cache_file)

# Force light theme

st.set_page_config(

    page_title="Drug-Target Graph Database",

    page_icon="💊",

    layout="wide",

    initial_sidebar_state="expanded",

    menu_items={

        'Get Help': 'https://github.com',

        'Report a bug': "https://github.com",

        'About': "# Drug-Target Graph Database\nExplore drug-target interactions!"

    }

)



# Load environment variables from .env file (optional)

try:

    from dotenv import load_dotenv

    import os

    if os.path.exists('.env'):

        load_dotenv('.env', encoding='utf-8')

except (ImportError, FileNotFoundError, UnicodeDecodeError, Exception):

    pass  # dotenv not available, .env file missing/corrupted, or other issues - use fallback



# Try to import chemical visualization libraries

try:

    from rdkit import Chem

    from rdkit.Chem import AllChem, Descriptors

    import stmol

    RDKIT_AVAILABLE = True

except ImportError as e:

    RDKIT_AVAILABLE = False

    RDKIT_ERROR = str(e)

from typing import List, Dict, Any, Optional

import os

import networkx as nx

import numpy as np

from collections import Counter

import plotly.graph_objects as go

from plotly.subplots import make_subplots



# Import mechanism classifier

try:

    from mechanism_classifier import DrugTargetMechanismClassifier

    CLASSIFIER_AVAILABLE = True

except ImportError:

    CLASSIFIER_AVAILABLE = False

    st.warning("Mechanism classifier not available. Install google-generativeai to enable drug-target mechanism classification.")



# Configure logging

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)



# Note: Page config was already set above. Avoid calling st.set_page_config twice.


# Custom CSS for better styling

st.markdown("""

<style>

    .main-header {

        font-size: 2.5rem;

        color: #2C3E50;

        text-align: center;

        margin-bottom: 2rem;

        font-weight: 600;

    }

    .metric-card {

        background: linear-gradient(135deg, #E8F6FF 0%, #F0F8FF 100%);

        color: #2C3E50;

        padding: 1.5rem;

        border-radius: 12px;

        border: 1px solid #E1E8ED;

        box-shadow: 0 2px 8px rgba(0,0,0,0.05);

        margin: 0.5rem 0;

    }

    .drug-card {

        background: linear-gradient(135deg, #F0FFF4 0%, #F5FFFA 100%);

        color: #2C3E50;

        padding: 1rem;

        border-radius: 10px;

        border: 1px solid #D5E8D4;

        margin: 0.5rem 0;

        box-shadow: 0 2px 6px rgba(0,0,0,0.04);

    }

    .target-card {

        background: linear-gradient(135deg, #FFF8E1 0%, #FFFDE7 100%);

        color: #2C3E50;

        padding: 1rem;

        border-radius: 10px;

        border: 1px solid #F0E68C;

        margin: 0.5rem 0;

        box-shadow: 0 2px 6px rgba(0,0,0,0.04);

    }

    .connection-form {

        background: linear-gradient(135deg, #F8F9FA 0%, #FFFFFF 100%);

        padding: 2rem;

        border-radius: 12px;

        color: #2C3E50;

        margin: 1rem 0;

        border: 1px solid #E9ECEF;

        box-shadow: 0 4px 12px rgba(0,0,0,0.05);

    }

    .stButton > button {

        border-radius: 8px;

        font-weight: 500;

        border: 1px solid #D1D5DB !important;

        background: white !important;

        color: #374151 !important;

        transition: all 0.2s;

    }

    .stButton > button:hover {

        background: #F9FAFB !important;

        border-color: #9CA3AF !important;

        color: #374151 !important;

    }

    

    /* Fix all button styling */

    button {

        background-color: #ffffff !important;

        color: #1a1a1a !important;

        border: 1px solid #cccccc !important;

    }

    

    button:hover {

        background-color: #f0f0f0 !important;

        color: #1a1a1a !important;

    }

    .network-graph {

        border: 1px solid #E5E7EB;

        border-radius: 12px;

        padding: 1rem;

        background: #FAFAFA;

    }

    .analytics-card {

        background: linear-gradient(135deg, #F0F9FF 0%, #E0F2FE 100%);

        color: #0F172A;

        padding: 1.5rem;

        border-radius: 12px;

        border: 1px solid #BAE6FD;

        box-shadow: 0 2px 8px rgba(0,0,0,0.04);

        margin: 0.5rem 0;

    }

    .insight-card {

        background: linear-gradient(135deg, #FEF7FF 0%, #FAF5FF 100%);

        color: #1F2937;

        padding: 1.5rem;

        border-radius: 12px;

        border: 1px solid #E9D5FF;

        box-shadow: 0 2px 8px rgba(0,0,0,0.04);

        margin: 0.5rem 0;

    }

    /* Overall app background */

    .stApp {

        background-color: #FFFFFF;

    }

    

    /* Sidebar styling */

    .css-1d391kg, .css-1aumxhk {

        background-color: #F8F9FA;

    }

    

    /* Main content area */

    .main .block-container {

        padding-top: 2rem;

        background-color: #FFFFFF;

    }

    

    /* Force light background for all containers */

    .css-1kyxreq, .css-12oz5g7, .css-1v3fvcr {

        background-color: #FFFFFF;

    }

    

    /* Streamlit containers */

    .css-1avcm0n {

        background-color: #FFFFFF;

    }

    

    /* Header area */

    .css-18e3th9 {

        background-color: #FFFFFF;

    }

    

    /* Force white background for all elements */

    div[data-testid="stAppViewContainer"] {

        background-color: #FFFFFF;

    }

    

    /* Sidebar background */

    section[data-testid="stSidebar"] {

        background-color: #F8F9FA;

    }

    

    /* Main content background */

    div[data-testid="stAppViewContainer"] > div:first-child {

        background-color: #FFFFFF;

    }

    

    /* Ensure all text is dark and readable */

    .css-1d391kg, .css-1aumxhk, .main, .stMarkdown, .stText, p, div, span, h1, h2, h3, h4, h5, h6 {

        color: #1a1a1a !important;

    }

    

    /* Force dark text for all Streamlit elements */

    .stMarkdown, .stMarkdown * {

        color: #1a1a1a !important;

    }

    

    /* Input labels and text */

    .stTextInput label, .stSelectbox label, .stButton button {

        color: #1a1a1a !important;

    }

    

    /* Sidebar text */

    .css-1d391kg *, section[data-testid="stSidebar"] * {

        color: #1a1a1a !important;

    }

    

    /* Connection form text */

    .connection-form * {

        color: #1a1a1a !important;

    }

    

    /* All text inputs and labels */

    [data-testid="stTextInput"] *, [data-testid="stSelectbox"] *, [data-testid="stButton"] * {

        color: #1a1a1a !important;

    }

    

    /* Force text contrast */

    * {

        color: #1a1a1a !important;

    }

    

    /* Override any white text */

    .css-1avcm0n *, .css-18e3th9 *, .css-1kyxreq *, .css-12oz5g7 *, .css-1v3fvcr * {

        color: #1a1a1a !important;

    }

    

    /* Fix selectbox styling */

    .stSelectbox > div > div {

        background-color: #ffffff !important;

        color: #1a1a1a !important;

        border: 1px solid #cccccc !important;

    }

    

    /* Selectbox options dropdown */

    .stSelectbox > div > div > div {

        background-color: #ffffff !important;

        color: #1a1a1a !important;

    }

    

    /* Selectbox arrow and text */

    .stSelectbox [data-baseweb="select"] {

        background-color: #ffffff !important;

        color: #1a1a1a !important;

    }

    

    /* Dropdown menu */

    .stSelectbox [role="listbox"] {

        background-color: #ffffff !important;

        color: #1a1a1a !important;

    }

    

    /* Individual dropdown options */

    .stSelectbox [role="option"] {

        background-color: #ffffff !important;

        color: #1a1a1a !important;

    }

    

    /* Dropdown option hover */

    .stSelectbox [role="option"]:hover {

        background-color: #f0f0f0 !important;

        color: #1a1a1a !important;

    }

    

    /* More specific selectbox targeting */

    div[data-testid="stSelectbox"] {

        background-color: #ffffff !important;

        color: #1a1a1a !important;

    }

    

    div[data-testid="stSelectbox"] * {

        background-color: #ffffff !important;

        color: #1a1a1a !important;

    }

    

    /* BaseWeb select component */

    [data-baseweb="select"] * {

        background-color: #ffffff !important;

        color: #1a1a1a !important;

    }

    

    /* Popover/dropdown container */

    [data-baseweb="popover"] {

        background-color: #ffffff !important;

    }

    

    [data-baseweb="popover"] * {

        background-color: #ffffff !important;

        color: #1a1a1a !important;

    }

    

    /* Menu items */

    [data-baseweb="menu"] {

        background-color: #ffffff !important;

    }

    

    [data-baseweb="menu"] * {

        background-color: #ffffff !important;

        color: #1a1a1a !important;

    }

    

    /* Fix text input fields */

    .stTextInput > div > div > input {

        background-color: #ffffff !important;

        color: #1a1a1a !important;

        border: 1px solid #cccccc !important;

    }

    

    /* Text input container */

    .stTextInput {

        background-color: transparent !important;

    }

    

    /* Text input field */

    input[type="text"] {

        background-color: #ffffff !important;

        color: #1a1a1a !important;

        border: 1px solid #cccccc !important;

    }

    

    /* All input elements */

    input {

        background-color: #ffffff !important;

        color: #1a1a1a !important;

        border: 1px solid #cccccc !important;

    }

    

    /* Text input data-testid */

    div[data-testid="stTextInput"] input {

        background-color: #ffffff !important;

        color: #1a1a1a !important;

        border: 1px solid #cccccc !important;

    }

    

    /* BaseWeb input components */

    [data-baseweb="input"] {

        background-color: #ffffff !important;

        color: #1a1a1a !important;

    }

    

    [data-baseweb="input"] * {

        background-color: #ffffff !important;

        color: #1a1a1a !important;

    }

    

    /* Fix dataframe/table styling */

    .stDataFrame, .stDataFrame table {

        background-color: #ffffff !important;

        color: #1a1a1a !important;

    }

    

    .stDataFrame th, .stDataFrame td {

        background-color: #ffffff !important;

        color: #1a1a1a !important;

        border-color: #e0e0e0 !important;

    }

    

    /* Fix table headers */

    .stDataFrame thead th {

        background-color: #f8f9fa !important;

        color: #1a1a1a !important;

        font-weight: bold !important;

    }

    

    /* Fix success/info/warning message styling */

    .stSuccess, .stInfo, .stWarning, .stError {

        color: #1a1a1a !important;

    }

    

    .stSuccess > div, .stInfo > div, .stWarning > div, .stError > div {

        color: #1a1a1a !important;

    }

    

    /* Fix alert text */

    [data-testid="stAlert"] {

        color: #1a1a1a !important;

    }

    

    [data-testid="stAlert"] * {

        color: #1a1a1a !important;

    }

    

    /* Fix all table elements */

    table, thead, tbody, tr, th, td {

        background-color: #ffffff !important;

        color: #1a1a1a !important;

    }

    

    /* Streamlit specific table fixes */

    div[data-testid="stDataFrame"] {

        background-color: #ffffff !important;

        color: #1a1a1a !important;

    }

    

    div[data-testid="stDataFrame"] * {

        background-color: #ffffff !important;

        color: #1a1a1a !important;

    }

    

    /* Fix markdown tables */

    .streamlit-expanderContent table {

        background-color: #ffffff !important;

        color: #1a1a1a !important;

    }

    

    .streamlit-expanderContent table th,

    .streamlit-expanderContent table td {

        background-color: #ffffff !important;

        color: #1a1a1a !important;

    }

    

    /* Fix all message containers */

    .element-container {

        background-color: transparent !important;

    }

    

    /* Force all text elements to be dark */

    .markdown-text-container {

        color: #1a1a1a !important;

    }

    

    /* Fix any remaining light text */

    .css-1e5imcs, .css-1h6y0x9, .css-fg4pbf {

        color: #1a1a1a !important;

    }

    @media (max-width: 768px) {

        .main-header {

            font-size: 2rem;

        }

        .metric-card, .drug-card, .target-card {

            margin: 0.25rem 0;

            padding: 1rem;

        }

    }

    

    /* Enhanced table visibility for ALL tables including Similar Drugs */

    .dataframe, .dataframe * {

        background-color: #ffffff !important;

        color: #333333 !important;

        border: 1px solid #ddd !important;

    }

    

    /* All Streamlit DataFrames */

    .stDataFrame .dataframe,

    .stDataFrame .dataframe * {

        background-color: #ffffff !important;

        color: #333333 !important;

    }

    

    /* Table headers with better contrast */

    .dataframe thead, .dataframe thead th,

    .stDataFrame .dataframe thead, .stDataFrame .dataframe thead th {

        background-color: #f8f9fa !important;

        color: #495057 !important;

        font-weight: bold !important;

        border: 1px solid #ddd !important;

    }

    

    /* Table body cells */

    .dataframe tbody tr td,

    .stDataFrame .dataframe tbody tr td {

        background-color: #ffffff !important;

        color: #333333 !important;

        border: 1px solid #ddd !important;

        padding: 8px 12px !important;

    }

    

    /* Alternating row colors for better readability */

    .dataframe tbody tr:nth-child(even),

    .stDataFrame .dataframe tbody tr:nth-child(even) {

        background-color: #f8f9fa !important;

    }

    

    /* Force visibility for all table types */

    [data-testid="stTable"], [data-testid="stTable"] *,

    .stTable, .stTable *,

    div[role="table"], div[role="table"] * {

        background-color: #ffffff !important;

        color: #333333 !important;

    }

    

    /* Specific targeting for Similar Drugs and other expandable content tables */

    .streamlit-expanderContent .dataframe,

    .streamlit-expanderContent .dataframe * {

        background-color: #ffffff !important;

        color: #333333 !important;

        border: 1px solid #ddd !important;

    }

    

    /* Ultra-specific targeting for stubborn table elements */

    div[data-testid="stDataFrame"] table,

    div[data-testid="stDataFrame"] table *,

    div[data-testid="stDataFrame"] tbody,

    div[data-testid="stDataFrame"] tbody *,

    div[data-testid="stDataFrame"] tr,

    div[data-testid="stDataFrame"] tr *,

    div[data-testid="stDataFrame"] td,

    div[data-testid="stDataFrame"] th {

        background-color: #ffffff !important;

        color: #333333 !important;

        border: 1px solid #e0e0e0 !important;

    }

    

    /* Force all pandas DataFrame elements to be visible */

    .dataframe tbody tr,

    .dataframe tbody tr td,

    .dataframe tbody tr th {

        background-color: #ffffff !important;

        color: #333333 !important;

        border: 1px solid #e0e0e0 !important;

        font-size: 14px !important;

    }

    

    /* Target any remaining invisible table cells */

    div[class*="dataframe"] td,

    div[class*="dataframe"] th,

    table[class*="dataframe"] td,

    table[class*="dataframe"] th {

        background-color: #ffffff !important;

        color: #333333 !important;

        padding: 8px !important;

        border: 1px solid #e0e0e0 !important;

    }

    

    /* Nuclear option - force ALL table-like elements */

    div[role="grid"],

    div[role="grid"] *,

    div[role="gridcell"],

    div[role="columnheader"],

    div[role="row"],

    div[role="row"] * {

        background-color: #ffffff !important;

        color: #333333 !important;

    }

</style>

""", unsafe_allow_html=True)



class DrugTargetGraphApp:

    def __init__(self):

        """Initialize the Streamlit app"""

        # Use session state to persist connection
        if 'driver' not in st.session_state:

            st.session_state.driver = None

        if 'database' not in st.session_state:

            st.session_state.database = None

        if 'classifier' not in st.session_state:

            st.session_state.classifier = None

        

        self.driver = st.session_state.driver

        self.database = st.session_state.database
        
        # Initialize caching and background processing
        if 'classification_cache' not in st.session_state:
            st.session_state.classification_cache = {}
        if 'background_threads' not in st.session_state:
            st.session_state.background_threads = {}
            
        self._classification_cache = st.session_state.classification_cache
        self._background_threads = st.session_state.background_threads

        self.classifier = st.session_state.classifier

        

    def connect_to_neo4j(self):

        """Connect to Neo4j database"""

        try:

            # Try to get connection details from config

            try:

                from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE

                self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

                self.database = NEO4J_DATABASE

                # Test connection

                with self.driver.session(database=self.database) as session:

                    session.run("RETURN 1").single()

                st.success("✅ Connected to Neo4j database successfully!")

                return True

            except ImportError:

                st.warning("⚠️ Config file not found. Please enter Neo4j connection details.")

                return self.get_manual_connection()

                

        except Exception as e:

            st.error(f"❌ Failed to connect to Neo4j: {e}")

            return self.get_manual_connection()

    

    def get_manual_connection(self):

        """Get manual connection details from user"""

        st.markdown('<div class="connection-form">', unsafe_allow_html=True)

        st.header("🔗 Database Connection")
        

        # Connection type selector

        connection_type = st.selectbox(

            "Choose Database:",
            ["☁️ Neo4j Aura (Cloud)", "💻 Local Database"]

        )

        

        if connection_type == "☁️ Neo4j Aura (Cloud)":

            # Pre-filled cloud connection details

            col1, col2 = st.columns(2)

            

            with col1:

                uri = st.text_input("Neo4j Aura URI", value="neo4j+s://c8287756.databases.neo4j.io")
                user = st.text_input("Username", value="neo4j")
            

            with col2:

                password = st.text_input("Password", type="password", value="bsSvDn8Kh-qVZrtwwAH2t3yhLf0pGjDKzCL8Bs5jqkM")
                database = st.text_input("Database", value="neo4j")
            

        else:

            # Local connection details

            col1, col2 = st.columns(2)

            

            with col1:

                uri = st.text_input("Neo4j URI", value="bolt://127.0.0.1:7687")
                user = st.text_input("Username", value="neo4j")
            

            with col2:

                password = st.text_input("Password", type="password", value="11223344")
                database = st.text_input("Database", value="neo4j")
        

        # Connection buttons

        col1, col2 = st.columns(2)
        

        with col1:

            if st.button("🧪 Test Connection", type="secondary"):

                with st.spinner("Testing connection..."):

                    try:

                        from neo4j import GraphDatabase, basic_auth

                        

                        if "neo4j+s://" in uri:

                            test_driver = GraphDatabase.driver(uri, auth=basic_auth(user, password))
                        else:

                            test_driver = GraphDatabase.driver(uri, auth=(user, password))

                        

                        with test_driver.session(database=database) as session:

                            result = session.run("RETURN 1 as test").single()

                            st.success("✅ Connection successful!")
                        test_driver.close()

                        

                    except Exception as e:

                        st.error(f"❌ Connection failed: {str(e)}")
        

        with col2:

            if st.button("🔗 Connect", type="primary"):

                with st.spinner("Connecting to database..."):

                    try:

                        # Create driver and test connection with proper Aura config

                        from neo4j import GraphDatabase, basic_auth

                        import time

                        

                        if "neo4j+s://" in uri:

                            st.info("🔄 Establishing secure connection to Neo4j Aura...")

                            time.sleep(2)  # Brief delay for Aura

                            test_driver = GraphDatabase.driver(uri, auth=basic_auth(user, password))
                        else:

                            test_driver = GraphDatabase.driver(uri, auth=(user, password))

                        

                        with test_driver.session(database=database) as session:

                            session.run("RETURN 1").single()

                        

                        # If successful, store in session state

                        st.session_state.driver = test_driver

                        st.session_state.database = database

                        st.session_state.neo4j_uri = uri

                        st.session_state.neo4j_user = user

                        st.session_state.neo4j_password = password

                        st.session_state.neo4j_database = database

                        

                        # Update instance variables

                        self.driver = test_driver

                        self.database = database

                        

                        # Initialize classifier if available

                        self.initialize_classifier(uri, user, password, database)

                        

                        st.success("✅ Connected successfully!")

                        st.rerun()

                        return True

                        

                    except Exception as e:

                        error_msg = str(e)

                        st.error(f"❌ Connection failed: {error_msg}")

                        

                        # Provide specific help based on error type

                        if "Cannot resolve address" in error_msg:

                            st.warning("""

                            🔧 **DNS Resolution Issue:**

                            - Your Neo4j Aura instance might be starting up (wait 60+ seconds)

                            - Try refreshing the page and connecting again

                            - Verify the instance is running at https://console.neo4j.io

                            """)

                            st.info("💡 **Quick Fix:** Try switching to 'Local' connection temporarily if you have local Neo4j running")

                        elif "authentication" in error_msg.lower():

                            st.warning("🔑 **Authentication Issue:** Double-check your Aura password")

                        elif "ServiceUnavailable" in error_msg:

                            st.warning("🚫 **Service Issue:** The Aura instance might be paused or starting up")

                        return False

        

        

        st.markdown('</div>', unsafe_allow_html=True)

        return False

    

    def get_graph_statistics(self) -> Dict[str, Any]:

        """Get basic statistics about the graph"""

        if not self.driver:

            return None

            

        try:

            with self.driver.session(database=self.database) as session:

                # Count nodes

                drug_count = session.run("MATCH (d:Drug) RETURN count(d) as count").single()["count"]

                target_count = session.run("MATCH (t:Target) RETURN count(t) as count").single()["count"]

                relationship_count = session.run("MATCH ()-[r:TARGETS]->() RETURN count(r) as count").single()["count"]

                

                return {

                    "drug_count": drug_count,

                    "target_count": target_count,

                    "relationship_count": relationship_count

                }

        except Exception as e:

            st.error(f"Error getting statistics: {e}")

            return None

    

    def get_network_data(self, limit: int = 50) -> Dict[str, Any]:

        """Get network data for visualization with mechanism information"""

        if not self.driver:

            return None

            

        try:

            with self.driver.session(database=self.database) as session:

                # Get sample drugs and their targets with mechanism details

                result = session.run("""

                    MATCH (d:Drug)-[r:TARGETS]->(t:Target)

                    RETURN d.name as drug, d.moa as moa, d.phase as phase, 

                           t.name as target, count(t) as target_count,

                           r.mechanism as mechanism,

                           r.relationship_type as relationship_type,

                           r.target_class as target_class,

                           r.confidence as confidence,

                           r.classified as is_classified

                    ORDER BY target_count DESC

                    LIMIT $limit

                """, limit=limit)

                

                data = result.data()

                

                # Create nodes and edges for network

                nodes = []

                edges = []

                drug_ids = {}

                target_ids = {}

                

                for i, record in enumerate(data):

                    drug_name = record['drug']

                    target_name = record['target']

                    

                    # Add drug node if not exists

                    if drug_name not in drug_ids:

                        drug_ids[drug_name] = len(nodes)

                        nodes.append({

                            'id': len(nodes),

                            'label': drug_name,

                            'type': 'drug',

                            'moa': record['moa'],

                            'phase': record['phase']

                        })

                    

                    # Add target node if not exists

                    if target_name not in target_ids:

                        target_ids[target_name] = len(nodes)

                        nodes.append({

                            'id': len(nodes),

                            'label': target_name,

                            'type': 'target'

                        })

                    

                    # Add edge

                    edges.append({

                        'source': drug_ids[drug_name],

                        'target': target_ids[target_name],

                        'type': 'targets'

                    })

                

                return {

                    'nodes': nodes,

                    'edges': edges,

                    'drug_ids': drug_ids,

                    'target_ids': target_ids

                }

        except Exception as e:

            st.error(f"Error getting network data: {e}")

            return None

    

    def get_drug_network(self, drug_name: str, depth: int = 1) -> Dict[str, Any]:

        """Get network around a specific drug"""

        if not self.driver:

            return None

            

        try:

            with self.driver.session(database=self.database) as session:

                # Get drug's targets and similar drugs

                result = session.run("""

                    MATCH (d:Drug {name: $drug_name})-[:TARGETS]->(t:Target)

                    OPTIONAL MATCH (t)<-[:TARGETS]-(other:Drug)

                    WHERE other.name <> $drug_name

                    RETURN d.name as drug, d.moa as moa, d.phase as phase,

                           t.name as target, other.name as other_drug, 

                           other.moa as other_moa, other.phase as other_phase

                    LIMIT 100

                """, drug_name=drug_name)

                

                data = result.data()

                

                # Create network data

                nodes = []

                edges = []

                node_ids = {}

                

                # Add central drug

                node_ids[drug_name] = 0

                nodes.append({

                    'id': 0,

                    'label': drug_name,

                    'type': 'central_drug',

                    'moa': data[0]['moa'] if data else '',

                    'phase': data[0]['phase'] if data else ''

                })

                

                # Add targets and other drugs

                for record in data:

                    target_name = record['target']

                    other_drug = record['other_drug']

                    

                    # Add target

                    if target_name not in node_ids:

                        node_ids[target_name] = len(nodes)

                        nodes.append({

                            'id': len(nodes),

                            'label': target_name,

                            'type': 'target'

                        })

                    

                    # Add other drug

                    if other_drug and other_drug not in node_ids:

                        node_ids[other_drug] = len(nodes)

                        nodes.append({

                            'id': len(nodes),

                            'label': other_drug,

                            'type': 'other_drug',

                            'moa': record['other_moa'],

                            'phase': record['other_phase']

                        })

                    

                    # Add edges

                    edges.append({

                        'source': node_ids[drug_name],

                        'target': node_ids[target_name],

                        'type': 'targets'

                    })

                    

                    if other_drug:

                        edges.append({

                            'source': node_ids[other_drug],

                            'target': node_ids[target_name],

                            'type': 'targets'

                        })

                

                return {

                    'nodes': nodes,

                    'edges': edges,

                    'central_drug': drug_name

                }

        except Exception as e:

            st.error(f"Error getting drug network: {e}")

            return None

    def find_drugs_by_target(self, target_name: str) -> List[Dict]:
        """Find all drugs that target a specific target"""
        if not self.driver:
            return []
            
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run("""
                    MATCH (d:Drug)-[:TARGETS]->(t:Target {name: $target_name})
                    RETURN d.name as drug, d.moa as moa, d.phase as phase
                    ORDER BY d.name
                """, target_name=target_name)
                return result.data()
        except Exception as e:
            st.error(f"Error finding drugs by target: {e}")
            return []

    
    def get_target_network(self, target_name: str, depth: int = 1) -> Dict[str, Any]:
        """Get network around a specific target"""
        
        if not self.driver:
            return None
            
        try:
            with self.driver.session(database=self.database) as session:
                # Get target's drugs and their targets
                result = session.run("""
                    MATCH (t:Target {name: $target_name})<-[:TARGETS]-(d:Drug)
                    OPTIONAL MATCH (d)-[:TARGETS]->(other_t:Target)
                    WHERE other_t.name <> $target_name
                    RETURN t.name as target, d.name as drug, d.moa as moa, d.phase as phase,
                           other_t.name as other_target
                    LIMIT 100
                """, target_name=target_name)
                
                data = result.data()
                
                # Create network data
                nodes = []
                edges = []
                node_ids = {}
                
                # Add central target
                node_ids[target_name] = 0
                nodes.append({
                    'id': 0,
                    'label': target_name,
                    'type': 'central_target'
                })
                
                # Add drugs and other targets
                for record in data:
                    drug_name = record['drug']
                    other_target = record['other_target']
                    
                    # Add drug
                    if drug_name not in node_ids:
                        node_ids[drug_name] = len(nodes)
                        nodes.append({
                            'id': len(nodes),
                            'label': drug_name,
                            'type': 'drug',
                            'moa': record['moa'],
                            'phase': record['phase']
                        })
                    
                    # Add other target
                    if other_target and other_target not in node_ids:
                        node_ids[other_target] = len(nodes)
                        nodes.append({
                            'id': len(nodes),
                            'label': other_target,
                            'type': 'other_target'
                        })
                    
                    # Add edges
                    edges.append({
                        'source': node_ids[drug_name],
                        'target': node_ids[target_name],
                        'type': 'targets'
                    })
                    
                    if other_target:
                        edges.append({
                            'source': node_ids[drug_name],
                            'target': node_ids[other_target],
                            'type': 'targets'
                        })
                
                return {
                    'nodes': nodes,
                    'edges': edges,
                    'central_target': target_name
                }
                
        except Exception as e:
            st.error(f"Error getting target network: {e}")
            return None

    def search_drugs(self, search_term: str, limit: int = 20) -> List[Dict]:

        """Search for drugs by name"""

        if not self.driver:

            return []

            

        try:

            with self.driver.session(database=self.database) as session:

                result = session.run("""

                    MATCH (d:Drug)

                    WHERE toLower(d.name) CONTAINS toLower($search_term)

                    RETURN d.name as drug, d.moa as moa, d.phase as phase

                    ORDER BY d.name

                    LIMIT $limit

                """, search_term=search_term, limit=limit)

                return result.data()

        except Exception as e:

            st.error(f"Error searching drugs: {e}")

            return []

    

    def search_targets(self, search_term: str, limit: int = 20) -> List[Dict]:

        """Search for targets by name"""

        if not self.driver:

            return []

            

        try:

            with self.driver.session(database=self.database) as session:

                result = session.run("""

                    MATCH (t:Target)

                    WHERE toLower(t.name) CONTAINS toLower($search_term)

                    RETURN t.name as target

                    ORDER BY t.name

                    LIMIT $limit

                """, search_term=search_term, limit=limit)

                return result.data()

        except Exception as e:

            st.error(f"Error searching targets: {e}")

            return []

    

    def get_drug_details(self, drug_name: str) -> Dict[str, Any]:

        """Get comprehensive information about a specific drug including all relationships"""

        if not self.driver:

            return None

            

        try:

            with self.driver.session(database=self.database) as session:

                # Get comprehensive drug info with all properties

                drug_info = session.run("""

                    MATCH (d:Drug {name: $drug_name})

                    RETURN d.name as name, d.moa as moa, d.phase as phase,

                           d.disease_area as disease_area, d.indication as indication,

                           d.vendor as vendor, d.purity as purity, d.smiles as smiles

                """, drug_name=drug_name).single()

                

                if not drug_info:

                    return None

                    

                # Get targets with detailed information

                targets = session.run("""

                    MATCH (d:Drug {name: $drug_name})-[:TARGETS]->(t:Target)

                    RETURN t.name as target

                    ORDER BY t.name

                """, drug_name=drug_name).data()

                

                # Get related indications

                indications = session.run("""

                    MATCH (d:Drug {name: $drug_name})-[:TREATS]->(i:Indication)

                    RETURN i.name as indication

                    ORDER BY i.name

                """, drug_name=drug_name).data()

                

                # Get disease areas

                disease_areas = session.run("""

                    MATCH (d:Drug {name: $drug_name})-[:BELONGS_TO]->(da:DiseaseArea)

                    RETURN da.name as disease_area

                    ORDER BY da.name

                """, drug_name=drug_name).data()

                

                # Get vendors

                vendors = session.run("""

                    MATCH (d:Drug {name: $drug_name})-[:SUPPLIED_BY]->(v:Vendor)

                    RETURN v.name as vendor

                    ORDER BY v.name

                """, drug_name=drug_name).data()

                

                # Get similar drugs

                similar_drugs = session.run("""

                    MATCH (d:Drug {name: $drug_name})-[:TARGETS]->(t:Target)<-[:TARGETS]-(other:Drug)

                    WHERE other.name <> $drug_name

                    WITH other, count(t) as common_targets

                    ORDER BY common_targets DESC

                    LIMIT 10

                    RETURN other.name as drug, other.moa as moa, other.phase as phase, common_targets

                """, drug_name=drug_name).data()

                

                return {

                    "drug_info": dict(drug_info),

                    "targets": [t["target"] for t in targets],

                    "indications": [i["indication"] for i in indications],

                    "disease_areas": [da["disease_area"] for da in disease_areas],

                    "vendors": [v["vendor"] for v in vendors],

                    "similar_drugs": similar_drugs

                }

        except Exception as e:

            st.error(f"Error getting drug details: {e}")

            return None

    

    def get_target_details(self, target_name: str) -> Dict[str, Any]:

        """Get detailed information about a target including mechanism classifications"""

        if not self.driver:

            return None

            

        try:

            with self.driver.session(database=self.database) as session:

                # Get comprehensive target information with mechanism details

                result = session.run("""

                    MATCH (t:Target {name: $target_name})<-[r:TARGETS]-(d:Drug)

                    RETURN 

                        t.name as target_name,

                        d.name as drug_name,

                        d.moa as drug_moa,

                        d.phase as drug_phase,

                        r.relationship_type as relationship_type,

                        r.target_class as target_class,

                        r.target_subclass as target_subclass,

                        r.mechanism as mechanism,

                        r.confidence as confidence,

                        r.reasoning as reasoning,

                        r.classified as is_classified

                    ORDER BY d.name

                """, target_name=target_name).data()

                

                if not result:

                    return {

                        "target_name": target_name,

                        "drugs": [],

                        "target_info": {},

                        "classification_stats": {"total": 0, "classified": 0}

                    }

                

                # Process the results

                drugs = []

                target_classes = set()

                target_subclasses = set()

                classified_count = 0

                

                for record in result:

                    drug_info = {

                        "drug_name": record["drug_name"],

                        "drug_moa": record["drug_moa"],

                        "drug_phase": record["drug_phase"],

                        "relationship_type": record.get("relationship_type"),

                        "target_class": record.get("target_class"),

                        "target_subclass": record.get("target_subclass"),

                        "mechanism": record.get("mechanism"),

                        "confidence": record.get("confidence"),

                        "reasoning": record.get("reasoning"),

                        "is_classified": record.get("is_classified", False)

                    }

                    drugs.append(drug_info)

                    

                    # Collect target class information

                    if record.get("target_class"):

                        target_classes.add(record["target_class"])

                    if record.get("target_subclass"):

                        target_subclasses.add(record["target_subclass"])

                    

                    if drug_info["is_classified"]:

                        classified_count += 1

                

                # Determine target type (most common classification)

                target_info = {

                    "name": target_name,

                    "target_classes": list(target_classes),

                    "target_subclasses": list(target_subclasses),

                    "primary_class": list(target_classes)[0] if target_classes else "Unknown",

                    "primary_subclass": list(target_subclasses)[0] if target_subclasses else "Unknown"

                }

                

                classification_stats = {

                    "total": len(drugs),

                    "classified": classified_count,

                    "percentage": (classified_count / len(drugs) * 100) if drugs else 0

                }

                

                return {

                    "target_name": target_name,

                    "drugs": drugs,

                    "target_info": target_info,

                    "classification_stats": classification_stats

                }

                

        except Exception as e:

            st.error(f"Error getting target details: {e}")

            return None

    

    def get_phase_statistics(self) -> List[Dict]:

        """Get statistics by drug development phase"""

        if not self.driver:

            return []

            

        try:

            with self.driver.session(database=self.database) as session:

                result = session.run("""

                    MATCH (d:Drug)

                    WHERE d.phase IS NOT NULL AND d.phase <> ''

                    RETURN d.phase as phase, count(d) as drug_count

                    ORDER BY drug_count DESC

                """)

                return result.data()

        except Exception as e:

            st.error(f"Error getting phase statistics: {e}")

            return []

    

    def get_moa_statistics(self) -> List[Dict]:

        """Get enhanced MOA statistics with new relationship data"""

        if not self.driver:

            return []

            

        try:

            with self.driver.session(database=self.database) as session:

                result = session.run("""

                    MATCH (m:MOA)

                    OPTIONAL MATCH (m)<-[:HAS_MOA]-(d:Drug)

                    OPTIONAL MATCH (m)-[:TARGETS_VIA]->(t:Target)

                    OPTIONAL MATCH (m)-[:BELONGS_TO_CLASS]->(tc:TherapeuticClass)

                    RETURN m.name as moa, 

                           count(DISTINCT d) as drug_count,

                           count(DISTINCT t) as target_count,

                           collect(DISTINCT tc.name)[0] as therapeutic_class,

                           m.avg_development_stage as avg_stage

                    ORDER BY drug_count DESC

                    LIMIT 20

                """)

                return result.data()

        except Exception as e:

            st.error(f"Error getting MOA statistics: {e}")

            return []

    

    def search_drugs_by_moa(self, moa_search: str, limit: int = 20) -> List[Dict]:

        """Search drugs by mechanism of action"""

        if not self.driver:

            return []

            

        try:

            with self.driver.session(database=self.database) as session:

                result = session.run("""

                    MATCH (m:MOA)

                    WHERE toLower(m.name) CONTAINS toLower($moa_search)

                    MATCH (m)<-[:HAS_MOA]-(d:Drug)

                    RETURN d.name as drug, d.moa as moa, d.phase as phase,

                           m.drug_count as moa_drug_count,

                           m.target_diversity as moa_target_diversity

                    ORDER BY m.drug_count DESC, d.name

                    LIMIT $limit

                """, moa_search=moa_search, limit=limit)

                return result.data()

        except Exception as e:

            st.error(f"Error searching drugs by MOA: {e}")

            return []

    

    def get_similar_drugs_by_moa(self, drug_name: str, limit: int = 10) -> List[Dict]:

        """Get drugs with similar MOA to the given drug"""

        if not self.driver:

            return []

            

        try:

            with self.driver.session(database=self.database) as session:

                result = session.run("""

                    MATCH (d1:Drug {name: $drug_name})-[:SIMILAR_MOA]-(d2:Drug)

                    MATCH (d1)-[:HAS_MOA]->(m:MOA)

                    OPTIONAL MATCH (d2)-[:TARGETS]->(t:Target)

                    RETURN d2.name as drug, d2.moa as moa, d2.phase as phase,

                           m.name as shared_mechanism,

                           count(t) as target_count

                    ORDER BY target_count DESC

                    LIMIT $limit

                """, drug_name=drug_name, limit=limit)

                return result.data()

        except Exception as e:

            st.error(f"Error getting similar drugs by MOA: {e}")

            return []

    

    def get_repurposing_candidates(self, drug_name: str = None, limit: int = 15) -> List[Dict]:

        """Get drug repurposing candidates"""

        if not self.driver:

            return []

            

        try:

            with self.driver.session(database=self.database) as session:

                if drug_name:

                    # Get repurposing candidates for specific drug

                    result = session.run("""

                        MATCH (d1:Drug {name: $drug_name})-[r:REPURPOSING_CANDIDATE]->(d2:Drug)

                        OPTIONAL MATCH (d1)-[:TREATS]->(i1:Indication)

                        OPTIONAL MATCH (d2)-[:TREATS]->(i2:Indication)

                        RETURN d1.name as source_drug, d2.name as candidate_drug,

                               d1.moa as source_moa, d2.moa as candidate_moa,

                               d1.phase as source_phase, d2.phase as candidate_phase,

                               r.shared_targets as shared_targets,

                               collect(DISTINCT i1.name) as source_indications,

                               collect(DISTINCT i2.name) as candidate_indications

                        ORDER BY r.shared_targets DESC

                        LIMIT $limit

                    """, drug_name=drug_name, limit=limit)

                else:

                    # Get top repurposing opportunities overall

                    result = session.run("""

                        MATCH (d1:Drug)-[r:REPURPOSING_CANDIDATE]->(d2:Drug)

                        WHERE d1.phase = 'Approved' OR d2.phase = 'Approved'

                        RETURN d1.name as source_drug, d2.name as candidate_drug,

                               d1.moa as source_moa, d2.moa as candidate_moa,

                               d1.phase as source_phase, d2.phase as candidate_phase,

                               r.shared_targets as shared_targets

                        ORDER BY r.shared_targets DESC

                        LIMIT $limit

                    """, limit=limit)

                

                return result.data()

        except Exception as e:

            st.error(f"Error getting repurposing candidates: {e}")

            return []

    

    def get_therapeutic_class_analysis(self, class_name: str = None) -> Dict[str, Any]:

        """Get therapeutic class analysis"""

        if not self.driver:

            return {}

            

        try:

            with self.driver.session(database=self.database) as session:

                if class_name:

                    # Analyze specific therapeutic class

                    result = session.run("""

                        MATCH (tc:TherapeuticClass {name: $class_name})<-[:BELONGS_TO_CLASS]-(m:MOA)<-[:HAS_MOA]-(d:Drug)

                        OPTIONAL MATCH (d)-[:TARGETS]->(t:Target)

                        RETURN tc.name as class_name,

                               count(DISTINCT m) as moa_count,

                               count(DISTINCT d) as drug_count,

                               count(DISTINCT t) as target_count,

                               collect(DISTINCT m.name)[0..10] as sample_moas,

                               collect(DISTINCT d.name)[0..10] as sample_drugs

                    """, class_name=class_name)

                    

                    data = result.single()

                    return dict(data) if data else {}

                else:

                    # Get all therapeutic classes overview

                    result = session.run("""

                        MATCH (tc:TherapeuticClass)<-[:BELONGS_TO_CLASS]-(m:MOA)<-[:HAS_MOA]-(d:Drug)

                        RETURN tc.name as class_name,

                               count(DISTINCT m) as moa_count,

                               count(DISTINCT d) as drug_count

                        ORDER BY drug_count DESC

                    """)

                    

                    return {"classes": result.data()}

        except Exception as e:

            st.error(f"Error getting therapeutic class analysis: {e}")

            return {}

    

    def initialize_classifier(self, neo4j_uri: str, neo4j_user: str, neo4j_password: str, neo4j_database: str):

        """Initialize the mechanism classifier with current database connection"""

        if not CLASSIFIER_AVAILABLE:

            return

            

        try:

            # Get Gemini API key from environment, .env file, or fallback

            gemini_api_key = os.getenv('GEMINI_API_KEY')

            

            # Fallback API key if not found in environment

            if not gemini_api_key:

                gemini_api_key = "AIzaSyDg9hpHWOZz4Y3iXiUbezTPE-ROTdJDdYs"  # Your provided API key

            

            if gemini_api_key:

                self.classifier = DrugTargetMechanismClassifier(

                    gemini_api_key=gemini_api_key,

                    neo4j_uri=neo4j_uri,

                    neo4j_user=neo4j_user,

                    neo4j_password=neo4j_password,

                    neo4j_database=neo4j_database

                )

                st.session_state.classifier = self.classifier

                logger.info("Mechanism classifier initialized successfully")

            else:

                logger.warning("GEMINI_API_KEY not found in environment variables")

                

        except Exception as e:

            logger.error(f"Error initializing classifier: {e}")

    

    def get_drug_target_classification(self, drug_name: str, target_name: str, force_reclassify: bool = False) -> Optional[Dict]:
        """Get or create mechanism classification for a drug-target pair with enhanced caching"""
        if not self.classifier:
            return None
            
        # Check in-memory cache first
        cache_key = f"{drug_name}_{target_name}"
        if not force_reclassify and cache_key in self._classification_cache:
            return self._classification_cache[cache_key]
            
        # Check persistent cache
        persistent_key = get_cache_key(drug_name, target_name)
        if not force_reclassify:
            cached_data = load_from_cache(persistent_key)
            if cached_data:
                self._classification_cache[cache_key] = cached_data
                return cached_data
        
        try:
            # Get classification from API
            classification = self.classifier.classify_and_store(drug_name, target_name, force_reclassify=force_reclassify)
            
            # Save to both caches
            if classification:
                self._classification_cache[cache_key] = classification
                save_to_cache(persistent_key, classification)
            
            return classification
            
        except Exception as e:
            logger.error(f"Error classifying {drug_name} -> {target_name}: {e}")
            return None
    
    def get_cached_classification(self, drug_name: str, target_name: str) -> Optional[Dict]:
        """Get classification from cache only (no API call)"""
        cache_key = f"{drug_name}_{target_name}"
        if cache_key in self._classification_cache:
            return self._classification_cache[cache_key]
    
    def is_cached(self, drug_name: str, target_name: str) -> bool:
        """Check if classification is cached"""
        cache_key = f"{drug_name}_{target_name}"
        return cache_key in self._classification_cache
    
    def background_classify_targets(self, drug_name: str, targets: List[str]) -> None:
        """Classify targets in background thread"""
        thread_key = f"classify_{drug_name}"
        
        # Don't start if already running
        if thread_key in self._background_threads:
            return
            
        def classify_worker():
            try:
                for target in targets:
                    # Check if already cached
                    if self.get_cached_classification(drug_name, target):
                        continue
                    
                    # Classify in background
                    classification = self.classifier.classify_and_store(drug_name, target)
                    if classification:
                        cache_key = f"{drug_name}_{target}"
                        self._classification_cache[cache_key] = classification
                        persistent_key = get_cache_key(drug_name, target)
                        save_to_cache(persistent_key, classification)
                        
                # Remove thread reference when done
                if thread_key in self._background_threads:
                    del self._background_threads[thread_key]
                    
            except Exception as e:
                st.error(f"Background classification error: {e}")
                if thread_key in self._background_threads:
                    del self._background_threads[thread_key]
        
        # Start background thread
        thread = threading.Thread(target=classify_worker, daemon=True)
        thread.start()
        self._background_threads[thread_key] = thread
    
    def get_target_network_data(self, target_name: str) -> Dict[str, Any]:
        """Get network data for a target-centered view"""
        if not self.driver:
            return None
            
        try:
            with self.driver.session(database=self.database) as session:
                # Get all drugs targeting this target
                result = session.run("""
                    MATCH (d:Drug)-[:TARGETS]->(t:Target {name: $target_name})
                    RETURN d.name as drug, d.moa as moa, d.phase as phase
                    ORDER BY d.name
                """, target_name=target_name)
                
                drugs = result.data()
                
                # Get mechanism information for each drug-target pair
                target_mechanisms = {}
                for drug in drugs:
                    drug_name = drug['drug']
                    classification = self.get_cached_classification(drug_name, target_name)
                    if classification:
                        target_mechanisms[drug_name] = {
                            'mechanism': classification.get('mechanism', 'Unknown'),
                            'relationship_type': classification.get('relationship_type', 'Unknown'),
                            'target_class': classification.get('target_class', 'Unknown'),
                            'target_subclass': classification.get('target_subclass', 'Unknown'),
                            'confidence': classification.get('confidence', 0),
                            'reasoning': classification.get('reasoning', 'No details available'),
                            'classified': True
                        }
                    else:
                        target_mechanisms[drug_name] = {
                            'mechanism': 'Unclassified',
                            'relationship_type': 'Unclassified',
                            'target_class': 'Unknown',
                            'target_subclass': 'Unknown',
                            'confidence': 0,
                            'reasoning': 'No details available',
                            'classified': False
                        }
                
                return {
                    'target': target_name,
                    'drugs': drugs,
                    'target_mechanisms': target_mechanisms
                }
                
        except Exception as e:
            st.error(f"Error getting target network data: {e}")
            return None

    def get_top_drugs_by_targets(self, limit: int = 10) -> List[Dict]:

        """Get drugs with most targets"""

        if not self.driver:

            return []

            

        try:

            with self.driver.session(database=self.database) as session:

                result = session.run("""

                    MATCH (d:Drug)-[:TARGETS]->(t:Target)

                    RETURN d.name as drug, d.moa as moa, d.phase as phase, count(t) as target_count

                    ORDER BY target_count DESC

                    LIMIT $limit

                """, limit=limit)

                return result.data()

        except Exception as e:

            st.error(f"Error getting top drugs: {e}")

            return []

    

    def get_top_targets_by_drugs(self, limit: int = 10) -> List[Dict]:

        """Get targets with most drugs"""

        if not self.driver:

            return []

            

        try:

            with self.driver.session(database=self.database) as session:

                result = session.run("""

                    MATCH (d:Drug)-[:TARGETS]->(t:Target)

                    RETURN t.name as target, count(d) as drug_count

                    ORDER BY drug_count DESC

                    LIMIT $limit

                """, limit=limit)

                return result.data()

        except Exception as e:

            st.error(f"Error getting top targets: {e}")

            return []

    

    def get_drug_repurposing_insights(self) -> Dict[str, Any]:

        """Get insights for drug repurposing opportunities"""

        if not self.driver:

            return None

            

        try:

            with self.driver.session(database=self.database) as session:

                # Get drugs with multiple targets (polypharmacology)

                poly_drugs = session.run("""

                    MATCH (d:Drug)-[:TARGETS]->(t:Target)

                    WITH d, count(t) as target_count

                    WHERE target_count > 3

                    RETURN d.name as drug, d.moa as moa, d.phase as phase, target_count

                    ORDER BY target_count DESC

                    LIMIT 10

                """).data()

                

                # Get targets with multiple drugs (druggable targets)

                druggable_targets = session.run("""

                    MATCH (d:Drug)-[:TARGETS]->(t:Target)

                    WITH t, count(d) as drug_count

                    WHERE drug_count > 2

                    RETURN t.name as target, drug_count

                    ORDER BY drug_count DESC

                    LIMIT 10

                """).data()

                

                # Get phase distribution insights

                phase_insights = session.run("""

                    MATCH (d:Drug)

                    WHERE d.phase IS NOT NULL AND d.phase <> ''

                    RETURN d.phase as phase, count(d) as drug_count

                    ORDER BY drug_count DESC

                """).data()

                

                return {

                    "polypharmacology_drugs": poly_drugs,

                    "druggable_targets": druggable_targets,

                    "phase_distribution": phase_insights

                }

        except Exception as e:

            st.error(f"Error getting repurposing insights: {e}")

            return None

    

    def get_drug_similarity_analysis(self, drug_name: str) -> Dict[str, Any]:

        """Analyze similarity between drugs based on target profiles"""

        if not self.driver:

            return None

            

        try:

            with self.driver.session(database=self.database) as session:

                # Get drugs with similar target profiles

                similar_drugs = session.run("""

                    MATCH (d1:Drug {name: $drug_name})-[:TARGETS]->(t:Target)<-[:TARGETS]-(d2:Drug)

                    WHERE d2.name <> $drug_name

                    WITH d2, count(t) as common_targets

                    ORDER BY common_targets DESC

                    LIMIT 15

                    RETURN d2.name as drug, d2.moa as moa, d2.phase as phase, common_targets

                """, drug_name=drug_name).data()

                

                # Get target overlap percentage

                total_targets = session.run("""

                    MATCH (d:Drug {name: $drug_name})-[:TARGETS]->(t:Target)

                    RETURN count(t) as total_targets

                """, drug_name=drug_name).single()["total_targets"]

                

                # Calculate similarity scores

                for drug in similar_drugs:

                    drug['similarity_score'] = round((drug['common_targets'] / total_targets) * 100, 2)

                

                return {

                    "similar_drugs": similar_drugs,

                    "total_targets": total_targets

                }

        except Exception as e:

            st.error(f"Error getting drug similarity: {e}")

            return None

    

    def get_3d_network_data(self, limit: int = 30) -> Dict[str, Any]:

        """Get 3D network data for visualization"""

        if not self.driver:

            return None

            

        try:

            with self.driver.session(database=self.database) as session:

                # Get sample drugs and their targets with 3D positioning

                result = session.run("""

                    MATCH (d:Drug)-[:TARGETS]->(t:Target)

                    RETURN d.name as drug, d.moa as moa, d.phase as phase, 

                           t.name as target, count(t) as target_count

                    ORDER BY target_count DESC

                    LIMIT $limit

                """, limit=limit)

                

                data = result.data()

                

                # Create 3D nodes and edges

                nodes = []

                edges = []

                drug_ids = {}

                target_ids = {}

                

                for i, record in enumerate(data):

                    drug_name = record['drug']

                    target_name = record['target']

                    

                    # Add drug node if not exists

                    if drug_name not in drug_ids:

                        drug_ids[drug_name] = len(nodes)

                        # Create 3D position in a sphere

                        angle = len(nodes) * 2 * np.pi / (limit * 2)

                        radius = 2.0

                        nodes.append({

                            'id': len(nodes),

                            'label': drug_name,

                            'type': 'drug',

                            'moa': record['moa'],

                            'phase': record['phase'],

                            'x': radius * np.cos(angle),

                            'y': radius * np.sin(angle),

                            'z': np.random.uniform(-1, 1)

                        })

                    

                    # Add target node if not exists

                    if target_name not in target_ids:

                        target_ids[target_name] = len(nodes)

                        # Create 3D position in inner sphere

                        angle = len(nodes) * 2 * np.pi / (limit * 2)

                        radius = 1.0

                        nodes.append({

                            'id': len(nodes),

                            'label': target_name,

                            'type': 'target',

                            'x': radius * np.cos(angle),

                            'y': radius * np.sin(angle),

                            'z': np.random.uniform(-0.5, 0.5)

                        })

                    

                    # Add edge

                    edges.append({

                        'source': drug_ids[drug_name],

                        'target': target_ids[target_name],

                        'type': 'targets'

                    })

                

                return {

                    'nodes': nodes,

                    'edges': edges,

                    'drug_ids': drug_ids,

                    'target_ids': target_ids

                }

        except Exception as e:

            st.error(f"Error getting 3D network data: {e}")

            return None

    

    def get_drug_comparison(self, drug1: str, drug2: str) -> Dict[str, Any]:

        """Compare two drugs in detail"""

        if not self.driver:

            return None

            

        try:

            with self.driver.session(database=self.database) as session:

                # Get drug 1 details

                drug1_info = session.run("""

                    MATCH (d:Drug {name: $drug1})

                    RETURN d.name as name, d.moa as moa, d.phase as phase

                """, drug1=drug1).single()

                

                # Get drug 2 details

                drug2_info = session.run("""

                    MATCH (d:Drug {name: $drug2})

                    RETURN d.name as name, d.moa as moa, d.phase as phase

                """, drug2=drug2).single()

                

                if not drug1_info or not drug2_info:

                    return None

                

                # Get targets for both drugs

                drug1_targets = session.run("""

                    MATCH (d:Drug {name: $drug1})-[:TARGETS]->(t:Target)

                    RETURN t.name as target

                    ORDER BY t.name

                """, drug1=drug1).data()

                

                drug2_targets = session.run("""

                    MATCH (d:Drug {name: $drug2})-[:TARGETS]->(t:Target)

                    RETURN t.name as target

                    ORDER BY t.name

                """, drug2=drug2).data()

                

                # Get common targets

                common_targets = session.run("""

                    MATCH (d1:Drug {name: $drug1})-[:TARGETS]->(t:Target)<-[:TARGETS]-(d2:Drug {name: $drug2})

                    RETURN t.name as target

                    ORDER BY t.name

                """, drug1=drug1, drug2=drug2).data()

                

                # Get unique targets for each drug

                drug1_unique = [t['target'] for t in drug1_targets if t['target'] not in [ct['target'] for ct in common_targets]]

                drug2_unique = [t['target'] for t in drug2_targets if t['target'] not in [ct['target'] for ct in common_targets]]

                

                return {

                    "drug1": dict(drug1_info),

                    "drug2": dict(drug2_info),

                    "drug1_targets": [t['target'] for t in drug1_targets],

                    "drug2_targets": [t['target'] for t in drug2_targets],

                    "common_targets": [t['target'] for t in common_targets],

                    "drug1_unique": drug1_unique,

                    "drug2_unique": drug2_unique,

                    "similarity_score": len(common_targets) / max(len(drug1_targets), len(drug2_targets)) * 100

                }

        except Exception as e:

            st.error(f"Error comparing drugs: {e}")

            return None

    

    def get_therapeutic_pathways(self, drug_name: str) -> Dict[str, Any]:

        """Get therapeutic pathways and mechanisms for a drug"""

        if not self.driver:

            return None

            

        try:

            with self.driver.session(database=self.database) as session:

                # Get drug's targets and their biological functions

                result = session.run("""

                    MATCH (d:Drug {name: $drug_name})-[:TARGETS]->(t:Target)

                    OPTIONAL MATCH (t)<-[:TARGETS]-(other:Drug)

                    WHERE other.name <> $drug_name

                    RETURN d.name as drug, d.moa as moa, d.phase as phase,

                           t.name as target, count(other) as other_drugs

                    ORDER BY other_drugs DESC

                """, drug_name=drug_name)

                

                data = result.data()

                

                if not data:

                    return None

                

                # Group by mechanism of action

                moa_groups = {}

                for record in data:

                    moa = record['moa'] if record['moa'] else 'Unknown'

                    if moa not in moa_groups:

                        moa_groups[moa] = []

                    moa_groups[moa].append({

                        'target': record['target'],

                        'other_drugs': record['other_drugs']

                    })

                

                return {

                    "drug_name": drug_name,

                    "moa_groups": moa_groups,

                    "total_targets": len(data),

                    "unique_moa": len(moa_groups)

                }

        except Exception as e:

            st.error(f"Error getting therapeutic pathways: {e}")

            return None

    

    def close(self):

        """Close the database connection"""

        if self.driver:

            self.driver.close()



def main():

    """Main Streamlit app"""

    st.markdown('<h1 class="main-header">💊 Drug-Target Graph Database</h1>', unsafe_allow_html=True)

    

    # Initialize the app

    app = DrugTargetGraphApp()

    

    # Show connection status and setup

    if not app.driver:

        st.info("🔗 Please connect to your database to get started.")
        

        # Show connection form in main area if not connected

        app.get_manual_connection()

    else:

        st.success("✅ Connected to Neo4j database successfully!")

        st.info(f"Database: {app.database}")

        

        # Sidebar navigation

        st.sidebar.title("🧭 Navigation")

        

        # Connection status

        st.sidebar.success("✅ Connected to Neo4j")

        

        # No more automatic navigation - everything is inline now
        page = st.sidebar.selectbox(

            "Choose a page:",

            ["🏠 Dashboard", "🔍 Search Drugs", "🎯 Search Targets", "🧬 MOA Analysis", "🔄 Drug Repurposing", "🔬 Mechanism Classification", "📊 Statistics", "🌐 Network Visualization", "🎨 3D Network", "💡 Drug Discovery", "📈 Advanced Analytics"]

        )

        

        try:

            if page == "🏠 Dashboard":

                show_dashboard(app)

            elif page == "🔍 Search Drugs":

                show_drug_search(app)

            elif page == "🎯 Search Targets":

                show_target_search(app)

            elif page == "🧬 MOA Analysis":

                show_moa_analysis(app)

            elif page == "🔄 Drug Repurposing":

                show_drug_repurposing(app)

            elif page == "🔬 Mechanism Classification":

                show_mechanism_classification(app)

            elif page == "📊 Statistics":

                show_statistics(app)

            elif page == "🌐 Network Visualization":

                show_network_visualization(app)

            elif page == "🎨 3D Network":

                show_3d_network_visualization(app)

            elif page == "💡 Drug Discovery":

                show_drug_discovery(app)

            elif page == "📈 Advanced Analytics":

                show_advanced_analytics(app)

                

        except Exception as e:

            st.error(f"An error occurred: {e}")

            st.exception(e)

        

        # Close connection when app is done

        if st.button("Close Connection"):

            app.close()

            st.success("Connection closed!")

            st.rerun()



def show_dashboard(app):

    """Show the main dashboard"""

    # Welcome message and introduction

    st.markdown("""

    ## 👋 Welcome to the Enhanced Drug-Target Graph Database!

    

    **What is this?** A powerful interactive tool to explore comprehensive relationships between drugs and their biological targets using Neo4j graph database technology.

    

    **🌟 What can you do here?**

    - 🔍 **Search drugs** and see detailed MOAs, targets, disease areas, vendors, and chemical structures

    - 🎯 **Find all drugs** targeting specific proteins with complete profiles

    - 🌐 **Visualize networks** in beautiful 2D and immersive 3D interactive graphs

    - 💡 **Discover insights** for drug repurposing and advanced analytics

    - 🏥 **Filter by disease areas** and medical indications

    - 🧪 **View chemical structures** in SMILES notation

    """)

    

    st.header("📊 Database Overview")

    

    # Get basic statistics

    stats = app.get_graph_statistics()

    

    if stats:

        # Display metrics in beautiful cards

        col1, col2, col3 = st.columns(3)

        

        with col1:

            st.markdown(f"""

            <div class="metric-card">

                <h3>💊 Total Drugs</h3>

                <h2>{stats['drug_count']:,}</h2>

                <p>Pharmaceutical compounds</p>

            </div>

            """, unsafe_allow_html=True)

        

        with col2:

            st.markdown(f"""

            <div class="metric-card">

                <h3>🎯 Total Targets</h3>

                <h2>{stats['target_count']:,}</h2>

                <p>Biological targets</p>

            </div>

            """, unsafe_allow_html=True)

        

        with col3:

            st.markdown(f"""

            <div class="metric-card">

                <h3>🔗 Total Relationships</h3>

                <h2>{stats['relationship_count']:,}</h2>

                <p>Drug-target interactions</p>

            </div>

            """, unsafe_allow_html=True)

        

        # Show top drugs and targets

        col1, col2 = st.columns(2)

        

        with col1:

            st.subheader("🏆 Top Drugs by Target Count")

            top_drugs = app.get_top_drugs_by_targets(5)

            if top_drugs:

                for drug in top_drugs:

                    st.markdown(f"""

                    <div class="drug-card">

                        <h4>{drug['drug']}</h4>

                        <p><strong>Targets:</strong> {drug['target_count']}</p>

                        <p><strong>MOA:</strong> {drug['moa']}</p>

                        <p><strong>Phase:</strong> {drug['phase']}</p>

                    </div>

                    """, unsafe_allow_html=True)

        

        with col2:

            st.subheader("🎯 Top Targets by Drug Count")

            top_targets = app.get_top_targets_by_drugs(5)

            if top_targets:

                for target in top_targets:

                    st.markdown(f"""

                    <div class="target-card">

                        <h4>{target['target']}</h4>

                        <p><strong>Drugs:</strong> {target['drug_count']}</p>

                        <p>Targeted by multiple compounds</p>

                    </div>

                    """, unsafe_allow_html=True)

        

        # Quick search

        st.subheader("🔍 Quick Search")

        search_type = st.selectbox("Search for:", ["Drugs", "Targets"])

        search_term = st.text_input("Enter search term:")

        

        if search_term:

            if search_type == "Drugs":

                results = app.search_drugs(search_term, 10)

                if results:

                    st.write(f"Found {len(results)} drugs:")

                    for drug in results:

                        st.write(f"- **{drug['drug']}** (MOA: {drug['moa']}, Phase: {drug['phase']})")

            else:

                results = app.search_targets(search_term, 10)

                if results:

                    st.write(f"Found {len(results)} targets:")

                    for target in results:

                        st.write(f"- **{target['target']}**")

    else:

        st.warning("Please connect to Neo4j database first.")



def show_network_visualization(app):

    """Show network visualization"""

    st.header("🌐 Network Visualization")

    

    # Add helpful introduction

    st.markdown("""

    **What is network visualization?** See how drugs and biological targets connect to each other in beautiful interactive graphs.

    

    **What do the colors mean?**

    - 🔴 **Red nodes** = Drugs (medicines)

    - 🔵 **Blue nodes** = Biological targets (proteins in your body)

    - 🟢 **Green nodes** = Related drugs (drugs with similar targets)

    - **Gray lines** = Connections showing "drug targets this protein"

    

    **How to use:** Enter a drug name below to see its network, or generate a global view of all connections.

    """)

    

    # Network options

    col1, col2 = st.columns(2)

    

    with col1:

        st.subheader("🔍 Drug Network Explorer")

        

        # Add example buttons for network exploration

        st.write("**Try these examples:**")

        col_a, col_b, col_c = st.columns(3)

        with col_a:

            if st.button("🩹 Aspirin Network", help="See how aspirin connects to targets"):

                st.session_state.network_drug_example = "aspirin"

        with col_b:

            if st.button("💊 Morphine Network", help="Explore morphine's target network"):

                st.session_state.network_drug_example = "morphine"

        with col_c:

            if st.button("🧬 Insulin Network", help="View insulin's biological connections"):

                st.session_state.network_drug_example = "insulin"

        

        # Get drug name from input or example

        default_network_value = st.session_state.get('network_drug_example', '')

        drug_name = st.text_input("Enter drug name to explore its network:", value=default_network_value, help="Enter any drug name to see how it connects to biological targets")

        

        if drug_name:

            # Check if a target was clicked to center the network
            center_key = f'main_drug_network_center_{drug_name}'
            center_node = st.session_state.get(center_key, drug_name)
            
            # Debug information
            st.caption(f"🔍 Debug: Center key = '{center_key}', Center node = '{center_node}'")

            if center_node == drug_name:
                # Drug-centered view: show drug in center with its targets
                network_data = app.get_drug_network(drug_name)
            else:
                # Target-centered view: show target in center with all drugs targeting it
                network_data = app.get_target_network(center_node)

            if network_data:

                if center_node == drug_name:
                    st.success(f"Found network for {drug_name}")
                else:
                    st.success(f"Found network for target {center_node}")

                

                # Create network graph using plotly

                nodes = network_data['nodes']

                edges = network_data['edges']

                

                # Prepare data for plotly

                node_x = []

                node_y = []

                node_text = []

                node_color = []

                

                for node in nodes:

                    if center_node == drug_name:
                        # Drug-centered view
                        if node['type'] == 'central_drug':
                            node_x.append(0)
                            node_y.append(0)
                            node_color.append('red')
                        elif node['type'] == 'target':
                            node_x.append(np.cos(len(node_x) * 2 * np.pi / len([n for n in nodes if n['type'] == 'target'])))
                            node_y.append(np.sin(len(node_x) * 2 * np.pi / len([n for n in nodes if n['type'] == 'target'])))
                            node_color.append('blue')
                        else:
                            node_x.append(np.cos(len(node_x) * 2 * np.pi / len([n for n in nodes if n['type'] == 'other_drug'])))
                            node_y.append(np.sin(len(node_x) * 2 * np.pi / len([n for n in nodes if n['type'] == 'other_drug'])))
                            node_color.append('green')
                    else:
                        # Target-centered view
                        if node['type'] == 'central_target':
                            node_x.append(0)
                            node_y.append(0)
                            node_color.append('red')
                        elif node['type'] == 'drug':
                            node_x.append(np.cos(len(node_x) * 2 * np.pi / len([n for n in nodes if n['type'] == 'drug'])))
                            node_y.append(np.sin(len(node_x) * 2 * np.pi / len([n for n in nodes if n['type'] == 'drug'])))
                            node_color.append('green')
                        else:
                            node_x.append(np.cos(len(node_x) * 2 * np.pi / len([n for n in nodes if n['type'] == 'other_target'])))
                            node_y.append(np.sin(len(node_x) * 2 * np.pi / len([n for n in nodes if n['type'] == 'other_target'])))
                            node_color.append('blue')

                    

                    node_text.append(f"{node['label']}<br>Type: {node['type']}")

                

                # Create edge traces

                edge_x = []

                edge_y = []

                for edge in edges:

                    x0, y0 = node_x[edge['source']], node_y[edge['source']]

                    x1, y1 = node_x[edge['target']], node_y[edge['target']]

                    edge_x.extend([x0, x1, None])

                    edge_y.extend([y0, y1, None])

                

                # Create the network plot

                fig = go.Figure()

                

                # Add edges

                fig.add_trace(go.Scatter(

                    x=edge_x, y=edge_y,

                    line=dict(width=0.5, color='#888'),

                    hoverinfo='none',

                    mode='lines'))

                

                # Add nodes

                fig.add_trace(go.Scatter(

                    x=node_x, y=node_y,

                    mode='markers+text',

                    hoverinfo='text',

                    text=[node['label'] for node in nodes],

                    textposition="top center",

                    marker=dict(

                        size=20,

                        color=node_color,

                        line=dict(width=2, color='white')

                    ),

                    textfont=dict(size=10)

                ))

                

                if center_node == drug_name:
                    title_text = f"🕸️ Drug-Centered Network: {drug_name}"
                else:
                    title_text = f"🕸️ Target-Centered Network: {center_node}"
                
                fig.update_layout(
                    title=title_text,
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    height=600
                )

                

                st.plotly_chart(fig, width='stretch')
                
                # Add interactive buttons for network reorientation
                if center_node == drug_name:
                    # Drug-centered view: show target buttons
                    st.markdown("**🎯 Click a target below to center the network on it:**")
                    target_nodes = [n for n in nodes if n['type'] == 'target']
                    if target_nodes:
                        target_cols = st.columns(min(4, len(target_nodes)))
                        for i, target_node in enumerate(target_nodes):
                            with target_cols[i % len(target_cols)]:
                                target_name = target_node['label']
                                if st.button(f"🎯 {target_name}", key=f"center_target_{drug_name}_{target_name}_{i}"):
                                    st.session_state[f'main_drug_network_center_{drug_name}'] = target_name
                                    st.success(f"🎯 Centering network on target: {target_name}")
                                    st.rerun()
                    else:
                        st.info("No targets found for this drug")
                else:
                    # Target-centered view: show drug buttons
                    st.markdown(f"**🎯 Currently centered on: {center_node}**")
                    st.markdown("**💊 Click a drug below to center the network on it:**")
                    drug_nodes = [n for n in nodes if n['type'] == 'drug']
                    if drug_nodes:
                        drug_cols = st.columns(min(4, len(drug_nodes)))
                        for i, drug_node in enumerate(drug_nodes):
                            with drug_cols[i % len(drug_cols)]:
                                drug_name_btn = drug_node['label']
                                button_text = f"💊 {drug_name_btn}" if drug_name_btn != drug_name else f"⭐ {drug_name_btn} (Original)"
                                if st.button(button_text, key=f"center_drug_{drug_name}_{drug_name_btn}_{i}"):
                                    st.session_state[f'main_drug_network_center_{drug_name}'] = drug_name_btn
                                    st.success(f"💊 Centering network on drug: {drug_name_btn}")
                                    st.rerun()
                    else:
                        st.info("No drugs found for this target")
                
                # Add reset button
                reset_text = "🔄 Reset to Drug Center" if center_node != drug_name else "🔄 Reset Network"
                if st.button(reset_text, key=f"reset_main_network_{drug_name}"):
                    if f'main_drug_network_center_{drug_name}' in st.session_state:
                        del st.session_state[f'main_drug_network_center_{drug_name}']
                    st.success("🔄 Reset to drug center")
                    st.rerun()

                # Show network statistics

                st.subheader("📊 Network Statistics")

                col1, col2, col3 = st.columns(3)

                

                with col1:

                    st.metric("Total Nodes", len(nodes))

                with col2:

                    st.metric("Total Edges", len(edges))

                with col3:

                    target_count = len([n for n in nodes if n['type'] == 'target'])

                    st.metric("Targets", target_count)

    

    with col2:

        st.subheader("🌍 Global Network Overview")

        st.write("View the overall drug-target network structure")

        

        if st.button("Generate Global Network"):

            with st.spinner("Generating network visualization..."):

                network_data = app.get_network_data(100)

                if network_data:

                    st.success("Network generated successfully!")

                    

                    # Create a simplified network visualization

                    nodes = network_data['nodes']

                    edges = network_data['edges']

                    

                    # Create a force-directed layout using networkx

                    G = nx.Graph()

                    

                    for node in nodes:

                        G.add_node(node['id'], label=node['label'], type=node['type'])

                    

                    for edge in edges:

                        G.add_edge(edge['source'], edge['target'])

                    

                    # Use spring layout

                    pos = nx.spring_layout(G, k=1, iterations=50)

                    

                    # Create plotly visualization

                    edge_x = []

                    edge_y = []

                    for edge in G.edges():

                        x0, y0 = pos[edge[0]]

                        x1, y1 = pos[edge[1]]

                        edge_x.extend([x0, x1, None])

                        edge_y.extend([y0, y1, None])

                    

                    node_x = []

                    node_y = []

                    node_text = []

                    node_color = []

                    

                    for node in G.nodes():

                        x, y = pos[node]

                        node_x.append(x)

                        node_y.append(y)

                        node_data = G.nodes[node]

                        node_text.append(f"{node_data['label']}<br>Type: {node_data['type']}")

                        

                        if node_data['type'] == 'drug':

                            node_color.append('red')

                        else:

                            node_color.append('blue')

                    

                    fig = go.Figure()

                    

                    # Add edges

                    fig.add_trace(go.Scatter(

                        x=edge_x, y=edge_y,

                        line=dict(width=0.5, color='#888'),

                        hoverinfo='none',

                        mode='lines'))

                    

                    # Add nodes

                    fig.add_trace(go.Scatter(

                        x=node_x, y=node_y,

                        mode='markers',

                        hoverinfo='text',

                        text=node_text,

                        marker=dict(

                            size=8,

                            color=node_color,

                            line=dict(width=1, color='white')

                        )

                    ))

                    

                    fig.update_layout(

                        title="Global Drug-Target Network",

                        showlegend=False,

                        hovermode='closest',

                        margin=dict(b=20,l=5,r=5,t=40),

                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),

                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),

                        height=600

                    )

                    

                    st.plotly_chart(fig, width='stretch')

                    

                    # Show network statistics

                    st.subheader("📊 Global Network Statistics")

                    col1, col2, col3 = st.columns(3)

                    

                    with col1:

                        drug_nodes = len([n for n in nodes if n['type'] == 'drug'])

                        st.metric("Drug Nodes", drug_nodes)

                    with col2:

                        target_nodes = len([n for n in nodes if n['type'] == 'target'])

                        st.metric("Target Nodes", target_nodes)

                    with col3:

                        st.metric("Total Edges", len(edges))



def show_3d_network_visualization(app):

    """Show 3D network visualization"""

    st.header("🎨 3D Network Visualization")

    

    # Add helpful introduction

    st.markdown("""

    **What is 3D network visualization?** Experience drug-target relationships in immersive 3D space!

    

    **How to interact with 3D networks:**

    - 🖱️ **Click and drag** to rotate the view

    - 🔍 **Mouse wheel** to zoom in and out

    - 👆 **Right-click and drag** to pan around

    - 🖱️ **Double-click** to reset the view

    

    **What you'll see:**

    - 🔴 **Red diamonds** = Drugs positioned in outer sphere

    - 🔵 **Blue circles** = Biological targets in inner sphere

    - **Gray lines** = Connections between drugs and targets

    """)

    

    # 3D Network Options

    col1, col2 = st.columns(2)

    

    with col1:

        st.subheader("🔧 3D Network Settings")

        network_size = st.slider("Network Size", min_value=10, max_value=100, value=30, 

                                help="Number of nodes to display (larger = more complex)")

        

        if st.button("🎨 Generate 3D Network", type="primary"):

            with st.spinner("Creating 3D network visualization..."):

                network_data = app.get_3d_network_data(network_size)

                if network_data:

                    st.success("3D Network generated successfully!")

                    

                    # Create 3D scatter plot

                    nodes = network_data['nodes']

                    edges = network_data['edges']

                    

                    # Separate drugs and targets

                    drug_nodes = [n for n in nodes if n['type'] == 'drug']

                    target_nodes = [n for n in nodes if n['type'] == 'target']

                    

                    # Create 3D plot

                    fig = go.Figure()

                    

                    # Add drug nodes

                    if drug_nodes:

                        fig.add_trace(go.Scatter3d(

                            x=[n['x'] for n in drug_nodes],

                            y=[n['y'] for n in drug_nodes],

                            z=[n['z'] for n in drug_nodes],

                            mode='markers+text',

                            name='Drugs',

                            text=[n['label'] for n in drug_nodes],

                            marker=dict(

                                size=8,

                                color='red',

                                symbol='diamond',

                                line=dict(width=2, color='white')

                            ),

                            textposition="top center",

                            textfont=dict(size=8)

                        ))

                    

                    # Add target nodes

                    if target_nodes:

                        fig.add_trace(go.Scatter3d(

                            x=[n['x'] for n in target_nodes],

                            y=[n['y'] for n in target_nodes],

                            z=[n['z'] for n in target_nodes],

                            mode='markers+text',

                            name='Targets',

                            text=[n['label'] for n in target_nodes],

                            marker=dict(

                                size=6,

                                color='blue',

                                symbol='circle',

                                line=dict(width=1, color='white')

                            ),

                            textposition="top center",

                            textfont=dict(size=8)

                        ))

                    

                    # Add edges (connections)

                    edge_x = []

                    edge_y = []

                    edge_z = []

                    

                    for edge in edges:

                        source_node = next(n for n in nodes if n['id'] == edge['source'])

                        target_node = next(n for n in nodes if n['id'] == edge['target'])

                        

                        edge_x.extend([source_node['x'], target_node['x'], None])

                        edge_y.extend([source_node['y'], target_node['y'], None])

                        edge_z.extend([source_node['z'], target_node['z'], None])

                    

                    fig.add_trace(go.Scatter3d(

                        x=edge_x, y=edge_y, z=edge_z,

                        mode='lines',

                        name='Connections',

                        line=dict(width=1, color='rgba(128,128,128,0.6)'),

                        hoverinfo='none'

                    ))

                    

                    # Update layout for 3D

                    fig.update_layout(

                        title=f"3D Drug-Target Network ({len(nodes)} nodes, {len(edges)} connections)",

                        scene=dict(

                            xaxis_title="X",

                            yaxis_title="Y", 

                            zaxis_title="Z",

                            camera=dict(

                                eye=dict(x=1.5, y=1.5, z=1.5)

                            )

                        ),

                        height=700,

                        showlegend=True

                    )

                    

                    st.plotly_chart(fig, width='stretch')

                    

                    # Network statistics

                    st.subheader("📊 3D Network Statistics")

                    col1, col2, col3, col4 = st.columns(4)

                    

                    with col1:

                        st.metric("Total Nodes", len(nodes))

                    with col2:

                        st.metric("Total Edges", len(edges))

                    with col3:

                        drug_count = len([n for n in nodes if n['type'] == 'drug'])

                        st.metric("Drug Nodes", drug_count)

                    with col4:

                        target_count = len([n for n in nodes if n['type'] == 'target'])

                        st.metric("Target Nodes", target_count)

                    

                    # Interactive exploration

                    st.subheader("🔍 Interactive 3D Exploration")

                    st.write("""

                    **How to use the 3D visualization:**

                    - **Rotate:** Click and drag to rotate the view

                    - **Zoom:** Use mouse wheel to zoom in/out

                    - **Pan:** Right-click and drag to pan

                    - **Hover:** Hover over nodes to see labels

                    - **Double-click:** Reset the view

                    """)

                else:

                    st.error("Failed to generate 3D network data.")

    

    with col2:

        st.subheader("🎯 3D Network Features")

        st.markdown("""

        **🌟 What's New in 3D:**

        

        - **🌍 Immersive 3D Space** - Explore networks in three dimensions

        - **🎨 Interactive Controls** - Rotate, zoom, and pan freely

        - **🔍 Enhanced Visibility** - Better node separation and clarity

        - **📊 Spatial Relationships** - See how drugs and targets relate spatially

        - **⚡ Performance Optimized** - Smooth rendering even with large networks

        

        **💡 Use Cases:**

        - **Research Presentations** - Impressive 3D visualizations for demos

        - **Network Analysis** - Better understanding of complex relationships

        - **Drug Discovery** - Spatial insights into target interactions

        - **Educational Purposes** - Engaging way to learn about drug networks

        """)

        

        # Quick 3D demo

        st.subheader("🚀 Quick 3D Demo")

        if st.button("🎬 Show 3D Demo", type="secondary"):

            st.info("🎨 3D visualization is ready! Use the controls on the left to generate your own 3D network.")

            

            # Show sample 3D data structure

            st.code("""

# Sample 3D Network Data Structure

{

    'nodes': [

        {

            'id': 0,

            'label': 'Drug Name',

            'type': 'drug',

            'x': 2.0,  # 3D X coordinate

            'y': 0.0,  # 3D Y coordinate  

            'z': 0.5   # 3D Z coordinate

        }

    ],

    'edges': [

        {

            'source': 0,  # Source node ID

            'target': 1,  # Target node ID

            'type': 'targets'

        }

    ]

}

            """, language="python")



def show_drug_search(app):

    """Show drug search interface"""

    st.header("🔍 Drug Search")

    
    # Initialize drug_details to None to avoid UnboundLocalError
    drug_details = None
    

    # Add helpful introduction

    st.markdown("""

    **What can you do here?** Search for any drug to see detailed information about it.

    

    **Try these examples:** aspirin, insulin, morphine, ibuprofen, metformin

    """)

    

    # Add example buttons

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        if st.button("Try: Aspirin", help="Search for Aspirin"):

            st.session_state.search_example = "aspirin"

    with col2:

        if st.button("Try: Insulin", help="Search for Insulin"):

            st.session_state.search_example = "insulin"

    with col3:

        if st.button("Try: Morphine", help="Search for Morphine"):

            st.session_state.search_example = "morphine"

    with col4:

        if st.button("Try: Metformin", help="Search for Metformin"):

            st.session_state.search_example = "metformin"

    

    # Get search term from input or example

    default_value = st.session_state.get('search_example', '')

    
    search_term = st.text_input("Enter drug name or partial name:", value=default_value, help="You can search for full names or just part of a drug name")

    

    if search_term:

        results = app.search_drugs(search_term, 50)

        

        if results:

            st.success(f"Found {len(results)} drugs matching '{search_term}'")

            

            # Create a DataFrame for better display

            df = pd.DataFrame(results)

            # Streamlit 1.28 requires width as int; use full container width instead
            st.dataframe(df, use_container_width=True)
            
            # Simple summary
            st.info(f"📋 Found {len(results)} drugs. Select one below for detailed information.")
            

            # Allow user to select a drug for detailed view

            selected_drug = st.selectbox("Select a drug for detailed view:", [r['drug'] for r in results])

            

            if selected_drug:

                drug_details = app.get_drug_details(selected_drug)

                if drug_details:

                    # Auto-classify all drug-target relationships if classifier is available

                    if app.classifier and drug_details['targets']:

                        unclassified_targets = []

                        for target in drug_details['targets']:

                            existing = app.classifier.get_existing_classification(selected_drug, target)

                            if not existing or not existing.get('classified', False):

                                unclassified_targets.append(target)

                        

                        if unclassified_targets:

                            # Classify ALL targets automatically - no limit

                            targets_to_classify = unclassified_targets

                            

                            st.info(f"🔄 **Auto-classifying ALL {len(targets_to_classify)} drug-target relationships...** This will take about {len(targets_to_classify) * 3} seconds.")

                            

                            # Progress bar for classification

                            progress_bar = st.progress(0)

                            status_text = st.empty()

                            

                            classified_count = 0

                            for i, target in enumerate(targets_to_classify):

                                status_text.text(f"🧬 Analyzing {selected_drug} → {target}...")

                                

                                try:

                                    classification = app.get_drug_target_classification(selected_drug, target)

                                    if classification:

                                        classified_count += 1

                                except Exception as e:

                                    # Log the error but continue with other classifications

                                    logger.warning(f"Classification failed for {selected_drug} → {target}: {e}")

                                

                                progress_bar.progress((i + 1) / len(targets_to_classify))

                            

                            progress_bar.empty()

                            status_text.empty()

                            

                            if classified_count > 0:

                                st.success(f"✅ **Successfully classified {classified_count}/{len(targets_to_classify)} relationships!** Complete mechanism analysis available below.")

                                if classified_count == len(targets_to_classify):

                                    st.success("🎉 **All classifications completed successfully!**")

                            else:

                                st.warning("⚠️ **Auto-classification encountered issues.** You can manually classify individual relationships below.")

                    

                    st.subheader(f"💊 Comprehensive Details for {selected_drug}")

                    

                    # Basic Drug Information

                    st.markdown("### 📊 **Basic Information**")

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        st.metric("Name", drug_details['drug_info']['name'])

                        st.metric("Development Phase", drug_details['drug_info']['phase'] or 'N/A')

                    with col2:

                        st.metric("Disease Area", drug_details['drug_info']['disease_area'] or 'N/A')

                        st.metric("Purity", drug_details['drug_info']['purity'] or 'N/A')

                    with col3:

                        st.metric("Vendor", drug_details['drug_info']['vendor'] or 'N/A')

                        st.metric("Indication", drug_details['drug_info']['indication'] or 'N/A')

                    

                    # Mechanism of Action

                    st.markdown("### 🔬 **Mechanism of Action (MOA)**")

                    moa = drug_details['drug_info']['moa'] or 'Not specified'

                    st.info(f"**{moa}**")

                    

                    # Add clickable button to search for other drugs with same MOA
                    if moa != 'Not specified':
                        if st.button(f"🔍 **Find Other Drugs with MOA: {moa}**", key=f"search_moa_{moa}_{selected_drug}"):
                            # Store the MOA to search in session state
                            st.session_state.moa_to_search = moa
                            st.session_state.switch_to_moa_analysis = True
                            st.rerun()
                    
                    # Chemical Structure

                    if drug_details['drug_info']['smiles'] and drug_details['drug_info']['smiles'] != 'N/A':

                        st.markdown("### 🧪 **Chemical Structure**")

                        

                        # Show SMILES notation

                        st.markdown("#### 📝 SMILES Notation")
                        st.code(drug_details['drug_info']['smiles'], language='text')
                        st.caption("SMILES notation - textual representation of the molecular structure")

                        

                        # 3D Molecular Visualization

                        st.markdown("#### 🌐 **Interactive 3D Molecular Structure**")

                        

                        try:

                            # Try to create 3D visualization

                            smiles = drug_details['drug_info']['smiles']

                            

                            # Check if RDKit is available

                            if RDKIT_AVAILABLE:

                                try:

                                    # Debug: Show the SMILES string

                                    st.info(f"🔍 **Raw SMILES:** `{smiles[:100]}...`" if len(smiles) > 100 else f"🔍 **Raw SMILES:** `{smiles}`")

                                    

                                    # Clean and process SMILES string

                                    # Handle multiple SMILES separated by commas

                                    smiles_list = [s.strip() for s in smiles.split(',') if s.strip()]

                                    

                                    # Try each SMILES until one works

                                    mol = None

                                    working_smiles = None

                                    

                                    for i, single_smiles in enumerate(smiles_list):

                                        # Clean the SMILES string

                                        cleaned_smiles = single_smiles.replace('-3', '3').replace('-2', '2').replace('-1', '1')

                                        

                                        try:

                                            test_mol = Chem.MolFromSmiles(cleaned_smiles)

                                            if test_mol is not None:

                                                mol = test_mol

                                                working_smiles = cleaned_smiles

                                                st.success(f"✅ **Using SMILES #{i+1}:** `{working_smiles}`")

                                                break

                                        except:

                                            continue

                                    

                                    if mol is None:

                                        st.warning(f"⚠️ Tried {len(smiles_list)} SMILES variants, none could be parsed")

                                        # Show all the SMILES that were tried

                                        st.markdown("##### 🔍 See all SMILES variants tried")
                                        for i, s in enumerate(smiles_list):
                                            st.code(f"{i+1}. {s}")

                                    

                                    # Continue with the working molecule

                                    if mol is not None:

                                        # Add hydrogens and generate 3D coordinates

                                        mol = Chem.AddHs(mol)

                                        AllChem.EmbedMolecule(mol, randomSeed=42)

                                        AllChem.MMFFOptimizeMolecule(mol)

                                        

                                        # Create 3D visualization

                                        st.info("🔬 Rotate, zoom, and explore the 3D molecular structure below:")

                                        

                                        # Convert to mol block for 3D display

                                        mol_block = Chem.MolToMolBlock(mol)

                                        

                                        # Display 3D molecule using py3Dmol directly

                                        try:

                                            import py3Dmol

                                            

                                            # Create enhanced 3D viewer with labels

                                            view = py3Dmol.view(width=600, height=400)

                                            view.addModel(mol_block, 'mol')

                                            

                                            # Enhanced styling with labels and colors

                                            view.setStyle({

                                                'stick': {

                                                    'colorscheme': 'default',

                                                    'radius': 0.15

                                                },

                                                'sphere': {

                                                    'scale': 0.3,

                                                    'colorscheme': 'default'

                                                }

                                            })

                                            

                                            # Add atom labels

                                            view.addStyle({

                                                'stick': {

                                                    'showNonBondedAsSticks': True,

                                                    'colorscheme': 'default'

                                                }

                                            })

                                            

                                            # Add element labels to atoms

                                            view.addPropertyLabels('elem', '', {

                                                'fontColor': 'black',

                                                'fontSize': 12,

                                                'showBackground': False,

                                                'alignment': 'center'

                                            })

                                            

                                            view.setBackgroundColor('white')

                                            view.zoomTo()

                                            

                                            # Show in Streamlit

                                            stmol.showmol(view, height=400, width=600)

                                            

                                        except Exception as py3d_error:

                                            # Fallback: try simpler stmol approach

                                            try:

                                                stmol.showmol(mol_block, height=400, width=600)

                                            except Exception as stmol_error:

                                                st.error(f"3D visualization failed: {py3d_error}")

                                                st.info("💡 **Alternative:** Try the demo molecules below or PubChem search")

                                        

                                        st.success("✅ 3D structure generated from SMILES data")

                                        st.caption("🖱️ **Controls:** Click and drag to rotate, scroll to zoom, right-click to pan")

                                        st.caption("🏷️ **Labels:** Atom symbols shown (C=Carbon, N=Nitrogen, O=Oxygen, etc.)")

                                        st.caption("🎨 **Colors:** Standard CPK coloring (C=gray, N=blue, O=red, H=white)")

                                        

                                        # Show molecular properties

                                        mol_weight = Descriptors.MolWt(mol)

                                        num_atoms = mol.GetNumAtoms()

                                        num_bonds = mol.GetNumBonds()

                                        

                                        col1, col2, col3 = st.columns(3)

                                        with col1:

                                            st.metric("🧮 Molecular Weight", f"{mol_weight:.2f} g/mol")

                                        with col2:

                                            st.metric("⚛️ Number of Atoms", num_atoms)

                                        with col3:

                                            st.metric("🔗 Number of Bonds", num_bonds)

                                        

                                    else:

                                        st.warning("⚠️ Could not parse SMILES notation for 3D visualization")

                                        

                                        # Offer demo molecules

                                        st.info("💡 **Try a demo molecule instead:**")

                                        demo_molecules = {

                                            "Aspirin": "CC(=O)OC1=CC=CC=C1C(=O)O",

                                            "Caffeine": "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",

                                            "Morphine": "CN1CC[C@]23c4c5ccc(O)c4O[C@H]2[C@@H](O)C=C[C@H]3[C@H]1C5",

                                            "Glucose": "C([C@@H]1[C@H]([C@@H]([C@H]([C@H](O1)O)O)O)O)O",

                                            "Benzene": "c1ccccc1"

                                        }

                                        

                                        col1, col2, col3 = st.columns(3)

                                        with col1:

                                            if st.button("🧪 Aspirin", key="demo_aspirin"):

                                                demo_smiles = demo_molecules["Aspirin"]

                                                st.session_state[f'demo_smiles_{selected_drug}'] = demo_smiles

                                        with col2:

                                            if st.button("☕ Caffeine", key="demo_caffeine"):

                                                demo_smiles = demo_molecules["Caffeine"]

                                                st.session_state[f'demo_smiles_{selected_drug}'] = demo_smiles

                                        with col3:

                                            if st.button("💊 Morphine", key="demo_morphine"):

                                                demo_smiles = demo_molecules["Morphine"]

                                                st.session_state[f'demo_smiles_{selected_drug}'] = demo_smiles

                                        

                                        # Check if demo molecule was selected

                                        if f'demo_smiles_{selected_drug}' in st.session_state:

                                            demo_smiles = st.session_state[f'demo_smiles_{selected_drug}']

                                            st.success(f"🧪 **Displaying demo molecule structure**")

                                            

                                            try:

                                                demo_mol = Chem.MolFromSmiles(demo_smiles)

                                                if demo_mol is not None:

                                                    demo_mol = Chem.AddHs(demo_mol)

                                                    AllChem.EmbedMolecule(demo_mol, randomSeed=42)

                                                    AllChem.MMFFOptimizeMolecule(demo_mol)

                                                    

                                                    demo_mol_block = Chem.MolToMolBlock(demo_mol)

                                                    

                                                    # Display demo molecule

                                                    try:

                                                        import py3Dmol

                                                        

                                                        # Create enhanced 3D viewer for demo

                                                        demo_view = py3Dmol.view(width=600, height=400)

                                                        demo_view.addModel(demo_mol_block, 'mol')

                                                        

                                                        # Enhanced styling with labels for demo

                                                        demo_view.setStyle({

                                                            'stick': {

                                                                'colorscheme': 'default',

                                                                'radius': 0.15

                                                            },

                                                            'sphere': {

                                                                'scale': 0.3,

                                                                'colorscheme': 'default'

                                                            }

                                                        })

                                                        

                                                        # Add element labels to demo molecule

                                                        demo_view.addPropertyLabels('elem', '', {

                                                            'fontColor': 'black',

                                                            'fontSize': 12,

                                                            'showBackground': False,

                                                            'alignment': 'center'

                                                        })

                                                        

                                                        demo_view.setBackgroundColor('white')

                                                        demo_view.zoomTo()

                                                        

                                                        # Show in Streamlit

                                                        stmol.showmol(demo_view, height=400, width=600)

                                                        

                                                    except Exception:

                                                        # Fallback for demo

                                                        try:

                                                            stmol.showmol(demo_mol_block, height=400, width=600)

                                                        except Exception as e:

                                                            st.error(f"Demo visualization failed: {e}")

                                                    

                                                    st.caption("🖱️ **Controls:** Click and drag to rotate, scroll to zoom")

                                                    st.caption("📝 This is a demo molecule for visualization purposes")

                                            except Exception as e:

                                                st.error(f"Demo molecule error: {e}")

                                        

                                except Exception as e:

                                    st.error(f"❌ Error generating 3D structure: {str(e)}")

                            else:

                                st.warning(f"📦 3D visualization libraries not available: {RDKIT_ERROR}")

                                st.info("💡 **To enable 3D structures:** pip install rdkit-pypi stmol")

                        

                        except Exception as e:

                            st.warning(f"Chemical structure visualization not available: {e}")

                    else:

                        st.info("🧪 **Chemical structure data not available** in local database")

                        

                        # Try to fetch from PubChem as fallback

                        st.markdown("#### 🌐 **Try PubChem Lookup**")

                        if st.button("🔍 Search PubChem for 3D Structure", key=f"pubchem_{selected_drug}"):

                            try:

                                import requests

                                import time

                                

                                with st.spinner(f"Searching PubChem for {selected_drug}..."):

                                    # Search PubChem for the drug name

                                    search_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{selected_drug}/property/IsomericSMILES/JSON"

                                    

                                    response = requests.get(search_url, timeout=10)

                                    

                                    if response.status_code == 200:

                                        data = response.json()

                                        if 'PropertyTable' in data and 'Properties' in data['PropertyTable']:

                                            smiles = data['PropertyTable']['Properties'][0]['IsomericSMILES']

                                            

                                            st.success(f"✅ Found structure for {selected_drug} in PubChem!")

                                            st.code(smiles, language='text')

                                            st.caption("SMILES from PubChem database")

                                            

                                            # Try to create 3D visualization with PubChem SMILES

                                            if RDKIT_AVAILABLE:

                                                try:

                                                    mol = Chem.MolFromSmiles(smiles)

                                                    if mol is not None:

                                                        mol = Chem.AddHs(mol)

                                                        AllChem.EmbedMolecule(mol, randomSeed=42)

                                                        AllChem.MMFFOptimizeMolecule(mol)

                                                        

                                                        st.info("🔬 3D structure from PubChem data:")

                                                        mol_block = Chem.MolToMolBlock(mol)

                                                        

                                                        # Display PubChem molecule

                                                        try:

                                                            import py3Dmol

                                                            

                                                            # Create enhanced 3D viewer for PubChem data

                                                            pubchem_view = py3Dmol.view(width=600, height=400)

                                                            pubchem_view.addModel(mol_block, 'mol')

                                                            

                                                            # Enhanced styling with labels for PubChem

                                                            pubchem_view.setStyle({

                                                                'stick': {

                                                                    'colorscheme': 'default',

                                                                    'radius': 0.15

                                                                },

                                                                'sphere': {

                                                                    'scale': 0.3,

                                                                    'colorscheme': 'default'

                                                                }

                                                            })

                                                            

                                                            # Add element labels to PubChem molecule

                                                            pubchem_view.addPropertyLabels('elem', '', {

                                                                'fontColor': 'black',

                                                                'fontSize': 12,

                                                                'showBackground': False,

                                                                'alignment': 'center'

                                                            })

                                                            

                                                            pubchem_view.setBackgroundColor('white')

                                                            pubchem_view.zoomTo()

                                                            

                                                            # Show in Streamlit

                                                            stmol.showmol(pubchem_view, height=400, width=600)

                                                            

                                                        except Exception:

                                                            # Fallback for PubChem

                                                            stmol.showmol(mol_block, height=400, width=600)

                                                        

                                                        st.caption("🖱️ **Controls:** Click and drag to rotate, scroll to zoom")

                                                        

                                                except Exception as e:

                                                    st.warning(f"Could not generate 3D structure: {e}")

                                            else:

                                                st.warning("RDKit not available for 3D visualization")

                                        else:

                                            st.warning(f"❌ No structure found for '{selected_drug}' in PubChem")

                                    else:

                                        st.warning(f"❌ PubChem search failed (Status: {response.status_code})")

                                        

                            except requests.exceptions.Timeout:

                                st.error("⏱️ PubChem request timed out. Try again later.")

                            except requests.exceptions.RequestException as e:

                                st.error(f"🌐 Network error: {e}")

                            except Exception as e:

                                st.error(f"❌ Error searching PubChem: {e}")

                        

                        st.caption("💡 **Tip:** PubChem is a free chemistry database with millions of compound structures")

                    

                    # Biological Targets with Mechanism Classification

                    st.markdown("### 🎯 **Biological Targets & Mechanisms**")

                    if drug_details.get('targets'):

                        st.success(f"This drug targets **{len(drug_details['targets'])} biological proteins/receptors**:")

                        

                        # Check if classifier is available

                        if app.classifier:

                            # Count classified vs unclassified targets

                            classified_count = 0

                            for target in drug_details['targets']:

                                existing = app.classifier.get_existing_classification(selected_drug, target)

                                if existing and existing.get('classified', False):

                                    classified_count += 1

                

                if classified_count == len(drug_details['targets']):

                    st.success(f"🔬 **All {classified_count} targets have been classified!** Detailed mechanism insights available below.")

                elif classified_count > 0:

                    st.info(f"🔬 **{classified_count}/{len(drug_details['targets'])} targets classified** - Remaining targets can be manually classified using buttons below.")

                    

                    # Option to classify remaining targets

                    remaining_count = len(drug_details['targets']) - classified_count

                    if remaining_count > 0 and st.button(f"🚀 Classify All {remaining_count} Remaining Targets", type="secondary"):

                        with st.spinner(f"Classifying {remaining_count} remaining targets..."):

                            batch_count = 0

                            for target in drug_details['targets']:

                                existing = app.classifier.get_existing_classification(selected_drug, target)

                                if not existing or not existing.get('classified', False):

                                    try:

                                        classification = app.get_drug_target_classification(selected_drug, target)

                                        if classification:

                                            batch_count += 1

                                    except Exception as e:

                                        logger.warning(f"Batch classification failed for {selected_drug} → {target}: {e}")

                            

                            if batch_count > 0:

                                st.success(f"✅ Successfully classified {batch_count} additional targets!")

                                st.rerun()  # Refresh to show updated classifications

                else:

                    st.info("🔬 **Mechanism classifications available** - Use 'Classify Mechanism' buttons for detailed insights")

            

            # Display targets with expanders for clean organization
            st.markdown("### 🎯 **Biological Targets**")
            st.info("💡 **Click on any target name to see detailed information about that protein/receptor**")
            
            # Show targets in expandable sections
            for target in drug_details['targets']:

                # Check if target has classification
                has_classification = False
                if app.classifier:
                    existing_classification = app.classifier.get_existing_classification(selected_drug, target)
                    has_classification = existing_classification is not None
                
                # Create expander with status indicator
                status_icon = "✅" if has_classification else "⏳"
                with st.expander(f"{status_icon} **{target}** - Click for details"):
                    
                    col1, col2 = st.columns([2, 1])

                    

                    with col1:

                        st.markdown(f"**Target:** {target}")

                        

                        # Add inline target details display
                        if st.button(f"🔍 **Show Drugs Targeting {target}**", key=f"show_target_drugs_{target}_{selected_drug}"):
                            # Show drugs targeting this target inline
                            with st.spinner(f"Loading drugs targeting {target}..."):
                                try:
                                    target_details = app.get_target_details(target)
                                    if target_details and target_details['drugs']:
                                        st.markdown(f"**🎯 Drugs Targeting {target}:**")
                                        
                                        # Create a nice display of drugs targeting this target
                                        drugs_data = []
                                        for drug in target_details['drugs'][:10]:  # Show top 10
                                            drugs_data.append({
                                                'Drug Name': drug['drug_name'],
                                                'MOA': drug['drug_moa'] or 'Not specified',
                                                'Phase': drug['drug_phase'] or 'Unknown',
                                                'Classified': '✅ Yes' if drug['is_classified'] else '⏳ No'
                                            })
                                        
                                        if drugs_data:
                                            drugs_df = pd.DataFrame(drugs_data)
                                            
                                            # Add custom CSS for better table visibility
                                            st.markdown("""
                                            <style>
                                            .drug-table {
                                                background-color: #f8f9fa;
                                                border: 1px solid #dee2e6;
                                                border-radius: 5px;
                                                padding: 10px;
                                                margin: 10px 0;
                                            }
                                            .drug-table th {
                                                background-color: #007bff;
                                                color: white;
                                                padding: 8px;
                                                text-align: left;
                                            }
                                            .drug-table td {
                                                padding: 8px;
                                                border-bottom: 1px solid #dee2e6;
                                            }
                                            </style>
                                            """, unsafe_allow_html=True)
                                            
                                            # Use st.table for better visibility
                                            st.markdown("**📋 Table View:**")
                                            st.table(drugs_df)
                                            
                                            # Alternative markdown display for better visibility
                                            st.markdown("**📝 List View:**")
                                            for i, drug in enumerate(drugs_data, 1):
                                                st.markdown(f"**{i}.** **{drug['Drug Name']}** - {drug['MOA']} - {drug['Phase']} - {drug['Classified']}")
                                            
                                            # Add network visualization
                                            st.markdown("**🕸️ Network Visualization:**")
                                            try:
                                                # Create a simple network graph
                                                import networkx as nx
                                                import plotly.graph_objects as go
                                                
                                                # Create network graph
                                                G = nx.Graph()
                                                
                                                # Add target as central node
                                                G.add_node(target, node_type='target', size=20, color='red')
                                                
                                                # Add drugs as nodes
                                                for drug in drugs_data:
                                                    drug_name = drug['Drug Name']
                                                    G.add_node(drug_name, node_type='drug', size=15, color='blue')
                                                    G.add_edge(target, drug_name)
                                                
                                                # Get positions
                                                pos = nx.spring_layout(G, k=3, iterations=50)
                                                
                                                # Create plotly figure
                                                fig = go.Figure()
                                                
                                                # Add edges
                                                for edge in G.edges():
                                                    x0, y0 = pos[edge[0]]
                                                    x1, y1 = pos[edge[1]]
                                                    fig.add_trace(go.Scatter(
                                                        x=[x0, x1, None],
                                                        y=[y0, y1, None],
                                                        mode='lines',
                                                        line=dict(color='gray', width=2),
                                                        hoverinfo='none',
                                                        showlegend=False
                                                    ))
                                                
                                                # Add nodes
                                                for node in G.nodes():
                                                    x, y = pos[node]
                                                    node_type = G.nodes[node]['node_type']
                                                    color = 'red' if node_type == 'target' else 'blue'
                                                    size = 20 if node_type == 'target' else 15
                                                    
                                                    fig.add_trace(go.Scatter(
                                                        x=[x],
                                                        y=[y],
                                                        mode='markers+text',
                                                        marker=dict(size=size, color=color),
                                                        text=node,
                                                        textposition="middle center",
                                                        textfont=dict(size=10, color='white'),
                                                        hoverinfo='text',
                                                        hovertext=f"{node} ({node_type})",
                                                        showlegend=False
                                                    ))
                                                
                                                # Update layout
                                                fig.update_layout(
                                                    title=f"Drug-Target Network: {target}",
                                                    showlegend=False,
                                                    hovermode='closest',
                                                    margin=dict(b=20,l=5,r=5,t=40),
                                                    annotations=[ dict(
                                                        text="Red: Target, Blue: Drugs",
                                                        showarrow=False,
                                                        xref="paper", yref="paper",
                                                        x=0.005, y=-0.002,
                                                        xanchor='left', yanchor='bottom',
                                                        font=dict(color='gray', size=12)
                                                    )],
                                                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                                    height=400
                                                )
                                                
                                                st.plotly_chart(fig, use_container_width=True)
                                                
                                            except Exception as e:
                                                st.info("Network visualization not available (missing dependencies)")
                                            
                                            if len(target_details['drugs']) > 10:
                                                st.info(f"Showing top 10 of {len(target_details['drugs'])} drugs targeting {target}")
                                        
                                        # Add classification button for this target
                                        unclassified_count = len([d for d in target_details['drugs'] if not d['is_classified']])
                                        if unclassified_count > 0 and app.classifier:
                                            if st.button(f"🔬 Classify All {unclassified_count} Unclassified Drugs for {target}", key=f"classify_all_{target}_{selected_drug}"):
                                                with st.spinner(f"Classifying {unclassified_count} drugs for {target}..."):
                                                    success_count = 0
                                                    error_count = 0
                                                    
                                                    for drug in target_details['drugs']:
                                                        if not drug['is_classified']:
                                                            try:
                                                                classification = app.get_drug_target_classification(drug['drug_name'], target)
                                                                if classification:
                                                                    success_count += 1
                                                                else:
                                                                    error_count += 1
                                                            except Exception as e:
                                                                error_count += 1
                                                    
                                                    st.success(f"✅ Classified {success_count} drugs for {target}")
                                                    if error_count > 0:
                                                        st.warning(f"⚠️ {error_count} drugs failed to classify")
                                    else:
                                        st.info(f"No drugs found targeting {target}")
                                except Exception as e:
                                    st.error(f"Error loading target details: {e}")
                        
                        # Check for existing classification

                        if app.classifier:

                            existing_classification = app.classifier.get_existing_classification(selected_drug, target)

                            

                            if existing_classification:

                                st.success("✅ **Classification Available:**")

                                

                                # Display classification in a nice format

                                col_a, col_b = st.columns(2)

                                with col_a:

                                    st.metric("🔗 Relationship Type", existing_classification['relationship_type'])

                                    st.metric("🧬 Target Class", existing_classification['target_class'])

                                with col_b:

                                    st.metric("⚙️ Mechanism", existing_classification['mechanism'])

                                    st.metric("🎯 Confidence", f"{existing_classification['confidence']:.1%}")

                                

                                st.markdown("**📝 Scientific Reasoning**")
                                st.write(existing_classification['reasoning'])
                                st.caption(f"Source: {existing_classification['source']} | {existing_classification['timestamp'][:10]}")

                            else:

                                st.info("ℹ️ No classification available yet")

                    

                    with col2:

                        if app.classifier:

                            if st.button(f"🔬 Classify Mechanism", key=f"classify_{selected_drug}_{target}"):

                                with st.spinner(f"Classifying {selected_drug} → {target}..."):

                                    classification = app.get_drug_target_classification(selected_drug, target)

                                    

                                    if classification:

                                        st.success("✅ Classification completed!")

                                        st.rerun()  # Refresh to show new classification

                                    else:

                                        st.error("❌ Classification failed. Check logs for details.")

                        else:

                            st.info("🔧 Set GEMINI_API_KEY to enable classification")

            

        else:

            st.warning("No biological targets found in database")

                    

        # Only show additional details if drug_details is available

        if drug_details:

            # Disease Areas and Indications

            col1, col2 = st.columns(2)

            with col1:

                st.markdown("### 🏥 **Disease Areas**")

                if drug_details.get('disease_areas'):

                    for da in drug_details['disease_areas']:

                        st.markdown(f"🏥 {da}")

                else:

                    st.info("No specific disease areas listed")

        

            with col2:

                st.markdown("### 💊 **Medical Indications**")

                if drug_details.get('indications'):

                    for indication in drug_details['indications']:

                        st.markdown(f"💊 {indication}")

                else:

                    st.info("No specific indications listed")

        

            # Vendor Information

            st.markdown("### 🏪 **Supplier/Vendor Information**")

            if drug_details.get('vendors'):

                st.info(f"Available from: **{', '.join(drug_details['vendors'])}**")

            else:

                st.info("No vendor information available")

                    

            # Enhanced Visual Network Graph with Mechanism Labels

            st.markdown("### 🌐 Drug-Target Network")

            if drug_details.get('targets'):

                col_net1, col_net2 = st.columns([3, 1])

                with col_net1:

                    st.info("🎯 **How to read:** Green = Primary effects, Orange = Side effects, Gray = Under analysis. Hover over nodes for details.")

                with col_net2:

                    if st.button("🔄 Refresh", help="Reload network data"):

                        st.rerun()

            

            # Get comprehensive mechanism information for each target

            target_mechanisms = {}

            classification_summary = {

                'Primary/On-Target': 0,

                'Secondary/Off-Target': 0, 

                'Unknown': 0,

                'Unclassified': 0

            }

            

            if app.classifier:

                for target in drug_details['targets']:

                    # Use the same method as target expanders for consistency

                    classification = app.classifier.get_existing_classification(selected_drug, target)

                    

                    if classification:  # If any classification exists, it means it's classified

                        target_mechanisms[target] = {

                            'mechanism': classification.get('mechanism', 'Unknown'),

                            'relationship_type': classification.get('relationship_type', 'Unknown'),

                            'target_class': classification.get('target_class', 'Unknown'),

                            'target_subclass': classification.get('target_subclass', 'Unknown'),

                            'confidence': classification.get('confidence', 0),

                            'reasoning': classification.get('reasoning', 'No reasoning provided'),

                            'classified': True  # If we have classification data, it's classified

                        }

                        rel_type = classification.get('relationship_type', 'Unknown')

                        if rel_type in classification_summary:

                            classification_summary[rel_type] += 1

                        else:

                            classification_summary['Unknown'] += 1

                    else:

                        target_mechanisms[target] = {

                            'mechanism': 'Unclassified',

                            'relationship_type': 'Unclassified',

                            'target_class': 'Unknown',

                            'target_subclass': 'Unknown',

                            'confidence': 0,

                            'reasoning': 'Target not yet analyzed by AI classifier',

                            'classified': False

                        }

                        classification_summary['Unclassified'] += 1

            

            # Show classification summary

            col1, col2, col3, col4 = st.columns(4)

            with col1:

                st.metric("🟢 Primary Effects", classification_summary['Primary/On-Target'])

            with col2:

                st.metric("🟠 Secondary Effects", classification_summary['Secondary/Off-Target'])

            with col3:

                st.metric("⚪ Unknown Type", classification_summary['Unknown'])

            with col4:

                st.metric("⚫ Unclassified", classification_summary['Unclassified'])

            

            # Create enhanced 3D-style network visualization

            import plotly.graph_objects as go

            import math

            import numpy as np

            

            # Interactive network with reorientation capability
            # Check if a target was clicked to center the network
            center_key = f'interactive_network_center_{selected_drug}'
            center_node = st.session_state.get(center_key, selected_drug)
            
            # Store original selected drug for fallback
            if 'original_selected_drug' not in st.session_state:
                st.session_state['original_selected_drug'] = selected_drug
            
            # Start background classification for all targets (only if not already cached)
            uncached_targets = [t for t in drug_details['targets'] if not app.is_cached(selected_drug, t)]
            if uncached_targets:
                app.background_classify_targets(selected_drug, uncached_targets)
            
            if center_node == selected_drug:
                # Drug-centered view: show drug in center with its targets
                targets = drug_details['targets']  # Show ALL targets
                network_data = None
            else:
                # Check if center_node is a drug (from target-centered view drug selection)
                if center_node in [d['drug'] for d in (network_data.get('drugs', []) if network_data else [])]:
                    # Switch to drug-centered view for the selected drug
                    selected_drug = center_node
                    # Get drug details for the new selected drug
                    drug_details = app.get_drug_details(selected_drug)
                    if drug_details:
                        targets = drug_details['targets']
                        network_data = None
                    else:
                        # Fallback to original drug
                        selected_drug = st.session_state.get('original_selected_drug', selected_drug)
                        targets = drug_details['targets']
                        network_data = None
                else:
                    # Target-centered view: show target in center with all drugs targeting it
                    # Use cached network data for faster reorientation
                    cache_key = f"target_network_{center_node}"
                    if cache_key in st.session_state:
                        network_data = st.session_state[cache_key]
                    else:
                        network_data = app.get_target_network_data(center_node)
                        if network_data:
                            st.session_state[cache_key] = network_data
                    
                    if network_data:
                        targets = [center_node]  # The centered target
                    else:
                        targets = drug_details['targets']  # Fallback to drug view
                        center_node = selected_drug
                    st.session_state[center_key] = selected_drug

            if targets:

                # Enhanced layout algorithm based on classification types
                if center_node == selected_drug:
                    # Drug-centered view: position targets around drug
                    drug_x, drug_y = 0, 0
                    target_positions = []
                    
                    # Group targets by classification type for intelligent positioning
                    primary_targets = []
                    secondary_targets = []
                    unknown_targets = []
                    unclassified_targets = []
                    
                    for target in targets:
                        mech_info = target_mechanisms.get(target, {})
                        rel_type = mech_info.get('relationship_type', 'Unclassified')
                        
                        if rel_type == 'Primary/On-Target':
                            primary_targets.append(target)
                        elif rel_type == 'Secondary/Off-Target':
                            secondary_targets.append(target)
                        elif rel_type == 'Unknown':
                            unknown_targets.append(target)
                        else:
                            unclassified_targets.append(target)
                    
                    # Group all targets by type for intelligent positioning
                    all_target_groups = [
                        (primary_targets, 'primary'),
                        (secondary_targets, 'secondary'), 
                        (unknown_targets, 'unknown'),
                        (unclassified_targets, 'unclassified')
                    ]
                    
                    # Calculate dramatic circular layout for maximum visual impact
                    total_targets = len(targets)

                    if total_targets <= 8:
                        # Single ring layout for few targets
                        radius = 6
                    else:
                        # Multi-ring layout for many targets
                        inner_radius = 5
                        outer_radius = 9
                        targets_per_ring = min(10, total_targets // 2)

                    target_index = 0

                    for target_group, group_type in all_target_groups:
                        for target in target_group:
                            if total_targets <= 8:
                                # Single ring layout
                                angle = 2 * math.pi * target_index / total_targets
                                x = radius * math.cos(angle)
                                y = radius * math.sin(angle)
                            else:
                                # Multi-ring layout
                                if target_index < targets_per_ring:
                                    # Inner ring
                                    angle = 2 * math.pi * target_index / targets_per_ring
                                    x = inner_radius * math.cos(angle)
                                    y = inner_radius * math.sin(angle)
                                else:
                                    # Outer ring
                                    outer_index = target_index - targets_per_ring
                                    remaining_targets = total_targets - targets_per_ring
                                    angle = 2 * math.pi * outer_index / remaining_targets
                                    x = outer_radius * math.cos(angle)
                                    y = outer_radius * math.sin(angle)
                            
                            target_positions.append((x, y, target, group_type))
                            target_index += 1
                else:
                    # Target-centered view: position drugs around target
                    drug_x, drug_y = 0, 0  # Target is at center
                    drug_positions = []
                    
                    # Initialize drug classification lists
                    primary_drugs = []
                    secondary_drugs = []
                    unknown_drugs = []
                    unclassified_drugs = []
                    
                    # Classify drugs based on their relationship to the centered target
                    if network_data and 'drugs' in network_data:
                        for drug_info in network_data['drugs']:
                            drug_name = drug_info.get('drug', '')
                            mech_info = target_mechanisms.get(drug_name, {})
                            rel_type = mech_info.get('relationship_type', 'Unclassified')
                            
                            if rel_type == 'Primary/On-Target':
                                primary_drugs.append(drug_name)
                            elif rel_type == 'Secondary/Off-Target':
                                secondary_drugs.append(drug_name)
                            elif rel_type == 'Unknown':
                                unknown_drugs.append(drug_name)
                            else:
                                unclassified_drugs.append(drug_name)
                    
                    # Group all drugs by type for intelligent positioning
                    all_drug_groups = [
                        (primary_drugs, 'primary'),
                        (secondary_drugs, 'secondary'), 
                        (unknown_drugs, 'unknown'),
                        (unclassified_drugs, 'unclassified')
                    ]
                    
                    # Calculate dramatic circular layout for maximum visual impact
                    total_drugs = len(network_data['drugs']) if network_data else 0

                    if total_drugs <= 8:
                        # Single ring layout for few drugs
                        radius = 6
                    else:
                        # Multi-ring layout for many drugs
                        inner_radius = 5
                        outer_radius = 9
                        drugs_per_ring = min(10, total_drugs // 2)

                    drug_index = 0

                    for drug_group, group_type in all_drug_groups:
                        for drug in drug_group:
                            if total_drugs <= 8:
                                # Single ring layout
                                angle = 2 * math.pi * drug_index / total_drugs
                                x = radius * math.cos(angle)
                                y = radius * math.sin(angle)
                            else:
                                # Multi-ring layout
                                if drug_index < drugs_per_ring:
                                    # Inner ring
                                    angle = 2 * math.pi * drug_index / drugs_per_ring
                                    x = inner_radius * math.cos(angle)
                                    y = inner_radius * math.sin(angle)
                                else:
                                    # Outer ring
                                    outer_index = drug_index - drugs_per_ring
                                    remaining_drugs = total_drugs - drugs_per_ring
                                    angle = 2 * math.pi * outer_index / remaining_drugs
                                    x = outer_radius * math.cos(angle)
                                    y = outer_radius * math.sin(angle)
                            
                            drug_positions.append((x, y, drug, group_type))
                            drug_index += 1

                # Create the VIVID, dramatic plot

                fig = go.Figure()

                

                # Add dramatic connection lines with glow effects

                edge_traces = {}  # Group edges by type for legend

                
                # Create edges based on current view
                if center_node == selected_drug:
                    # Drug-centered view: create edges from drug to targets
                    
                    for x, y, target, ring_type in target_positions:
                        # Get comprehensive mechanism info for this target
                        mech_info = target_mechanisms.get(target, {})
                        mechanism = mech_info.get('mechanism', 'Unclassified')
                        
                        try:
                            rel_type = mech_info.get('relationship_type', 'Unclassified')
                            target_class = mech_info.get('target_class', 'Unknown')
                            target_subclass = mech_info.get('target_subclass', 'Unknown')
                            confidence = mech_info.get('confidence', 0)
                            reasoning = mech_info.get('reasoning', 'No details available')
                            classified = mech_info.get('classified', False)
                            

                            # Clean, professional color scheme
                            if rel_type == 'Primary/On-Target':
                                edge_color = '#27AE60'  # Professional green
                                edge_width = 4
                                priority = 'Primary Effect'
                                node_color = '#2ECC71'  # Emerald green
                                glow_color = 'rgba(46, 204, 113, 0.2)'
                            elif rel_type == 'Secondary/Off-Target':
                                edge_color = '#E67E22'  # Professional orange
                                edge_width = 3
                                priority = 'Secondary Effect'
                                node_color = '#F39C12'  # Orange
                                glow_color = 'rgba(243, 156, 18, 0.2)'
                            else:  # Unknown or Unclassified
                                edge_color = '#7F8C8D'  # Professional gray
                                edge_width = 2
                                priority = 'Under Analysis'
                                node_color = '#95A5A6'  # Light gray
                                glow_color = 'rgba(149, 165, 166, 0.2)'

                            # Enhanced hover information with rich formatting
                            hover_text = f"""
                            <b style="font-size:16px; color:{edge_color}">{target}</b><br>
                            <b>Effect Type:</b> <span style="color:{edge_color}">{priority}</span><br>
                            <b>Mechanism:</b> <span style="color:white">{mechanism}</span><br>
                            <b>Confidence:</b> <span style="color:gold">{confidence:.0%}</span><br>
                            <b>Target Class:</b> <span style="color:lightblue">{target_class}</span>
                            """
                            
                            # Add subtle glow effect - much more minimal
                            fig.add_trace(go.Scatter(
                                x=[drug_x, x], y=[drug_y, y],
                                mode='lines',
                                line=dict(color=glow_color, width=edge_width + 2),
                                showlegend=False,
                                hoverinfo='skip'
                            ))

                            # Main connection line with VIVID colors
                            fig.add_trace(go.Scatter(
                                x=[drug_x, x], y=[drug_y, y],
                                mode='lines',
                                line=dict(color=edge_color, width=edge_width),
                                name=priority if priority not in edge_traces else '',
                                showlegend=priority not in edge_traces,
                                legendgroup=priority,
                                hovertemplate=hover_text + '<extra></extra>',
                                hoverinfo='text'
                            ))
                            edge_traces[priority] = True
                            
                        except Exception as e:
                            continue

                    # Add clean mechanism labels - only for primary effects to reduce clutter

                    if mechanism != 'Unclassified' and mechanism != 'Unknown' and rel_type == 'Primary/On-Target':
                        mid_x = (drug_x + x) / 2
                        mid_y = (drug_y + y) / 2
                        
                        # Enhanced mechanism text display with better visibility
                        display_mechanism = mechanism
                        if len(mechanism) > 15:
                            display_mechanism = mechanism[:12] + "..."
                        
                        # Enhanced background for text readability
                        fig.add_trace(go.Scatter(
                            x=[mid_x], y=[mid_y],
                            mode='markers',
                            marker=dict(size=50, color='rgba(255,255,255,0.95)', opacity=0.9, 
                                       line=dict(color=edge_color, width=2)),
                            showlegend=False,
                            hoverinfo='skip'
                        ))
                        
                        fig.add_trace(go.Scatter(
                            x=[mid_x], y=[mid_y],
                            mode='text',
                            text=[display_mechanism],

                            textfont=dict(size=11, color='black', family='Arial'),
                            textposition='middle center',
                            showlegend=False,

                            hovertemplate=f'<b>Mechanism:</b> {mechanism}<br><b>Effect:</b> {priority}<br><b>Confidence:</b> {confidence:.0%}<extra></extra>',
                            hoverinfo='text'

                        ))
                else:
                    # Target-centered view: create edges from target to drugs
                    target_x, target_y = 0, 0  # Target is at center
                    for x, y, drug, ring_type in drug_positions:
                        # Get drug info
                        drug_info = next((d for d in network_data['drugs'] if d['drug'] == drug), {})
                        moa = drug_info.get('moa', 'Unknown')
                        phase = drug_info.get('phase', 'Unknown')
                        
                        # Get mechanism info for this drug-target pair
                        mech_info = app.get_cached_classification(drug, center_node)
                        if not mech_info:
                            # If not cached, use a simple classification based on drug info
                            if phase in ['Approved', 'Phase 4']:
                                rel_type = 'Primary/On-Target'
                                mechanism = 'Approved Drug'
                                confidence = 0.9
                            elif phase in ['Phase 1', 'Phase 2', 'Phase 3']:
                                rel_type = 'Secondary/Off-Target'
                                mechanism = 'Clinical Trial Drug'
                                confidence = 0.7
                            else:
                                rel_type = 'Unclassified'
                                mechanism = 'Unknown'
                                confidence = 0.3
                        else:
                            mechanism = mech_info.get('mechanism', 'Unclassified')
                            rel_type = mech_info.get('relationship_type', 'Unclassified')
                            confidence = mech_info.get('confidence', 0)
                        
                        # Simple classification based on phase and mechanism
                        if rel_type == 'Primary/On-Target':
                            edge_color = '#27AE60'  # Professional green
                            edge_width = 4
                            priority = 'Primary Effect'
                            node_color = '#2ECC71'  # Emerald green
                            glow_color = 'rgba(46, 204, 113, 0.2)'
                        elif rel_type == 'Secondary/Off-Target':
                            edge_color = '#E67E22'  # Professional orange
                            edge_width = 3
                            priority = 'Secondary Effect'
                            node_color = '#F39C12'  # Orange
                            glow_color = 'rgba(243, 156, 18, 0.2)'
                        else:
                            edge_color = '#7F8C8D'  # Professional gray
                            edge_width = 2
                            priority = 'Under Analysis'
                            node_color = '#95A5A6'  # Light gray
                            glow_color = 'rgba(149, 165, 166, 0.2)'
                        
                        # Enhanced hover information
                        hover_text = f"""
                        <b style="font-size:16px; color:{edge_color}">{drug}</b><br>
                        <b>Effect Type:</b> <span style="color:{edge_color}">{priority}</span><br>
                        <b>MOA:</b> <span style="color:white">{moa}</span><br>
                        <b>Phase:</b> <span style="color:gold">{phase}</span><br>
                        <b>Confidence:</b> <span style="color:gold">{confidence:.0%}</span>
                        """
                        
                        # Add subtle glow effect
                        fig.add_trace(go.Scatter(
                            x=[target_x, x], y=[target_y, y],
                            mode='lines',
                            line=dict(color=glow_color, width=edge_width + 2),
                            showlegend=False,
                            hoverinfo='skip'
                        ))
                        
                        # Main connection line
                        fig.add_trace(go.Scatter(
                            x=[target_x, x], y=[target_y, y],
                            mode='lines',
                            line=dict(color=edge_color, width=edge_width),
                            name=priority if priority not in edge_traces else '',
                            showlegend=priority not in edge_traces,
                            legendgroup=priority,
                            hovertemplate=hover_text + '<extra></extra>',
                            hoverinfo='text'
                        ))
                        edge_traces[priority] = True
                    

                # Enhanced VIVID nodes with dramatic glow effects
                if center_node == selected_drug:
                    # Drug-centered view: show target nodes
                    # Collect all annotations first
                    annotations = []
                    
                    for x, y, target, ring_type in target_positions:
                        mech_info = target_mechanisms.get(target, {})
                        rel_type = mech_info.get('relationship_type', 'Unclassified')
                        mechanism = mech_info.get('mechanism', 'Unclassified')
                        confidence = mech_info.get('confidence', 0)

                        # Clean color scheme matching edges
                        if rel_type == 'Primary/On-Target':
                            node_color = '#2ECC71'  # Emerald green
                            border_color = '#27AE60'  # Professional green
                            text_color = 'white'
                            glow_color = 'rgba(46, 204, 113, 0.3)'
                        elif rel_type == 'Secondary/Off-Target':
                            node_color = '#F39C12'  # Orange
                            border_color = '#E67E22'  # Professional orange
                            text_color = 'white'
                            glow_color = 'rgba(243, 156, 18, 0.3)'
                        else:
                            node_color = '#95A5A6'  # Light gray
                            border_color = '#7F8C8D'  # Professional gray
                            text_color = 'white'
                            glow_color = 'rgba(149, 165, 166, 0.3)'

                    

                        # Enhanced hover info with rich styling
                        target_hover = f"""
                        <b style="font-size:18px; color:{border_color}">{target}</b><br>
                        <b>Effect Type:</b> <span style="color:{border_color}">{rel_type}</span><br>
                        <b>Mechanism:</b> <span style="color:white">{mechanism}</span><br>
                        <b>Confidence:</b> <span style="color:gold">{confidence:.0%}</span><br>
                        <b>Target Class:</b> <span style="color:lightblue">{mech_info.get('target_class', 'Unknown')}</span>
                        """
                        
                        # Add subtle glow effect for nodes - single layer
                        fig.add_trace(go.Scatter(
                            x=[x], y=[y],
                            mode='markers',
                            marker=dict(size=65, color=glow_color, opacity=0.4),

                        showlegend=False,

                        hoverinfo='skip'

                    ))

                    

                    # Main target node with clean styling
                    fig.add_trace(go.Scatter(

                        x=[x], y=[y],

                        mode='markers',

                        marker=dict(size=55, color=node_color, 

                                   line=dict(color=border_color, width=3),

                                   opacity=0.9),

                        showlegend=False,

                        hovertemplate=target_hover + '<extra></extra>',

                        hoverinfo='text'

                    ))
                    
                    # Collect annotation for this target
                    annotation = dict(
                        x=x, y=y,
                        text=target.upper(),
                        showarrow=False,
                        font=dict(size=16, color='white', family='Arial Black'),
                        bgcolor='rgba(0,0,0,0.7)',
                        bordercolor='white',
                        borderwidth=1,
                        xref='x', yref='y'
                    )
                    annotations.append(annotation)
                    st.caption(f"DEBUG: Added annotation for {target} at ({x}, {y})")
                    
                    # Add all annotations at once after the loop
                    # MOVED OUTSIDE LOOP - this was the bug!
                    
                    # Store annotations to be added in the final layout update
                    # (Don't call update_layout here - it gets overwritten later)
                else:
                    # Target-centered view: show drug nodes around the target
                    for x, y, drug, ring_type in drug_positions:
                        # Get drug info
                        drug_info = next((d for d in network_data['drugs'] if d['drug'] == drug), {})
                        moa = drug_info.get('moa', 'Unknown')
                        phase = drug_info.get('phase', 'Unknown')
                        
                        # Get mechanism info for this drug-target pair
                        mech_info = app.get_cached_classification(drug, center_node)
                        if not mech_info:
                            # If not cached, use a simple classification based on drug info
                            if phase in ['Approved', 'Phase 4']:
                                rel_type = 'Primary/On-Target'
                            elif phase in ['Phase 1', 'Phase 2', 'Phase 3']:
                                rel_type = 'Secondary/Off-Target'
                            else:
                                rel_type = 'Unclassified'
                        else:
                            rel_type = mech_info.get('relationship_type', 'Unclassified')
                        
                        # Color scheme for drugs
                        if rel_type == 'Primary/On-Target':
                            node_color = '#2ECC71'  # Emerald green
                            border_color = '#27AE60'  # Professional green
                            glow_color = 'rgba(46, 204, 113, 0.3)'
                        elif rel_type == 'Secondary/Off-Target':
                            node_color = '#F39C12'  # Orange
                            border_color = '#E67E22'  # Professional orange
                            glow_color = 'rgba(243, 156, 18, 0.3)'
                        else:
                            node_color = '#95A5A6'  # Light gray
                            border_color = '#7F8C8D'  # Professional gray
                            glow_color = 'rgba(149, 165, 166, 0.3)'
                        
                        # Drug hover info
                        drug_hover = f"""
                        <b style="font-size:18px; color:{border_color}">{drug}</b><br>
                        <b>MOA:</b> <span style="color:white">{moa}</span><br>
                        <b>Phase:</b> <span style="color:gold">{phase}</span><br>
                        <b>Effect Type:</b> <span style="color:{border_color}">{rel_type}</span>
                        """
                        
                        # Add subtle glow effect for drug nodes
                        fig.add_trace(go.Scatter(
                            x=[x], y=[y],
                            mode='markers',
                            marker=dict(size=65, color=glow_color, opacity=0.4),
                            showlegend=False,
                            hoverinfo='skip'
                        ))
                        
                        # Main drug node
                        fig.add_trace(go.Scatter(
                            x=[x], y=[y],
                            mode='markers+text',
                            marker=dict(size=55, color=node_color, 
                                       line=dict(color=border_color, width=3),
                                       opacity=0.9),
                            text=[drug],
                            textposition='middle center',
                            textfont=dict(size=12, color='white', family='Arial Black'),
                            showlegend=False,
                            hovertemplate=drug_hover + '<extra></extra>',
                            hoverinfo='text'
                        ))
                    
                    # Central target node
                    target_hover = f"""
                    <b style="font-size:22px; color:#FF1493">{center_node}</b><br>
                    <b>Total Drugs:</b> <span style="color:gold">{len(network_data['drugs']) if network_data else 0}</span><br>
                    <b>Target Type:</b> <span style="color:lightgreen">Protein</span>
                    """
                    
                    # Target node subtle glow effect
                    fig.add_trace(go.Scatter(
                        x=[target_x], y=[target_y],
                        mode='markers',
                        marker=dict(size=85, color='rgba(231, 76, 60, 0.3)', opacity=0.5),
                        showlegend=False,
                        hoverinfo='skip'
                    ))
                    
                    # Main target node
                    fig.add_trace(go.Scatter(
                        x=[target_x], y=[target_y],
                        mode='markers+text',
                        marker=dict(size=70, color='#E74C3C',  # Red for target
                                   line=dict(color='#C0392B', width=4),
                                   opacity=0.9),
                        text=[center_node.upper()],
                        textposition='middle center',
                        textfont=dict(size=14, color='white', family='Arial'),
                        name='🎯 Target',
                        showlegend=True,
                        hovertemplate=target_hover + '<extra></extra>',
                        hoverinfo='text'
                    ))

                # Enhanced CENTRAL drug node with MASSIVE dramatic effect (only for drug-centered view)
                if center_node == selected_drug:
                    drug_hover = f"""
                    <b style="font-size:22px; color:#FF1493">{selected_drug}</b><br>
                    <b>Total Targets:</b> <span style="color:gold">{len(drug_details['targets'])}</span><br>
                    <b>MOA:</b> <span style="color:lightgreen">{drug_details['drug_info'].get('moa', 'Unknown')}</span><br>
                    <b>Indication:</b> <span style="color:lightblue">{drug_details['drug_info'].get('indication', 'Unknown')}</span>
                    """
                    
                    # Drug node subtle glow effect - single layer
                    fig.add_trace(go.Scatter(
                        x=[drug_x], y=[drug_y],
                        mode='markers',
                        marker=dict(size=85, color='rgba(52, 152, 219, 0.3)', opacity=0.5),
                        showlegend=False,
                        hoverinfo='skip'
                    ))

                    # Main drug node - prominent but not overwhelming
                    fig.add_trace(go.Scatter(
                        x=[drug_x], y=[drug_y],
                        mode='markers+text',
                        marker=dict(size=70, color='#3498DB',  # Professional blue
                                   line=dict(color='#2980B9', width=4),  # Darker blue border
                                   opacity=0.9),
                        text=[selected_drug.upper()],
                        textposition='middle center',
                        textfont=dict(size=14, color='white', family='Arial'),
                        name='💊 Drug',
                        showlegend=True,
                        hovertemplate=drug_hover + '<extra></extra>',
                        hoverinfo='text'
                    ))

                # Clean, professional layout
                # Include annotations in the final layout update
                layout_kwargs = {
                    'title': dict(
                        text=f"Drug-Target Network: {selected_drug}",
                        font=dict(size=20, color='#2C3E50', family='Arial'),
                        x=0.5
                    ),
                    'height': 700,  # Reasonable size
                    'showlegend': True,
                    'legend': dict(
                        x=0.02, y=0.98,
                        bgcolor='rgba(255,255,255,0.95)',
                        bordercolor='#BDC3C7',
                        borderwidth=1,
                        font=dict(size=12, color='#2C3E50', family='Arial')
                    ),
                    'plot_bgcolor': '#F8F9FA',  # Light gray background
                    'paper_bgcolor': 'white',  # White paper
                    'margin': dict(l=50, r=50, t=80, b=50),
                    'xaxis': dict(
                        showgrid=False,
                        zeroline=False, 
                        showticklabels=False,
                        range=[-12, 12],  # Appropriate range
                        scaleratio=1
                    ),
                    'yaxis': dict(
                        showgrid=False,
                        zeroline=False, 
                        showticklabels=False,
                        range=[-10, 10]  # Appropriate range
                    )
                }
                
                # Add annotations if they exist (for drug-centered view)
                if center_node == selected_drug and 'annotations' in locals():
                    layout_kwargs['annotations'] = annotations
                    st.caption(f"DEBUG: Adding {len(annotations)} annotations to layout")

                fig.update_layout(**layout_kwargs)



                # Display the interactive network
                st.plotly_chart(fig, use_container_width=True)
                
                # Add interactive buttons for manual reorientation
                st.markdown("### 🎮 Interactive Controls")
                
                if center_node == selected_drug:
                    # Drug-centered view: show target buttons
                    st.markdown("**🎯 Click a target below to center the network on it:**")
                    if targets:
                        target_cols = st.columns(min(4, len(targets)))
                        for i, target in enumerate(targets):
                            with target_cols[i % len(target_cols)]:
                                if st.button(f"🎯 {target}", key=f"center_target_{selected_drug}_{target}_{i}"):
                                    st.session_state[center_key] = target
                                    st.success(f"🎯 Centering network on target: {target}")
                                    st.rerun()
                    else:
                        st.info("No targets found for this drug")
                else:
                    # Target-centered view: show drug buttons
                    st.markdown(f"**🎯 Currently centered on: {center_node}**")
                    st.markdown("**💊 Click a drug below to center the network on it:**")
                    if network_data and network_data['drugs']:
                        drug_cols = st.columns(min(4, len(network_data['drugs'])))
                        for i, drug in enumerate(network_data['drugs']):
                            with drug_cols[i % len(drug_cols)]:
                                drug_name = drug['drug']
                                button_text = f"💊 {drug_name}" if drug_name != selected_drug else f"⭐ {drug_name} (Original)"
                                if st.button(button_text, key=f"center_drug_{selected_drug}_{drug_name}_{i}"):
                                    st.session_state[center_key] = drug_name
                                    st.success(f"💊 Centering network on drug: {drug_name}")
                                    st.rerun()
                    else:
                        st.info("No drugs found for this target")
                
                # Add reset button
                reset_text = "🔄 Reset to Drug Center" if center_node != selected_drug else "🔄 Reset Network"
                if st.button(reset_text, key=f"reset_interactive_network_{selected_drug}"):
                    if center_key in st.session_state:
                        del st.session_state[center_key]
                    st.success("🔄 Reset to drug center")
                    st.rerun()

                # Clean summary

                st.markdown("### 📊 Network Analysis")



                col1, col2, col3, col4 = st.columns(4)

                with col1:

                    st.metric("🟢 Primary Effects", classification_summary['Primary/On-Target'])

                with col2:

                    st.metric("🟠 Secondary Effects", classification_summary['Secondary/Off-Target'])

                with col3:

                    other_count = classification_summary['Unknown'] + classification_summary['Unclassified']

                    st.metric("🟣 Under Analysis", other_count)

                with col4:

                    total = len(drug_details['targets'])

                    classified = classification_summary['Primary/On-Target'] + classification_summary['Secondary/Off-Target']

                    progress = (classified / total * 100) if total > 0 else 0

                    st.metric("📈 Analysis Progress", f"{progress:.0f}%")



                # Enhanced progress visualization with better messaging

                if progress == 100:

                    st.success("🎉 **COMPLETE ANALYSIS!** All drug-target relationships have been classified with AI-powered mechanism analysis.")

                elif progress > 50:

                    st.info(f"🔄 **Analysis {progress:.0f}% Complete** - {total - classified} targets remaining for comprehensive understanding.")

                else:

                    st.warning(f"📊 **Initial Analysis Phase** - {classified} of {total} targets classified. Additional AI analysis will provide deeper insights.")

            else:

                st.warning("No targets found for this drug.")

        else:

            st.info("No targets available to visualize.")

        

        # Show similar drugs

        if drug_details.get('similar_drugs'):

            st.subheader("🔗 Similar Drugs")

            similar_df = pd.DataFrame(drug_details['similar_drugs'])

            

            # Debug: Show dataframe info

            if not similar_df.empty:

                # Rename columns for better display

                if 'drug' in similar_df.columns:

                    similar_df = similar_df.rename(columns={

                        'drug': 'Drug Name',

                        'moa': 'Mechanism of Action', 

                        'phase': 'Development Phase',

                        'common_targets': 'Shared Targets'

                    })

                

                st.markdown("**Found similar drugs based on shared biological targets:**")

                

                # Use st.table() which should work without styling conflicts

                st.table(similar_df)

                

                # Alternative: Display as formatted text table if st.table still has issues

                st.markdown("---")

                st.markdown("### 📊 **Similar Drugs Details:**")

                

                for idx, row in similar_df.iterrows():

                    st.markdown(f"#### 💊 **{row['Drug Name']}** - {row['Shared Targets']} shared targets")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Drug:** {row['Drug Name']}")
                        st.markdown(f"**Mechanism:** {row['Mechanism of Action']}")
                    with col2:
                        st.markdown(f"**Phase:** {row['Development Phase']}")
                        st.markdown(f"**Shared Targets:** {row['Shared Targets']}")

                        # Add visual indicator for similarity strength

                        shared_count = int(row['Shared Targets'])

                        if shared_count >= 4:

                            st.success("🔥 **High Similarity** - Many shared targets")

                        elif shared_count >= 3:

                            st.info("⭐ **Good Similarity** - Several shared targets")

                        else:

                            st.warning("💡 **Moderate Similarity** - Some shared targets")

                st.caption(f"Found {len(similar_df)} drugs with shared targets")

            else:

                st.info("Similar drugs data is empty")

        else:

            st.info("No similar drugs found.")



def show_target_search(app):

    """Show target search interface"""

    st.header("🎯 Target Search")

    

    # Add helpful introduction

    st.markdown("""

    **What are targets?** Biological targets are proteins, receptors, or enzymes in your body that drugs interact with.

    

    **What can you do here?** Search for any biological target to see which drugs affect it.

    

    **Try these examples:** DRD2 (dopamine receptor), COX1, HTR2A (serotonin receptor), EGFR

    """)

    

    # Add example buttons for targets

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        if st.button("Try: DRD2", help="Dopamine receptor D2"):

            st.session_state.target_search_example = "DRD2"

    with col2:

        if st.button("Try: COX1", help="Cyclooxygenase-1"):

            st.session_state.target_search_example = "COX1"

    with col3:

        if st.button("Try: HTR2A", help="Serotonin receptor 2A"):

            st.session_state.target_search_example = "HTR2A"

    with col4:

        if st.button("Try: EGFR", help="Epidermal growth factor receptor"):

            st.session_state.target_search_example = "EGFR"

    

    # Get search term from input or example

    default_target_value = st.session_state.get('target_search_example', '')

    
    search_term = st.text_input("Enter target name or partial name:", value=default_target_value, help="Search for protein names, receptor names, or enzyme names")

    

    if search_term:

        results = app.search_targets(search_term, 50)

        

        if results:

            st.success(f"Found {len(results)} targets matching '{search_term}'")

            

            # Create a DataFrame for better display

            df = pd.DataFrame(results)

            st.dataframe(df, use_container_width=True)
            

            # Allow user to select a target for detailed view

            selected_target = st.selectbox("Select a target for detailed view:", [r['target'] for r in results])

            

            if selected_target:

                target_details = app.get_target_details(selected_target)

                if target_details:

                    st.subheader(f"🎯 Comprehensive Profile: {selected_target}")

                    

                    # Target Information Section

                    st.markdown("### 📊 **Target Information**")

                    

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        st.metric("🧬 Target Class", target_details['target_info']['primary_class'])

                    with col2:

                        st.metric("🏷️ Target Subclass", target_details['target_info']['primary_subclass'])

                    with col3:

                        st.metric("💊 Targeting Drugs", len(target_details['drugs']))

                    

                    # Classification Progress

                    stats = target_details['classification_stats']

                    if stats['total'] > 0:

                        col_a, col_b = st.columns(2)

                        with col_a:

                            st.metric("✅ Classified Interactions", f"{stats['classified']}/{stats['total']}")

                        with col_b:

                            st.metric("📈 Classification Progress", f"{stats['percentage']:.1f}%")

                        

                        progress = stats['classified'] / stats['total']

                        st.progress(progress)

                    

                    # Drugs Targeting This Target

                    st.markdown("### 💊 **Drugs Targeting This Target**")

                    

                    # Debug: Show what we found
                    st.info(f"Debug: Found {len(target_details['drugs'])} drugs for target {selected_target}")
                    
                    # Add "Classify All" button if there are unclassified drugs
                    unclassified_drugs = [drug for drug in target_details['drugs'] if not drug['is_classified']]
                    if unclassified_drugs and app.classifier:
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            if st.button(f"🔬 **Classify All {len(unclassified_drugs)} Unclassified Drugs**", 
                                       help=f"Classify all {len(unclassified_drugs)} unclassified drug-target relationships for {selected_target}",
                                       type="primary"):
                                with st.spinner(f"Classifying {len(unclassified_drugs)} drugs for {selected_target}... This may take a few minutes."):
                                    success_count = 0
                                    error_count = 0
                                    
                                    # Create progress bar
                                    progress_bar = st.progress(0)
                                    status_text = st.empty()
                                    
                                    for i, drug in enumerate(unclassified_drugs):
                                        status_text.text(f"Classifying {drug['drug_name']} → {selected_target} ({i+1}/{len(unclassified_drugs)})")
                                        
                                        try:
                                            classification = app.get_drug_target_classification(drug['drug_name'], selected_target)
                                            if classification:
                                                success_count += 1
                                            else:
                                                error_count += 1
                                        except Exception as e:
                                            error_count += 1
                                            st.error(f"Error classifying {drug['drug_name']}: {e}")
                                        
                                        # Update progress
                                        progress_bar.progress((i + 1) / len(unclassified_drugs))
                                    
                                    # Show results
                                    status_text.text("Classification complete!")
                                    st.success(f"✅ Successfully classified {success_count} drugs")
                                    if error_count > 0:
                                        st.warning(f"⚠️ {error_count} drugs failed to classify")
                                    
                                    st.info("✅ Classification complete! The results are shown above.")
                                    # Don't rerun - let the user see the results in the current view
                    
                    if target_details['drugs']:

                        # Show a simple table first with better styling
                        drugs_data = []
                        for drug in target_details['drugs']:

                            drugs_data.append({
                                'Drug Name': drug['drug_name'],
                                'MOA': drug['drug_moa'] or 'Not specified',
                                'Phase': drug['drug_phase'] or 'Unknown',
                                'Classified': '✅ Yes' if drug['is_classified'] else '⏳ No'
                            })
                        
                        if drugs_data:
                            # Add some styling to make the table more visible
                            st.markdown("### 📋 **Drugs Table**")
                            st.markdown("**Found drugs targeting this target:**")
                            st.info("💡 **Expand any drug to see detailed information, classify mechanisms, and find related drugs - all in one place!**")
                            
                            # Display drugs with inline expandable information
                            for i, drug in enumerate(target_details['drugs']):
                                # Create expandable section for each drug
                                with st.expander(f"💊 **{drug['drug_name']}** - {drug['drug_phase'] or 'Unknown'} - {drug['drug_moa'] or 'MOA not specified'}", expanded=False):
                                    
                                    # Drug basic info
                                    col1, col2, col3 = st.columns([2, 1, 1])
                                    with col1:
                                        st.markdown(f"**Drug Name:** {drug['drug_name']}")
                                        st.markdown(f"**Phase:** {drug['drug_phase'] or 'Unknown'}")
                                    with col2:
                                        st.markdown(f"**Classification:** {'✅ Classified' if drug['is_classified'] else '⏳ Unclassified'}")
                                    with col3:
                                        if not drug['is_classified'] and app.classifier:
                                            if st.button(f"🔬 Classify", key=f"classify_{drug['drug_name']}_{selected_target}_{i}"):
                                                with st.spinner(f"Classifying {drug['drug_name']} → {selected_target}..."):
                                                    try:
                                                        classification = app.get_drug_target_classification(drug['drug_name'], selected_target)
                                                        if classification:
                                                            st.success(f"✅ Classified: {classification}")
                                                        else:
                                                            st.warning("⚠️ Classification failed")
                                                    except Exception as e:
                                                        st.error(f"❌ Error: {e}")
                                    
                                    # MOA information
                                    moa = drug['drug_moa'] or 'Not specified'
                                    if moa != 'Not specified':
                                        st.markdown(f"**Mechanism of Action:** {moa}")
                                        
                                        # Show other drugs with same MOA
                                        if st.button(f"🔍 Find other drugs with MOA: {moa}", key=f"find_moa_{moa}_{drug['drug_name']}_{i}"):
                                            with st.spinner(f"Finding drugs with MOA: {moa}..."):
                                                try:
                                                    moa_drugs = app.search_drugs_by_moa(moa, 20)
                                                    if moa_drugs:
                                                        st.markdown(f"**Other drugs with MOA '{moa}':**")
                                                        for moa_drug in moa_drugs[:10]:  # Show top 10
                                                            st.markdown(f"• {moa_drug['drug_name']} ({moa_drug['drug_phase'] or 'Unknown'})")
                                                        if len(moa_drugs) > 10:
                                                            st.info(f"... and {len(moa_drugs) - 10} more drugs")
                                                    else:
                                                        st.info(f"No other drugs found with MOA: {moa}")
                                                except Exception as e:
                                                    st.error(f"Error searching MOA: {e}")
                                    else:
                                        st.markdown("**Mechanism of Action:** Not specified")
                                    
                                    # Drug details section
                                    if st.button(f"📋 Show detailed information for {drug['drug_name']}", key=f"details_{drug['drug_name']}_{selected_target}_{i}"):
                                        with st.spinner(f"Loading details for {drug['drug_name']}..."):
                                            try:
                                                # Get detailed drug information
                                                drug_details = app.get_drug_details(drug['drug_name'])
                                                if drug_details:
                                                    st.markdown("**📋 Detailed Drug Information:**")
                                                    
                                                    # Basic info
                                                    col1, col2 = st.columns(2)
                                                    with col1:
                                                        st.markdown(f"**Drug Name:** {drug_details.get('drug_name', 'N/A')}")
                                                        st.markdown(f"**Phase:** {drug_details.get('drug_phase', 'Unknown')}")
                                                        st.markdown(f"**MOA:** {drug_details.get('drug_moa', 'Not specified')}")
                                                    with col2:
                                                        st.markdown(f"**Indication:** {drug_details.get('indication', 'Not specified')}")
                                                        st.markdown(f"**Therapeutic Class:** {drug_details.get('therapeutic_class', 'Not specified')}")
                                                    
                                                    # Targets
                                                    if drug_details.get('targets'):
                                                        st.markdown("**🎯 All Targets:**")
                                                        for target in drug_details['targets'][:5]:  # Show top 5
                                                            st.markdown(f"• {target}")
                                                        if len(drug_details['targets']) > 5:
                                                            st.info(f"... and {len(drug_details['targets']) - 5} more targets")
                                                
                                                else:

                                                    st.info("No detailed information available for this drug")
                                            except Exception as e:
                                                st.error(f"Error loading drug details: {e}")
                        # Duplicate section removed - now handled above with unified information
                        
                        # Add network visualization for all drugs targeting this target
                        st.markdown("### 🕸️ **Interactive Network Visualization**")
                        try:
                            import networkx as nx
                            import plotly.graph_objects as go
                            
                            # Check if a node was clicked to center the network
                            center_key = f'target_network_center_{selected_target}'
                            center_node = st.session_state.get(center_key, selected_target)
                            
                            # Debug information
                            st.caption(f"🔍 Debug: Center key = '{center_key}', Center node = '{center_node}'")
                            
                            # Create network graph
                            G = nx.Graph()
                            
                            if center_node == selected_target:
                                # Target-centered view: show target in center with drugs around it
                                G.add_node(selected_target, node_type='target', size=25, color='red')
                                
                                # Add drugs as nodes with different colors based on classification
                                for drug in target_details['drugs']:
                                    drug_name = drug['drug_name']
                                    node_color = 'green' if drug['is_classified'] else 'orange'
                                    node_size = 20 if drug['is_classified'] else 15
                                    
                                    G.add_node(drug_name, 
                                              node_type='drug', 
                                              size=node_size, 
                                              color=node_color,
                                              moa=drug['drug_moa'] or 'Not specified',
                                              phase=drug['drug_phase'] or 'Unknown',
                                              classified=drug['is_classified'])
                                    G.add_edge(selected_target, drug_name)
                            else:
                                # Drug-centered view: show clicked drug in center with its targets
                                # Get drug details for the centered drug
                                centered_drug = next((d for d in target_details['drugs'] if d['drug_name'] == center_node), None)
                                if centered_drug:
                                    # Add the centered drug as central node
                                    G.add_node(center_node, node_type='drug', size=25, color='purple')
                                    
                                    # Add the original target and other drugs
                                    G.add_node(selected_target, node_type='target', size=20, color='red')
                                    G.add_edge(center_node, selected_target)
                                    
                                    # Add other drugs connected to the same target
                                    for drug in target_details['drugs']:
                                        if drug['drug_name'] != center_node:
                                            drug_name = drug['drug_name']
                                            node_color = 'green' if drug['is_classified'] else 'orange'
                                            node_size = 15 if drug['is_classified'] else 12
                                            
                                            G.add_node(drug_name, 
                                                      node_type='drug', 
                                                      size=node_size, 
                                                      color=node_color,
                                                      moa=drug['drug_moa'] or 'Not specified',
                                                      phase=drug['drug_phase'] or 'Unknown',
                                                      classified=drug['is_classified'])
                                            G.add_edge(selected_target, drug_name)
                            
                            # Get positions
                            pos = nx.spring_layout(G, k=4, iterations=100)
                            
                            # Create plotly figure
                            fig = go.Figure()
                            
                            # Add edges
                            for edge in G.edges():
                                x0, y0 = pos[edge[0]]
                                x1, y1 = pos[edge[1]]
                                fig.add_trace(go.Scatter(
                                    x=[x0, x1, None],
                                    y=[y0, y1, None],
                                    mode='lines',
                                    line=dict(color='lightgray', width=1),
                                    hoverinfo='none',
                                    showlegend=False
                                ))
                            
                            # Add nodes with dynamic centering
                            for node in G.nodes():
                                x, y = pos[node]
                                node_data = G.nodes[node]
                                color = node_data['color']
                                size = node_data['size']
                                node_type = node_data['node_type']
                                
                                # Determine symbol and styling based on node type and if it's the center
                                if node == center_node:
                                    # Center node gets special styling
                                    symbol = 'diamond' if node_type == 'target' else 'star'
                                    text_color = 'white'
                                    text_font = dict(size=12, color=text_color, family="Arial Black")
                                    hover_text = f"⭐ CENTER: {node}<br>Type: {node_type.title()}"
                                    if node_type == 'drug':
                                        hover_text += f"<br>MOA: {node_data['moa']}<br>Phase: {node_data['phase']}<br>Classified: {'Yes' if node_data['classified'] else 'No'}"
                                else:
                                    # Regular nodes
                                    symbol = 'diamond' if node_type == 'target' else 'circle'
                                    text_color = 'white'
                                    text_font = dict(size=8, color=text_color)
                                    if node_type == 'target':
                                        hover_text = f"Target: {node}"
                                    else:
                                        hover_text = f"Drug: {node}<br>MOA: {node_data['moa']}<br>Phase: {node_data['phase']}<br>Classified: {'Yes' if node_data['classified'] else 'No'}"
                                
                                fig.add_trace(go.Scatter(
                                    x=[x],
                                    y=[y],
                                    mode='markers+text',
                                    marker=dict(size=size, color=color, symbol=symbol),
                                    text=node,
                                    textposition="middle center",
                                    textfont=text_font,
                                    hoverinfo='text',
                                    hovertext=hover_text,
                                    showlegend=False
                                ))
                            
                            # Update layout with interactive settings
                            if center_node == selected_target:
                                title_text = f"🕸️ Target-Centered Network: {selected_target}"
                                legend_text = "🔴 Target (Center) | 🟢 Classified Drugs | 🟠 Unclassified Drugs | 💡 Use buttons below to center on different nodes!"
                            else:
                                title_text = f"🕸️ Drug-Centered Network: {center_node} → {selected_target}"
                                legend_text = "⭐ Drug (Center) | 🔴 Target | 🟢 Classified Drugs | 🟠 Unclassified Drugs | 💡 Use buttons below to center on different nodes!"
                            
                            fig.update_layout(
                                title=title_text,
                                showlegend=False,
                                hovermode='closest',
                                dragmode='pan',
                                margin=dict(b=40,l=5,r=5,t=60),
                                annotations=[
                                    dict(
                                        text=legend_text,
                                        showarrow=False,
                                        xref="paper", yref="paper",
                                        x=0.5, y=-0.1,
                                        xanchor='center', yanchor='top',
                                        font=dict(color='gray', size=12)
                                    )
                                ],
                                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                height=500,
                                plot_bgcolor='white'
                            )
                            
                            # Display the interactive chart
                            # Note: Streamlit's Plotly integration doesn't support direct node click handling
                            # We'll use the buttons below for node selection
                            st.plotly_chart(
                                fig, 
                                use_container_width=True, 
                                key=f"target_network_{selected_target}"
                            )
                            
                            # Add clickable buttons below the graph for manual node selection
                            if center_node == selected_target:
                                st.markdown("**💊 Click a drug below to center the network on it:**")
                                if target_details['drugs']:
                                    drug_cols = st.columns(min(4, len(target_details['drugs'])))
                                    for i, drug in enumerate(target_details['drugs']):
                                        with drug_cols[i % len(drug_cols)]:
                                            drug_name = drug['drug_name']
                                            if st.button(f"💊 {drug_name}", key=f"center_drug_{selected_target}_{drug_name}_{i}"):
                                                st.session_state[f'target_network_center_{selected_target}'] = drug_name
                                                st.success(f"🎯 Centering network on: {drug_name}")
                                                st.rerun()
                                else:
                                    st.info("No drugs found for this target")
                            else:
                                st.markdown(f"**🎯 Currently centered on: {center_node}**")
                                st.markdown("**💊 Click a different drug below to center the network on it:**")
                                if target_details['drugs']:
                                    drug_cols = st.columns(min(4, len(target_details['drugs'])))
                                    for i, drug in enumerate(target_details['drugs']):
                                        with drug_cols[i % len(drug_cols)]:
                                            drug_name = drug['drug_name']
                                            button_text = f"💊 {drug_name}" if drug_name != center_node else f"⭐ {drug_name} (Current)"
                                            if st.button(button_text, key=f"center_drug_{selected_target}_{drug_name}_{i}"):
                                                st.session_state[f'target_network_center_{selected_target}'] = drug_name
                                                st.success(f"🎯 Centering network on: {drug_name}")
                                                st.rerun()
                                else:
                                    st.info("No drugs found for this target")
                            
                            # Add reset button
                            reset_text = "🔄 Reset to Target Center" if center_node != selected_target else "🔄 Reset Network"
                            if st.button(reset_text, key=f"reset_target_{selected_target}"):
                                if f'target_network_center_{selected_target}' in st.session_state:
                                    del st.session_state[f'target_network_center_{selected_target}']
                                st.success("🔄 Reset to target center")
                                st.rerun()
                            
                        except Exception as e:
                            st.info("Network visualization not available (missing dependencies)")
                        

                        # Summary Statistics and Visualizations

                        st.markdown("### 📈 **Drug Analysis Summary**")

                        

                        # Create summary DataFrame

                        drugs_df = pd.DataFrame(target_details['drugs'])

                        

                        # Phase distribution

                        col1, col2 = st.columns(2)

                        

                        with col1:

                            if 'drug_phase' in drugs_df.columns:

                                phase_counts = drugs_df['drug_phase'].value_counts()

                                fig_phase = px.pie(values=phase_counts.values, names=phase_counts.index, 

                                                 title=f"Development Phases for {selected_target} Targeting Drugs")

                                st.plotly_chart(fig_phase, width='stretch')

                        

                        with col2:

                            # Mechanism distribution (if classified)

                            classified_df = drugs_df[drugs_df['is_classified'] == True]

                            if not classified_df.empty and 'mechanism' in classified_df.columns:

                                mech_counts = classified_df['mechanism'].value_counts()

                                fig_mech = px.bar(x=mech_counts.index, y=mech_counts.values,

                                                title=f"Mechanisms Targeting {selected_target}",

                                                labels={'x': 'Mechanism', 'y': 'Number of Drugs'})

                                fig_mech.update_layout(xaxis_tickangle=45)

                                st.plotly_chart(fig_mech, width='stretch')

                            else:

                                st.info("📊 Mechanism distribution will appear here after classification")

                        

                        # Detailed table view

                        st.markdown("#### 📋 **Detailed Drug Table**")

                        

                        # Prepare display DataFrame

                        display_cols = ['drug_name', 'drug_moa', 'drug_phase', 'mechanism', 'relationship_type', 'confidence']

                        available_cols = [col for col in display_cols if col in drugs_df.columns]

                        

                        if available_cols:

                            display_df = drugs_df[available_cols].copy()

                            

                            # Format confidence as percentage

                            if 'confidence' in display_df.columns:

                                display_df['confidence'] = display_df['confidence'].apply(

                                    lambda x: f"{x:.1%}" if pd.notna(x) else "N/A"

                                )

                            

                            # Rename columns for display

                            column_names = {

                                'drug_name': 'Drug Name',

                                'drug_moa': 'Drug MOA',

                                'drug_phase': 'Phase',

                                'mechanism': 'Target Mechanism',

                                'relationship_type': 'Relationship',

                                'confidence': 'Confidence'

                            }

                            display_df = display_df.rename(columns=column_names)

                            

                            # Use st.table for better visibility
                            st.table(display_df)
                    else:

                        st.warning("No drugs found targeting this target.")

        else:

            st.info("No targets found matching your search term.")



def show_statistics(app):

    """Show comprehensive statistics"""

    st.header("📊 Comprehensive Statistics")

    

    # Phase statistics

    st.subheader("📈 Drugs by Development Phase")

    phase_stats = app.get_phase_statistics()

    if phase_stats:

        phase_df = pd.DataFrame(phase_stats)

        

        # Create a beautiful bar chart

        fig = px.bar(phase_df, x='phase', y='drug_count', 

                    title="Drug Distribution by Development Phase",

                    color='drug_count',

                    color_continuous_scale='viridis')

        fig.update_layout(

            xaxis_title="Development Phase",

            yaxis_title="Number of Drugs",

            height=500

        )

        st.plotly_chart(fig, width='stretch')

        

        # Show data table

        st.dataframe(phase_df, use_container_width=True)
    

    # MOA statistics

    st.subheader("⚙️ Drugs by Mechanism of Action")

    moa_stats = app.get_moa_statistics()

    if moa_stats:

        moa_df = pd.DataFrame(moa_stats)

        # Show top 15 MOAs

        top_moa = moa_df.head(15)

        

        # Create horizontal bar chart for better readability

        fig = px.bar(top_moa, y='moa', x='drug_count', 

                    title="Top 15 Mechanisms of Action",

                    orientation='h',

                    color='drug_count',

                    color_continuous_scale='plasma')

        fig.update_layout(

            yaxis_title="Mechanism of Action",

            xaxis_title="Number of Drugs",

            height=600

        )

        st.plotly_chart(fig, width='stretch')

        

        # Show data table

        st.dataframe(moa_df, use_container_width=True)
    

    # Top drugs by target count

    st.subheader("🏆 Top Drugs by Number of Targets")

    top_drugs = app.get_top_drugs_by_targets(20)

    if top_drugs:

        top_drugs_df = pd.DataFrame(top_drugs)

        

        # Create a beautiful bar chart

        fig = px.bar(top_drugs_df.head(15), x='drug', y='target_count', 

                    title="Top 15 Drugs by Target Count",

                    color='target_count',

                    color_continuous_scale='inferno')

        fig.update_xaxes(tickangle=45)

        fig.update_layout(

            xaxis_title="Drug Name",

            yaxis_title="Number of Targets",

            height=500

        )

        st.plotly_chart(fig, width='stretch')

        

        # Show data table

        st.dataframe(top_drugs_df, use_container_width=True)
    

    # Top targets by drug count

    st.subheader("🎯 Top Targets by Number of Drugs")

    top_targets = app.get_top_targets_by_drugs(20)

    if top_targets:

        top_targets_df = pd.DataFrame(top_targets)

        

        # Create a beautiful bar chart

        fig = px.bar(top_targets_df.head(15), x='target', y='drug_count', 

                    title="Top 15 Targets by Drug Count",

                    color='drug_count',

                    color_continuous_scale='magma')

        fig.update_xaxes(tickangle=45)

        fig.update_layout(

            xaxis_title="Target Name",

            yaxis_title="Number of Drugs",

            height=500

        )

        st.plotly_chart(fig, width='stretch')

        

        # Show data table

        st.dataframe(top_targets_df, use_container_width=True)


def show_drug_discovery(app):

    """Show enhanced drug discovery insights with interactive tools"""

    st.header("💡 Enhanced Drug Discovery Insights")

    

    # Add introduction to drug discovery tools

    st.markdown("""

    **What is drug discovery?** The process of finding new medicines or new uses for existing medicines.

    

    **How can this tool help?** Use these advanced features to:

    - Find all drugs targeting specific proteins

    - Compare drugs to find similarities

    - Analyze how drugs work through biological pathways

    - Discover opportunities to repurpose existing drugs for new diseases

    """)

    

    # Create tabs for different discovery tools

    tab1, tab2, tab3, tab4 = st.tabs(["🔍 Target-Based Search", "🔗 Drug Comparison", "🔄 Therapeutic Pathways", "📚 Repurposing Insights"])

    

    with tab1:

        st.subheader("🔍 Find Drugs by Target")

        target_name = st.text_input("Enter target name (e.g., DRD2, HTR2A):", key="target_search")

        

        if target_name:

            drugs = search_drugs_by_target(app, target_name)

            if drugs:

                st.success(f"Found {len(drugs)} drugs targeting {target_name}")

                drugs_df = pd.DataFrame(drugs)

                st.dataframe(drugs_df, use_container_width=True)
                

                # Show phase distribution

                if 'phase' in drugs_df.columns:

                    phase_counts = drugs_df['phase'].value_counts()

                    fig = px.pie(values=phase_counts.values, names=phase_counts.index, 

                               title=f"Drugs Targeting {target_name} by Phase")

                    st.plotly_chart(fig, width='stretch')

            else:

                st.info(f"No drugs found targeting {target_name}")

    

    with tab2:

        st.subheader("🔗 Advanced Drug Comparison")

        col1, col2 = st.columns(2)

        

        with col1:

            drug1 = st.text_input("Enter first drug name:", key="drug1_comp")

        

        with col2:

            drug2 = st.text_input("Enter second drug name:", key="drug2_comp")

        

        if drug1 and drug2:

            if st.button("🔍 Compare Drugs", type="primary"):

                with st.spinner("Analyzing drug similarities..."):

                    comparison = app.get_drug_comparison(drug1, drug2)

                    if comparison:

                        st.success(f"Comparison completed! Similarity: {comparison['similarity_score']:.1f}%")

                        

                        # Display comparison metrics

                        col1, col2, col3 = st.columns(3)

                        with col1:

                            st.metric("Drug 1 Targets", len(comparison['drug1_targets']))

                        with col2:

                            st.metric("Drug 2 Targets", len(comparison['drug2_targets']))

                        with col3:

                            st.metric("Common Targets", len(comparison['common_targets']))

                        

                        # Create Venn diagram-like visualization

                        st.subheader("📊 Target Overlap Analysis")

                        

                        # Create comparison chart

                        fig = go.Figure()

                        

                        # Add bars for target counts

                        fig.add_trace(go.Bar(

                            name=drug1,

                            x=['Total Targets', 'Unique Targets', 'Common Targets'],

                            y=[len(comparison['drug1_targets']), len(comparison['drug1_unique']), len(comparison['common_targets'])],

                            marker_color='#ff7f0e'

                        ))

                        

                        fig.add_trace(go.Bar(

                            name=drug2,

                            x=['Total Targets', 'Unique Targets', 'Common Targets'],

                            y=[len(comparison['drug2_targets']), len(comparison['drug2_unique']), len(comparison['common_targets'])],

                            marker_color='#1f77b4'

                        ))

                        

                        fig.update_layout(

                            title=f"Target Comparison: {drug1} vs {drug2}",

                            barmode='group',

                            height=400

                        )

                        

                        st.plotly_chart(fig, width='stretch')

                        

                        # Show detailed breakdown

                        col1, col2 = st.columns(2)

                        with col1:

                            st.subheader(f"🎯 {drug1} Details")

                            st.write(f"**MOA:** {comparison['drug1']['moa']}")

                            st.write(f"**Phase:** {comparison['drug1']['phase']}")

                            st.write(f"**Targets:** {', '.join(comparison['drug1_targets'][:10])}")

                            if len(comparison['drug1_targets']) > 10:

                                st.write(f"... and {len(comparison['drug1_targets']) - 10} more")

                        

                        with col2:

                            st.subheader(f"🎯 {drug2} Details")

                            st.write(f"**MOA:** {comparison['drug2']['moa']}")

                            st.write(f"**Phase:** {comparison['drug2']['phase']}")

                            st.write(f"**Targets:** {', '.join(comparison['drug2_targets'][:10])}")

                            if len(comparison['drug2_targets']) > 10:

                                st.write(f"... and {len(comparison['drug2_targets']) - 10} more")

                    else:

                        st.error("Could not compare drugs. Please check drug names.")

    

    with tab3:

        st.subheader("🔄 Therapeutic Pathway Analysis")

        pathway_drug = st.text_input("Enter drug name for pathway analysis:", key="pathway_drug")

        

        if pathway_drug:

            if st.button("🔍 Analyze Pathways", type="primary"):

                with st.spinner("Analyzing therapeutic pathways..."):

                    pathways = app.get_therapeutic_pathways(pathway_drug)

                    if pathways:

                        st.success(f"Found {pathways['unique_moa']} unique mechanisms of action")

                        

                        # Display pathway information

                        col1, col2 = st.columns(2)

                        with col1:

                            st.metric("Total Targets", pathways['total_targets'])

                        with col2:

                            st.metric("Unique MOAs", pathways['unique_moa'])

                        

                        # Show MOA breakdown

                        st.subheader("⚙️ Mechanisms of Action Breakdown")

                        for moa, targets in pathways['moa_groups'].items():

                            st.markdown(f"#### 🔬 {moa} ({len(targets)} targets)")
                            for target in targets:
                                st.write(f"• **{target['target']}** - Targeted by {target['other_drugs']} other drugs")

                    else:

                        st.error("Could not analyze pathways. Please check drug name.")

    

    with tab4:

        st.subheader("📚 Drug Repurposing Opportunities")

        st.write("""

        This graph database can help identify drug repurposing opportunities by:

        - Finding drugs with similar target profiles

        - Identifying drugs that target multiple related targets

        - Discovering drugs that could be used in combination

        - Understanding drug mechanisms across different therapeutic areas

        """)

        

        # Quick repurposing analysis

        if st.button("🔍 Find Repurposing Candidates", type="secondary"):

            with st.spinner("Analyzing repurposing opportunities..."):

                insights = app.get_drug_repurposing_insights()

                if insights:

                    st.success("Found repurposing insights!")

                    

                    # Show polypharmacology drugs

                    st.subheader("💊 Polypharmacology Drugs (High Repurposing Potential)")

                    poly_df = pd.DataFrame(insights['polypharmacology_drugs'])

                    if not poly_df.empty:

                        fig = px.bar(poly_df.head(10), x='drug', y='target_count',

                                   title="Top 10 Drugs by Target Count",

                                   color='target_count',

                                   color_continuous_scale='viridis')

                        fig.update_xaxes(tickangle=45)

                        st.plotly_chart(fig, width='stretch')



def search_drugs_by_target(app, target_name: str):

    """Helper function to search drugs by target"""

    if not app.driver:

        return []

        

    try:

        with app.driver.session(database=app.database) as session:

            result = session.run("""

                MATCH (d:Drug)-[:TARGETS]->(t:Target {name: $target_name})

                RETURN d.name as drug, d.moa as moa, d.phase as phase

                ORDER BY d.name

            """, target_name=target_name)

            return result.data()

    except Exception as e:

        st.error(f"Error searching drugs by target: {e}")

        return []



def find_common_targets(app, drug1: str, drug2: str):

    """Helper function to find common targets between drugs"""

    if not app.driver:

        return []

        

    try:

        with app.driver.session(database=app.database) as session:

            result = session.run("""

                MATCH (d1:Drug {name: $drug1})-[:TARGETS]->(t:Target)<-[:TARGETS]-(d2:Drug {name: $drug2})

                RETURN t.name as target

                ORDER BY t.name

            """, drug1=drug1, drug2=drug2)

            return result.data()

    except Exception as e:

        st.error(f"Error finding common targets: {e}")

        return []



def show_advanced_analytics(app):

    """Show advanced analytics and insights"""

    st.header("📈 Advanced Analytics & Insights")

    

    # Drug Repurposing Insights

    st.subheader("🔬 Drug Repurposing Opportunities")

    

    if st.button("Generate Repurposing Insights"):

        with st.spinner("Analyzing drug repurposing opportunities..."):

            insights = app.get_drug_repurposing_insights()

            if insights:

                col1, col2 = st.columns(2)

                

                with col1:

                    st.markdown("""

                    <div class="analytics-card">

                        <h3>💊 Polypharmacology Drugs</h3>

                        <p>Drugs targeting multiple targets (potential for repurposing)</p>

                    </div>

                    """, unsafe_allow_html=True)

                    

                    poly_df = pd.DataFrame(insights['polypharmacology_drugs'])

                    if not poly_df.empty:

                        fig = px.bar(poly_df.head(10), x='drug', y='target_count',

                                   title="Top 10 Drugs by Target Count",

                                   color='target_count',

                                   color_continuous_scale='viridis')

                        fig.update_xaxes(tickangle=45)

                        st.plotly_chart(fig, width='stretch')

                

                with col2:

                    st.markdown("""

                    <div class="analytics-card">

                        <h3>🎯 Druggable Targets</h3>

                        <p>Targets with multiple drugs (well-studied pathways)</p>

                    </div>

                    """, unsafe_allow_html=True)

                    

                    target_df = pd.DataFrame(insights['druggable_targets'])

                    if not target_df.empty:

                        fig = px.bar(target_df.head(10), x='target', y='drug_count',

                                   title="Top 10 Targets by Drug Count",

                                   color='drug_count',

                                   color_continuous_scale='plasma')

                        fig.update_xaxes(tickangle=45)

                        st.plotly_chart(fig, width='stretch')

    

    # Drug Similarity Analysis

    st.subheader("🔍 Drug Similarity Analysis")

    drug_name = st.text_input("Enter drug name for similarity analysis:")

    

    if drug_name:

        if st.button("Analyze Drug Similarity"):

            with st.spinner("Analyzing drug similarities..."):

                similarity_data = app.get_drug_similarity_analysis(drug_name)

                if similarity_data:

                    st.success(f"Found {len(similarity_data['similar_drugs'])} similar drugs")

                    

                    # Create similarity heatmap

                    similar_df = pd.DataFrame(similarity_data['similar_drugs'])

                    if not similar_df.empty:

                        # Sort by similarity score

                        similar_df = similar_df.sort_values('similarity_score', ascending=False)

                        

                        # Create similarity chart

                        fig = px.bar(similar_df.head(15), x='similarity_score', y='drug',

                                   title=f"Drug Similarity to {drug_name}",

                                   orientation='h',

                                   color='similarity_score',

                                   color_continuous_scale='inferno')

                        fig.update_layout(

                            xaxis_title="Similarity Score (%)",

                            yaxis_title="Drug Name",

                            height=600

                        )

                        st.plotly_chart(fig, width='stretch')

                        

                        # Show detailed table

                        st.subheader("📋 Similarity Details")

                        st.dataframe(similar_df[['drug', 'moa', 'phase', 'common_targets', 'similarity_score']], 

                                   width='stretch')

    

    # Predictive Insights

    st.subheader("🔮 Predictive Insights")

    

    col1, col2, col3 = st.columns(3)

    

    with col1:

        st.markdown("""

        <div class="insight-card">

            <h3>🎯 Target Validation</h3>

            <p>Targets with multiple drugs are more likely to be druggable</p>

        </div>

        """, unsafe_allow_html=True)

    

    with col2:

        st.markdown("""

        <div class="insight-card">

            <h3>💊 Drug Repurposing</h3>

            <p>Drugs with multiple targets have higher repurposing potential</p>

        </div>

        """, unsafe_allow_html=True)

    

    with col3:

        st.markdown("""

        <div class="insight-card">

            <h3>🔬 Combination Therapy</h3>

            <p>Drugs targeting different targets can be combined for synergy</p>

        </div>

        """, unsafe_allow_html=True)



def show_moa_analysis(app):

    """Show MOA (Mechanism of Action) analysis page"""

    st.header("🧬 Mechanism of Action Analysis")

    

    st.markdown("""

    **Explore drug mechanisms and discover relationships based on how drugs work at the molecular level.**

    

    🔬 **What you can do:**

    - Search drugs by their mechanism of action

    - Analyze therapeutic classes and patterns

    - Find drugs with similar mechanisms

    - Explore MOA statistics and insights

    """)

    

    # MOA Search Section

    st.subheader("🔍 Search by Mechanism of Action")

    

    # MOA search functionality
    col1, col2 = st.columns([2, 1])

    with col1:

        moa_search = st.text_input("Enter mechanism keywords (e.g., 'kinase inhibitor', 'receptor agonist'):")

    with col2:

        st.markdown("**Examples:**")

        if st.button("🧪 Try: kinase inhibitor"):

            st.session_state.moa_search = "kinase inhibitor"

        if st.button("🎯 Try: receptor antagonist"):

            st.session_state.moa_search = "receptor antagonist"

        if st.button("🔬 Try: enzyme inhibitor"):

            st.session_state.moa_search = "enzyme inhibitor"

    

    # Use session state if available

    if 'moa_search' in st.session_state:

        moa_search = st.session_state.moa_search

    

    if moa_search:

        st.success(f"🔍 Searching for drugs with MOA: **{moa_search}**")

        

        drugs_by_moa = app.search_drugs_by_moa(moa_search, 25)

        if drugs_by_moa:

            st.write(f"Found **{len(drugs_by_moa)} drugs** with similar mechanisms:")

            

            # Create DataFrame for better display

            df = pd.DataFrame(drugs_by_moa)

            

            # Format the display

            if not df.empty:

                df['MOA'] = df['moa'].fillna('Unknown')

                df['Phase'] = df['phase'].fillna('Unknown')

                df['Drug Count in MOA'] = df['moa_drug_count'].fillna(0)

                df['Target Diversity'] = df['moa_target_diversity'].fillna(0)

                

                display_df = df[['drug', 'MOA', 'Phase', 'Drug Count in MOA', 'Target Diversity']].copy()

                display_df.columns = ['Drug Name', 'Mechanism of Action', 'Development Phase', 'Drugs in MOA', 'Target Diversity']

                

                st.dataframe(display_df, use_container_width=True)
                

                # MOA Pattern Analysis

                if len(df) > 1:

                    st.subheader("📊 MOA Pattern Analysis")

                    

                    col1, col2 = st.columns(2)

                    with col1:

                        # Phase distribution

                        phase_counts = df['Phase'].value_counts()

                        fig_phase = px.pie(values=phase_counts.values, names=phase_counts.index, 

                                         title="Development Phase Distribution")

                        st.plotly_chart(fig_phase, width='stretch')

                    

                    with col2:

                        # Target diversity analysis

                        if 'Target Diversity' in df.columns:

                            avg_diversity = df['Target Diversity'].mean()

                            max_diversity = df['Target Diversity'].max()

                            st.metric("Average Target Diversity", f"{avg_diversity:.1f}")

                            st.metric("Max Target Diversity", f"{int(max_diversity)}")

        else:

            st.info("No drugs found with that mechanism. Try broader keywords like 'inhibitor' or 'agonist'.")

    

    # Therapeutic Class Analysis

    st.subheader("🏥 Therapeutic Class Overview")

    

    class_analysis = app.get_therapeutic_class_analysis()

    if class_analysis and 'classes' in class_analysis:

        classes_df = pd.DataFrame(class_analysis['classes'])

        if not classes_df.empty:

            classes_df.columns = ['Therapeutic Class', 'MOA Count', 'Drug Count']

            st.dataframe(classes_df, use_container_width=True)
            

            # Visualize therapeutic classes

            fig_classes = px.bar(classes_df, x='Therapeutic Class', y='Drug Count',

                               title="Drugs per Therapeutic Class",

                               color='Drug Count',

                               color_continuous_scale='viridis')

            fig_classes.update_layout(xaxis_tickangle=45)

            st.plotly_chart(fig_classes, width='stretch')

    

    # Top MOAs

    st.subheader("🎯 Top Mechanisms of Action")

    moa_stats = app.get_moa_statistics()

    if moa_stats:

        moa_df = pd.DataFrame(moa_stats)

        if not moa_df.empty:

            # Clean and format the data

            moa_df['MOA'] = moa_df['moa'].fillna('Unknown')

            moa_df['Drug Count'] = moa_df['drug_count'].fillna(0)

            moa_df['Target Count'] = moa_df['target_count'].fillna(0)

            moa_df['Therapeutic Class'] = moa_df['therapeutic_class'].fillna('Unclassified')

            

            display_cols = ['MOA', 'Drug Count', 'Target Count', 'Therapeutic Class']

            st.dataframe(moa_df[display_cols], use_container_width=True)


def show_drug_repurposing(app):

    """Show drug repurposing opportunities page"""

    st.header("🔄 Drug Repurposing Discovery")

    

    st.markdown("""

    **Discover opportunities to repurpose existing drugs for new therapeutic applications.**

    

    💡 **Drug repurposing advantages:**

    - Faster development (skip early safety trials)

    - Lower costs and risks

    - Known safety profiles

    - Potential for breakthrough treatments

    """)

    

    # Repurposing Search Options

    tab1, tab2 = st.tabs(["🎯 Specific Drug", "🌟 Top Opportunities"])

    

    with tab1:

        st.subheader("Find Repurposing Candidates for a Specific Drug")

        

        col1, col2 = st.columns([2, 1])

        with col1:

            drug_name = st.text_input("Enter drug name:")

        with col2:

            st.markdown("**Try these:**")

            if st.button("💊 Aspirin"):

                st.session_state.repurpose_drug = "Aspirin"

            if st.button("🧬 Morphine"):

                st.session_state.repurpose_drug = "Morphine"

            if st.button("💉 Insulin"):

                st.session_state.repurpose_drug = "Insulin"

        

        # Use session state if available

        if 'repurpose_drug' in st.session_state:

            drug_name = st.session_state.repurpose_drug

        

        if drug_name:

            st.success(f"🔍 Finding repurposing opportunities for **{drug_name}**")

            

            # Get similar drugs by MOA

            similar_drugs = app.get_similar_drugs_by_moa(drug_name, 15)

            if similar_drugs:

                st.write(f"**{len(similar_drugs)} drugs** with similar mechanism:")

                

                similar_df = pd.DataFrame(similar_drugs)

                if not similar_df.empty:

                    similar_df.columns = ['Drug', 'MOA', 'Phase', 'Shared Mechanism', 'Target Count']

                    st.dataframe(similar_df, use_container_width=True)
                    

                    # Visualize similar drugs

                    fig_similar = px.scatter(similar_df, x='Target Count', y='Phase',

                                           hover_data=['Drug', 'MOA'],

                                           title=f"Similar Drugs to {drug_name} by Target Count",

                                           size='Target Count',

                                           color='Phase')

                    st.plotly_chart(fig_similar, width='stretch')

            

            # Get specific repurposing candidates

            repurposing_candidates = app.get_repurposing_candidates(drug_name, 10)

            if repurposing_candidates:

                st.subheader("🎯 Direct Repurposing Candidates")

                

                for candidate in repurposing_candidates:

                    st.markdown(f"#### 💊 {candidate['candidate_drug']} (Shared targets: {candidate['shared_targets']})")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Source Drug:** {candidate['source_drug']}")
                        st.write(f"**MOA:** {candidate['source_moa']}")
                        st.write(f"**Phase:** {candidate['source_phase']}")
                    with col2:
                        st.write(f"**Candidate Drug:** {candidate['candidate_drug']}")
                        st.write(f"**MOA:** {candidate['candidate_moa']}")
                        st.write(f"**Phase:** {candidate['candidate_phase']}")
                    st.info(f"🎯 **Shared biological targets:** {candidate['shared_targets']}")

    

    with tab2:

        st.subheader("🌟 Top Repurposing Opportunities")

        st.info("Showing high-potential repurposing opportunities with approved drugs")

        

        top_opportunities = app.get_repurposing_candidates(limit=20)

        if top_opportunities:

            st.write(f"Found **{len(top_opportunities)} repurposing opportunities:**")

            

            opp_df = pd.DataFrame(top_opportunities)

            if not opp_df.empty:

                # Format for display

                display_df = opp_df[['source_drug', 'candidate_drug', 'source_moa', 'candidate_moa', 

                                   'source_phase', 'candidate_phase', 'shared_targets']].copy()

                display_df.columns = ['Source Drug', 'Candidate Drug', 'Source MOA', 'Candidate MOA',

                                    'Source Phase', 'Candidate Phase', 'Shared Targets']

                

                st.dataframe(display_df, use_container_width=True)
                

                # Visualize opportunities

                fig_opp = px.bar(opp_df.head(15), x='shared_targets', y='source_drug',

                               orientation='h',

                               title="Top Repurposing Opportunities by Shared Targets",

                               labels={'shared_targets': 'Number of Shared Targets', 'source_drug': 'Source Drug'})

                st.plotly_chart(fig_opp, width='stretch')

        else:

            st.info("No repurposing opportunities found. This feature requires the enhanced MOA relationships.")

    

    # Repurposing Insights

    st.subheader("📈 Repurposing Insights")

    st.markdown("""

    **Key Repurposing Strategies:**

    

    1. **Target-based repurposing:** Drugs targeting the same proteins

    2. **MOA-based repurposing:** Drugs with similar mechanisms

    3. **Pathway-based repurposing:** Drugs affecting related biological pathways

    4. **Phenotype-based repurposing:** Drugs producing similar therapeutic effects

    """)



def show_mechanism_classification(app):

    """Show mechanism classification management page"""

    st.header("🔬 Drug-Target Mechanism Classification")

    

    st.markdown("""

    **Advanced pharmacological analysis using AI-powered mechanism classification.**

    

    🧬 **3-Level Classification System:**

    - **Level 1:** Relationship Type (Primary/Secondary effects)  

    - **Level 2:** Target Class (Protein, Nucleic Acid, etc.)

    - **Level 3:** Detailed Mechanism (Inhibitor, Agonist, etc.)

    """)

    

    # Check classifier availability

    if not CLASSIFIER_AVAILABLE:

        st.error("🚫 **Mechanism classifier not available.** Install `google-generativeai` to enable this feature.")

        return

    

    if not app.classifier:

        # Try to initialize classifier if we have database connection

        if app.driver and CLASSIFIER_AVAILABLE:

            st.info("🔄 **Initializing AI classifier...** This may take a moment.")

            try:

                # Get current connection details from session state

                if hasattr(st.session_state, 'neo4j_uri') and hasattr(st.session_state, 'neo4j_user'):

                    app.initialize_classifier(

                        st.session_state.neo4j_uri,

                        st.session_state.neo4j_user, 

                        st.session_state.neo4j_password,

                        st.session_state.neo4j_database

                    )

                    if app.classifier:

                        st.success("✅ **AI Classifier ready!** You can now perform mechanism classifications.")

                        st.rerun()

                    else:

                        st.warning("⚠️ **Classifier initialization failed.** Please check your API key setup.")

                else:

                    st.warning("🔌 **Please connect to Neo4j first** to enable AI classification features.")

            except Exception as e:

                st.error(f"❌ **Classifier error:** {e}")

        else:

            st.warning("🔧 **AI Classification temporarily unavailable.** The mechanism classifier is being initialized...")

            st.info("💡 **Tip:** You can still explore existing classifications and use other features while this loads.")

        return

    

    # Classification management interface

    tab1, tab2, tab3 = st.tabs(["🎯 Single Classification", "📊 Batch Processing", "📈 Classification Stats"])

    

    with tab1:

        st.subheader("🎯 Classify Individual Drug-Target Relationship")

        

        col1, col2 = st.columns(2)

        with col1:

            drug_name = st.text_input("Drug Name:", placeholder="e.g., Aspirin")

        with col2:

            target_name = st.text_input("Target Name:", placeholder="e.g., PTGS1")

        

        if drug_name and target_name:

            # Check for existing classification

            existing = app.classifier.get_existing_classification(drug_name, target_name)

            

            if existing:

                st.success("✅ **Existing Classification Found:**")

                

                # Display existing classification

                col_a, col_b, col_c = st.columns(3)

                with col_a:

                    st.metric("🔗 Relationship", existing['relationship_type'])

                    st.metric("🧬 Target Class", existing['target_class'])

                with col_b:

                    st.metric("🏷️ Subclass", existing['target_subclass'])

                    st.metric("⚙️ Mechanism", existing['mechanism'])

                with col_c:

                    st.metric("🎯 Confidence", f"{existing['confidence']:.1%}")

                    st.metric("📅 Date", existing['timestamp'][:10])

                

                st.markdown("**📝 Scientific Reasoning**")
                st.write(existing['reasoning'])

                

                # Reclassify option

                if st.button("🔄 Reclassify", help="Force a new classification"):

                    with st.spinner("Reclassifying..."):

                        new_classification = app.get_drug_target_classification(drug_name, target_name, force_reclassify=True)

                        if new_classification:

                            st.success("✅ Reclassification completed!")

                            st.rerun()

                        else:

                            st.error("❌ Reclassification failed")

            else:

                st.info("ℹ️ No existing classification found")

                

                if st.button("🔬 Classify Relationship", type="primary"):

                    with st.spinner(f"Classifying {drug_name} → {target_name}..."):

                        classification = app.get_drug_target_classification(drug_name, target_name)

                        

                        if classification:

                            st.success("✅ Classification completed!")

                            st.rerun()

                        else:

                            st.error("❌ Classification failed. Check that the drug and target exist in the database.")

    

    with tab2:

        st.subheader("📊 Batch Classification")

        

        drug_for_batch = st.text_input("Drug name for batch classification:", placeholder="e.g., Morphine")

        

        if drug_for_batch:

            if st.button("🚀 Classify All Targets", type="primary"):

                with st.spinner(f"Batch classifying targets for {drug_for_batch}..."):

                    if app.classifier:

                        results = app.classifier.batch_classify_drug_targets(drug_for_batch, limit=10)

                        

                        if results:

                            st.success(f"✅ Classified {len(results)} drug-target relationships!")

                            

                            # Display results in a table

                            results_df = pd.DataFrame(results)

                            if not results_df.empty:

                                display_cols = ['target_name', 'relationship_type', 'target_class', 'mechanism', 'confidence']

                                results_df = results_df[display_cols]

                                results_df.columns = ['Target', 'Relationship', 'Class', 'Mechanism', 'Confidence']

                                results_df['Confidence'] = results_df['Confidence'].apply(lambda x: f"{x:.1%}")

                                

                                st.dataframe(results_df, use_container_width=True)
                        else:

                            st.warning("No unclassified targets found or classification failed")

    

    with tab3:

        st.subheader("📈 Classification Statistics")

        

        if app.driver:

            with app.driver.session(database=app.database) as session:

                # Get classification stats

                stats = session.run("""

                    MATCH ()-[r:TARGETS]->()

                    RETURN 

                        count(r) as total_relationships,

                        count(CASE WHEN r.classified = true THEN 1 END) as classified_relationships,

                        count(CASE WHEN r.classified IS NULL OR r.classified = false THEN 1 END) as unclassified_relationships

                """).single()

                

                if stats:

                    total = stats['total_relationships']

                    classified = stats['classified_relationships']

                    unclassified = stats['unclassified_relationships']

                    

                    col1, col2, col3 = st.columns(3)

                    with col1:

                        st.metric("📊 Total Relationships", total)

                    with col2:

                        st.metric("✅ Classified", classified)

                    with col3:

                        st.metric("⏳ Pending", unclassified)

                    

                    # Progress bar

                    progress = classified / total if total > 0 else 0

                    st.progress(progress)

                    st.caption(f"Classification Progress: {progress:.1%}")

                

                # Classification breakdown

                mechanism_stats = session.run("""

                    MATCH ()-[r:TARGETS]->()

                    WHERE r.classified = true

                    RETURN r.mechanism as mechanism, count(*) as count

                    ORDER BY count DESC

                    LIMIT 10

                """).data()

                

                if mechanism_stats:

                    st.subheader("🔬 Top Mechanisms")

                    mech_df = pd.DataFrame(mechanism_stats)

                    mech_df.columns = ['Mechanism', 'Count']

                    

                    fig = px.bar(mech_df, x='Mechanism', y='Count', 

                               title="Most Common Drug-Target Mechanisms")

                    fig.update_layout(xaxis_tickangle=45)

                    st.plotly_chart(fig, width='stretch')

                else:

                    st.error("❌ **Drug not found or no data available.** Please check the drug name and try again.")

        else:

            st.warning(f"❌ **No drugs found matching '{search_term}'.** This drug may not exist in our database. Please check the spelling or try a different drug name.")

            st.info("💡 **Suggestions:** Try searching for common drugs like 'aspirin', 'morphine', or 'acetaminophen'.")



if __name__ == "__main__":

    main()

