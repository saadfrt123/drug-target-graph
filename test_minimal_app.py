import streamlit as st

st.title("🧪 Minimal Test App")
st.write("If you can see this, basic Streamlit is working!")

# Test basic imports
try:
    import pandas as pd
    st.success("✅ Pandas imported successfully")
except Exception as e:
    st.error(f"❌ Pandas import failed: {e}")

try:
    import plotly.graph_objects as go
    st.success("✅ Plotly imported successfully")
except Exception as e:
    st.error(f"❌ Plotly import failed: {e}")

try:
    from neo4j import GraphDatabase
    st.success("✅ Neo4j imported successfully")
except Exception as e:
    st.error(f"❌ Neo4j import failed: {e}")

try:
    import networkx as nx
    st.success("✅ NetworkX imported successfully")
except Exception as e:
    st.error(f"❌ NetworkX import failed: {e}")

try:
    import numpy as np
    st.success("✅ NumPy imported successfully")
except Exception as e:
    st.error(f"❌ NumPy import failed: {e}")

try:
    from rdkit import Chem
    st.success("✅ RDKit imported successfully")
except Exception as e:
    st.warning(f"⚠️ RDKit import failed (expected): {e}")

try:
    import stmol
    st.success("✅ stmol imported successfully")
except Exception as e:
    st.warning(f"⚠️ stmol import failed (expected): {e}")

st.write("## 🎯 Test completed!")
st.write("This minimal app tests all major dependencies.")
