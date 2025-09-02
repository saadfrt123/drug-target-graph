import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from neo4j import GraphDatabase
import logging
from typing import List, Dict, Any
import os
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Drug-Target Graph Database",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        border: none;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    .drug-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.8rem;
        border: none;
        margin: 0.5rem 0;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    }
    .target-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.8rem;
        border: none;
        margin: 0.5rem 0;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
    }
    .connection-form {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 1rem;
        color: white;
        margin: 1rem 0;
    }
    .stButton > button {
        border-radius: 0.5rem;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .network-graph {
        border: 2px solid #e0e0e0;
        border-radius: 1rem;
        padding: 1rem;
        background: #f8f9fa;
    }
    .analytics-card {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        border: none;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    .insight-card {
        background: linear-gradient(135deg, #fc466b 0%, #3f5efb 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        border: none;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
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
        
        self.driver = st.session_state.driver
        self.database = st.session_state.database
        
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
        st.header("🔗 Neo4j Connection")
        
        # Get connection details
        col1, col2 = st.columns(2)
        
        with col1:
            uri = st.text_input("Neo4j URI", value="bolt://127.0.0.1:7687", help="Usually bolt://127.0.0.1:7687")
            user = st.text_input("Username", value="neo4j", help="Default username is 'neo4j'")
        
        with col2:
            password = st.text_input("Password", type="password", value="11223344", help="Your Neo4j password")
            database = st.text_input("Database", value="neo4j", help="Usually 'neo4j'")
        
        # Connection buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🧪 Test Connection", type="secondary"):
                try:
                    test_driver = GraphDatabase.driver(uri, auth=(user, password))
                    with test_driver.session(database=database) as session:
                        session.run("RETURN 1").single()
                    test_driver.close()
                    st.success("✅ Connection test successful!")
                except Exception as e:
                    st.error(f"❌ Connection test failed: {e}")
        
        with col2:
            if st.button("🔗 Connect", type="primary"):
                try:
                    # Create driver and test connection
                    test_driver = GraphDatabase.driver(uri, auth=(user, password))
                    with test_driver.session(database=database) as session:
                        session.run("RETURN 1").single()
                    
                    # If successful, store in session state
                    st.session_state.driver = test_driver
                    st.session_state.database = database
                    
                    # Update instance variables
                    self.driver = test_driver
                    self.database = database
                    
                    st.success("✅ Connected successfully!")
                    st.rerun()
                    return True
                except Exception as e:
                    st.error(f"❌ Connection failed: {e}")
                    return False
        
        with col3:
            if st.button("📋 Show Help", type="secondary"):
                st.info("""
                **Connection Help:**
                
                1. **Make sure Neo4j Desktop is running**
                2. **Start your database instance** (should show "Started")
                3. **Check your password** in Neo4j Desktop
                4. **Try the Test Connection button first**
                
                **Common settings:**
                - URI: bolt://127.0.0.1:7687
                - Username: neo4j
                - Password: 11223344 (or your custom password)
                - Database: neo4j
                """)
        
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
        """Get network data for visualization"""
        if not self.driver:
            return None
            
        try:
            with self.driver.session(database=self.database) as session:
                # Get sample drugs and their targets
                result = session.run("""
                    MATCH (d:Drug)-[:TARGETS]->(t:Target)
                    RETURN d.name as drug, d.moa as moa, d.phase as phase, 
                           t.name as target, count(t) as target_count
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
        """Get detailed information about a specific drug"""
        if not self.driver:
            return None
            
        try:
            with self.driver.session(database=self.database) as session:
                # Get drug info
                drug_info = session.run("""
                    MATCH (d:Drug {name: $drug_name})
                    RETURN d.name as name, d.moa as moa, d.phase as phase
                """, drug_name=drug_name).single()
                
                if not drug_info:
                    return None
                    
                # Get targets
                targets = session.run("""
                    MATCH (d:Drug {name: $drug_name})-[:TARGETS]->(t:Target)
                    RETURN t.name as target
                    ORDER BY t.name
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
                    "similar_drugs": similar_drugs
                }
        except Exception as e:
            st.error(f"Error getting drug details: {e}")
            return None
    
    def get_target_details(self, target_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific target"""
        if not self.driver:
            return None
            
        try:
            with self.driver.session(database=self.database) as session:
                # Get drugs targeting this target
                drugs = session.run("""
                    MATCH (d:Drug)-[:TARGETS]->(t:Target {name: $target_name})
                    RETURN d.name as drug, d.moa as moa, d.phase as phase
                    ORDER BY d.name
                """, target_name=target_name).data()
                
                return {
                    "target_name": target_name,
                    "drugs": drugs
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
        """Get statistics by mechanism of action"""
        if not self.driver:
            return []
            
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run("""
                    MATCH (d:Drug)
                    WHERE d.moa IS NOT NULL AND d.moa <> ''
                    RETURN d.moa as moa, count(d) as drug_count
                    ORDER BY drug_count DESC
                    LIMIT 20
                """)
                return result.data()
        except Exception as e:
            st.error(f"Error getting MOA statistics: {e}")
            return []
    
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
        st.info("🔗 Please connect to Neo4j database using the connection form below.")
        st.warning("⚠️ Make sure Neo4j Desktop is running and your database is started!")
        
        # Show connection form in main area if not connected
        app.get_manual_connection()
    else:
        st.success("✅ Connected to Neo4j database successfully!")
        st.info(f"Database: {app.database}")
        
        # Sidebar navigation
        st.sidebar.title("🧭 Navigation")
        
        # Connection status
        st.sidebar.success("✅ Connected to Neo4j")
        
        page = st.sidebar.selectbox(
            "Choose a page:",
            ["🏠 Dashboard", "🔍 Search Drugs", "🎯 Search Targets", "📊 Statistics", "🌐 Network Visualization", "🎨 3D Network", "💡 Drug Discovery", "📈 Advanced Analytics"]
        )
        
        try:
            if page == "🏠 Dashboard":
                show_dashboard(app)
            elif page == "🔍 Search Drugs":
                show_drug_search(app)
            elif page == "🎯 Search Targets":
                show_target_search(app)
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
    st.header("📊 Dashboard Overview")
    
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
    
    # Network options
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔍 Drug Network Explorer")
        drug_name = st.text_input("Enter drug name to explore its network:")
        
        if drug_name:
            network_data = app.get_drug_network(drug_name)
            if network_data:
                st.success(f"Found network for {drug_name}")
                
                # Create network graph using plotly
                nodes = network_data['nodes']
                edges = network_data['edges']
                
                # Prepare data for plotly
                node_x = []
                node_y = []
                node_text = []
                node_color = []
                
                for node in nodes:
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
                
                fig.update_layout(
                    title=f"Network around {drug_name}",
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    height=600
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
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
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
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
    
    st.info("🌐 Explore drug-target relationships in immersive 3D space!")
    
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
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
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
    
    search_term = st.text_input("Enter drug name or partial name:")
    
    if search_term:
        results = app.search_drugs(search_term, 50)
        
        if results:
            st.success(f"Found {len(results)} drugs matching '{search_term}'")
            
            # Create a DataFrame for better display
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)
            
            # Allow user to select a drug for detailed view
            selected_drug = st.selectbox("Select a drug for detailed view:", [r['drug'] for r in results])
            
            if selected_drug:
                drug_details = app.get_drug_details(selected_drug)
                if drug_details:
                    st.subheader(f"📋 Details for {selected_drug}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Name:** {drug_details['drug_info']['name']}")
                        st.write(f"**MOA:** {drug_details['drug_info']['moa']}")
                        st.write(f"**Phase:** {drug_details['drug_info']['phase']}")
                    
                    with col2:
                        st.write(f"**Targets:** {len(drug_details['targets'])}")
                        if drug_details['targets']:
                            st.write(", ".join(drug_details['targets'][:10]))
                            if len(drug_details['targets']) > 10:
                                st.write(f"... and {len(drug_details['targets']) - 10} more")
                    
                    # Show similar drugs
                    if drug_details['similar_drugs']:
                        st.subheader("🔗 Similar Drugs")
                        similar_df = pd.DataFrame(drug_details['similar_drugs'])
                        st.dataframe(similar_df, use_container_width=True)
        else:
            st.info("No drugs found matching your search term.")

def show_target_search(app):
    """Show target search interface"""
    st.header("🎯 Target Search")
    
    search_term = st.text_input("Enter target name or partial name:")
    
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
                    st.subheader(f"📋 Details for {selected_target}")
                    st.write(f"**Target:** {target_details['target_name']}")
                    st.write(f"**Drugs targeting this target:** {len(target_details['drugs'])}")
                    
                    if target_details['drugs']:
                        # Create a DataFrame for better display
                        drugs_df = pd.DataFrame(target_details['drugs'])
                        st.dataframe(drugs_df, use_container_width=True)
                        
                        # Show phase distribution
                        if 'phase' in drugs_df.columns:
                            phase_counts = drugs_df['phase'].value_counts()
                            fig = px.pie(values=phase_counts.values, names=phase_counts.index, 
                                       title="Drugs by Development Phase")
                            st.plotly_chart(fig, use_container_width=True)
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
        st.plotly_chart(fig, use_container_width=True)
        
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
        st.plotly_chart(fig, use_container_width=True)
        
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
        st.plotly_chart(fig, use_container_width=True)
        
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
        st.plotly_chart(fig, use_container_width=True)
        
        # Show data table
        st.dataframe(top_targets_df, use_container_width=True)

def show_drug_discovery(app):
    """Show enhanced drug discovery insights with interactive tools"""
    st.header("💡 Enhanced Drug Discovery Insights")
    
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
                    st.plotly_chart(fig, use_container_width=True)
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
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
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
                            with st.expander(f"🔬 {moa} ({len(targets)} targets)"):
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
                        st.plotly_chart(fig, use_container_width=True)

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
                        st.plotly_chart(fig, use_container_width=True)
                
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
                        st.plotly_chart(fig, use_container_width=True)
    
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
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Show detailed table
                        st.subheader("📋 Similarity Details")
                        st.dataframe(similar_df[['drug', 'moa', 'phase', 'common_targets', 'similarity_score']], 
                                   use_container_width=True)
    
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

if __name__ == "__main__":
    main()
