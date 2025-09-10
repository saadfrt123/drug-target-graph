# 💊 Drug-Target Graph Database Explorer

An interactive web application for exploring comprehensive drug-target relationships, mechanisms of action, and drug repurposing opportunities using Neo4j graph database technology.

## 🌟 Features

### 🔍 **Drug & Target Search**
- **Comprehensive drug profiles** with MOA, targets, chemical structures, and clinical phases
- **Target analysis** showing all drugs targeting specific proteins
- **Interactive 3D molecular structures** with atom labels and CPK coloring
- **SMILES notation support** with PubChem integration for missing data

### 🧬 **Mechanism of Action (MOA) Analysis**
- **Search by mechanism** - Find drugs by how they work (e.g., "kinase inhibitor")
- **Therapeutic class analysis** - Group drugs by mechanism types
- **MOA statistics** - Drug counts, target diversity, development insights
- **Pattern visualization** - Phase distribution and development trends

### 🔄 **Drug Repurposing Discovery**
- **Find repurposing candidates** based on shared targets and mechanisms
- **Similarity analysis** - Drugs with similar MOAs for new applications
- **Opportunity visualization** - Interactive charts of repurposing potential
- **Risk assessment** - Leverage known safety profiles

### 🌐 **Network Visualization**
- **2D interactive networks** - Clean, readable drug-target relationships
- **3D immersive visualization** - Explore complex networks in 3D space
- **Smart layouts** - Golden angle spiral prevents node overlap
- **Multi-ring displays** - Handle drugs with many targets elegantly

### 📊 **Advanced Analytics**
- **Phase distribution analysis** - Drug development pipeline insights
- **Polypharmacology detection** - Multi-target drug identification
- **Therapeutic pathway analysis** - Biological mechanism exploration
- **Statistical dashboards** - Comprehensive database insights

## 🗃️ Database

### **Comprehensive Dataset**
- **6,798+ drugs** from drug repurposing databases
- **2,183+ biological targets** (proteins, receptors, enzymes)
- **1,433+ mechanisms of action** with therapeutic classifications
- **Complete drug profiles** including vendors, purity, SMILES, indications

### **Rich Relationships**
- **Drug → Target** relationships (TARGETS)
- **Drug → MOA** connections (HAS_MOA)  
- **MOA → Therapeutic Class** classifications (BELONGS_TO_CLASS)
- **Drug similarity** based on mechanisms (SIMILAR_MOA)
- **Repurposing candidates** with shared targets (REPURPOSING_CANDIDATE)
- **Disease/indication** associations (TREATS, BELONGS_TO)

## 🚀 Getting Started

### **Prerequisites**
```bash
# Required software
- Python 3.8+
- Neo4j Database (local or Neo4j Aura cloud)
- Anaconda/Miniconda (recommended)
```

### **Installation**
```bash
# Clone the repository
git clone https://github.com/your-username/drug-target-graph.git
cd drug-target-graph

# Create conda environment
conda create -n drug_graph_env python=3.9
conda activate drug_graph_env

# Install dependencies
pip install -r requirements.txt
```

### **Database Setup**
```bash
# Option 1: Local Neo4j
# 1. Install Neo4j Desktop
# 2. Create a new database with password "11223344"
# 3. Run database setup script
python enhanced_drug_target_graph.py

# Option 2: Neo4j Aura (Cloud) - Recommended for demos
# 1. Create free account at https://neo4j.com/aura/
# 2. Update connection details in the app
# 3. Use the pre-configured cloud database
```

### **Run the Application**
```bash
# Start the Streamlit app
streamlit run streamlit_app.py

# Open your browser to http://localhost:8501
```

## 💻 Usage

### **Connection Setup**
1. **Choose database type**: Local Neo4j or Neo4j Aura (Cloud)
2. **Test connection** before proceeding
3. **Connect** to access all features

### **Key Workflows**

#### 🔍 **Drug Discovery**
```
1. Search Drugs → Enter "Aspirin" → View complete profile
2. Explore 3D structure → Rotate and examine molecular details  
3. Analyze targets → See all biological interactions
4. Find similar drugs → Discover related compounds
```

#### 🧬 **Mechanism Research**
```
1. MOA Analysis → Search "kinase inhibitor"
2. View therapeutic classes → Explore drug categories
3. Analyze patterns → Phase distribution insights
4. Compare mechanisms → Find development opportunities
```

#### 🔄 **Repurposing Research**
```
1. Drug Repurposing → Enter target drug name
2. Find candidates → Shared targets and mechanisms
3. Assess opportunities → Known safety profiles
4. Visualize potential → Interactive opportunity charts
```

#### 🌐 **Network Exploration**
```
1. Network Visualization → Select drugs/targets
2. Explore 2D networks → Clean, readable layouts
3. Immerse in 3D → Comprehensive relationship view
4. Analyze connectivity → Multi-target insights
```

## 🛠️ Technical Stack

- **Frontend**: Streamlit (Python web framework)
- **Visualization**: Plotly (interactive charts), py3Dmol (3D molecules)
- **Database**: Neo4j (graph database)
- **Chemistry**: RDKit (molecular operations), stmol (3D structures)
- **Data**: Pandas (manipulation), NumPy (computations)
- **Network**: NetworkX (graph algorithms)

## 📁 Project Structure

```
drug-target-graph/
├── streamlit_app.py              # Main application
├── enhanced_drug_target_graph.py # Database setup script
├── enhanced_moa_relationships.py # MOA enhancement script
├── transfer_moa_to_cloud.py      # Cloud sync script
├── requirements.txt              # Python dependencies
├── config.py                     # Database configuration
├── Repurposing_Hub_export (1).txt # Source data
└── README.md                     # This file
```

## 🌐 Deployment

### **Streamlit Cloud (Recommended)**
```bash
# 1. Push to GitHub
git add .
git commit -m "Deploy drug discovery platform"
git push origin main

# 2. Deploy on Streamlit Cloud
# - Connect GitHub repository
# - Set main file: streamlit_app.py
# - Deploy automatically
```

### **Local Demo**
- Perfect for development and presentations
- Full 3D visualization support
- Fast performance with local database

## 📊 Demo Scenarios

### **For Researchers**
- **Target validation**: Find all drugs targeting EGFR
- **MOA analysis**: Compare kinase inhibitors vs receptor agonists
- **Repurposing**: Discover new applications for approved drugs

### **For Pharmaceutical Companies**
- **Pipeline analysis**: Drug development phase distribution
- **Competitive intelligence**: Mechanism landscape mapping
- **Partnership opportunities**: Shared target identification

### **For Educators**
- **Drug discovery education**: Interactive learning platform
- **Mechanism visualization**: 3D molecular structures
- **Network analysis**: Graph-based relationship exploration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Drug Repurposing Hub** - Source dataset
- **Neo4j** - Graph database technology
- **Streamlit** - Web application framework
- **RDKit** - Cheminformatics toolkit
- **Plotly** - Interactive visualizations

## 📞 Support

For questions, issues, or contributions:
- 📧 **Email**: your-email@example.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/your-username/drug-target-graph/issues)
- 📖 **Documentation**: [Project Wiki](https://github.com/your-username/drug-target-graph/wiki)

---

**🎯 Accelerate drug discovery through interactive graph exploration!** ⚡