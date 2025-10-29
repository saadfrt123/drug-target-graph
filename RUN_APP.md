# 🚀 Quick Start Guide - Running the App

## ✅ Setup Complete!

Your `drug_cascade_env` conda environment is ready with all dependencies installed!

---

## 📋 Before Running

### 1. Set Your Gemini API Key

**Option A: Create .env file (Recommended)**
```bash
# In your project directory, create .env file
echo GEMINI_API_KEY=your-actual-api-key-here > .env
```

**Option B: Set environment variable**
```powershell
# PowerShell
$env:GEMINI_API_KEY="your-actual-api-key-here"
```

### 2. Ensure Neo4j is Running

- Open Neo4j Desktop (if using local)
- OR verify Neo4j Aura connection (if using cloud)
- Default connection:
  - URI: bolt://127.0.0.1:7687
  - User: neo4j
  - Password: 11223344

---

## 🚀 Running the App

### Step 1: Activate Environment
```bash
conda activate drug_cascade_env
```

### Step 2: Navigate to Project
```bash
cd C:\Users\saad.waseem\drug-target-graph
```

### Step 3: Run Streamlit App
```bash
streamlit run streamlit_app.py
```

The app will open automatically in your browser at: **http://localhost:8501**

---

## 🧪 Testing the New Cascade Feature

Once the app is running:

1. **Navigate to "🌊 Cascade Analysis"** in the sidebar

2. **Go to Settings tab first:**
   - Click **"🔧 Create/Update Cascade Schema"**
   - This creates the required database schema (one-time setup)
   - Wait for success message

3. **Go to "🔍 Predict Cascade" tab:**
   - Select a drug (e.g., "aspirin")
   - Select a target (e.g., "PTGS2")
   - Set depth (try 2 for balanced results)
   - Click **"🤖 Predict Cascade Effects"**
   - Wait 5-15 seconds for AI prediction
   - View results!

4. **Explore other tabs:**
   - **📊 View Existing:** See cached predictions
   - **📈 Statistics:** Analytics dashboard

---

## 📝 Quick Commands Reference

```bash
# Activate environment
conda activate drug_cascade_env

# Run app
streamlit run streamlit_app.py

# Test cascade predictor standalone
python cascade_predictor.py

# Deactivate environment
conda deactivate
```

---

## 🔍 Verifying Installation

Test if everything is installed:

```bash
# Activate environment
conda activate drug_cascade_env

# Check packages
python -c "import streamlit; import neo4j; import google.generativeai; print('✅ All packages installed!')"
```

---

## ⚠️ Troubleshooting

### App won't start
```bash
# Verify you're in the right environment
conda env list

# Verify you're in project directory
pwd

# Check streamlit installation
streamlit --version
```

### "GEMINI_API_KEY not set" error
- Make sure you created the .env file with your API key
- OR set the environment variable in your current session

### Neo4j connection error
- Start Neo4j Desktop
- Verify credentials in config.py match your setup
- Test connection: `python test_connection.py`

### Import errors
- Make sure environment is activated: `conda activate drug_cascade_env`
- Reinstall if needed: `pip install -r requirements.txt`

---

## 📚 Next Steps After Running

1. ✅ Test the cascade prediction with a known drug
2. ✅ Review the CASCADE_PREDICTION_GUIDE.md for detailed usage
3. ✅ Review the DEPLOYMENT_PLAN.md for full testing plan
4. ✅ Validate predictions against literature

---

## 🎯 Implementation Plan Files

For detailed guidance, see:
- **DEPLOYMENT_PLAN.md** - Complete implementation roadmap
- **CASCADE_PREDICTION_GUIDE.md** - User guide with examples
- **IMPLEMENTATION_SUMMARY.md** - Quick reference
- **progress.md** - Technical documentation

---

**Ready to explore drug cascade effects! 🌊🧬**


