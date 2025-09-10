#!/usr/bin/env python3
"""
Environment Setup for Drug-Target Mechanism Classification
- Helps users set up Gemini API key
- Tests the classification system
"""

import os
import sys

def setup_gemini_api_key():
    """Guide user through setting up Gemini API key"""
    print("🔬 Drug-Target Mechanism Classification Setup")
    print("=" * 50)
    
    # Check if API key already exists
    existing_key = os.getenv('GEMINI_API_KEY')
    if existing_key:
        print(f"✅ GEMINI_API_KEY is already set: {existing_key[:10]}...")
        return existing_key
    
    print("\n📋 Setup Instructions:")
    print("1. Visit: https://makersuite.google.com/app/apikey")
    print("2. Create a new API key")
    print("3. Copy the API key")
    
    api_key = input("\n🔑 Enter your Gemini API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. Exiting...")
        return None
    
    # Set environment variable for current session
    os.environ['GEMINI_API_KEY'] = api_key
    
    print("\n💾 Setting environment variable...")
    
    # Provide instructions for permanent setup
    print("\n📌 To make this permanent, add to your system:")
    
    if sys.platform.startswith('win'):
        print(f"Windows (Command Prompt): set GEMINI_API_KEY={api_key}")
        print(f"Windows (PowerShell): $env:GEMINI_API_KEY='{api_key}'")
    else:
        print(f"Linux/Mac: export GEMINI_API_KEY={api_key}")
        print("Add this line to your ~/.bashrc or ~/.zshrc file")
    
    return api_key

def test_classification():
    """Test the classification system"""
    print("\n🧪 Testing Classification System...")
    
    try:
        from mechanism_classifier import DrugTargetMechanismClassifier
        
        # Test with example drug-target pair
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("❌ No API key available for testing")
            return
        
        classifier = DrugTargetMechanismClassifier(gemini_api_key=api_key)
        
        print("Testing with example: Aspirin → PTGS1...")
        
        # Test classification (without database storage)
        classification = classifier.classify_drug_target_relationship("Aspirin", "PTGS1", "COX-1 enzyme inhibition")
        
        if classification:
            print("✅ Classification successful!")
            print(f"   Relationship: {classification.relationship_type}")
            print(f"   Target Class: {classification.target_class}")
            print(f"   Mechanism: {classification.mechanism}")
            print(f"   Confidence: {classification.confidence:.1%}")
        else:
            print("❌ Classification failed")
            
    except ImportError:
        print("❌ Classification system not available. Install requirements:")
        print("   pip install google-generativeai")
    except Exception as e:
        print(f"❌ Error during testing: {e}")

def main():
    """Main setup function"""
    print("🚀 Starting Drug-Target Graph Setup...")
    
    # Setup API key
    api_key = setup_gemini_api_key()
    
    if api_key:
        # Test the system
        test_classification()
        
        print("\n🎉 Setup complete! You can now:")
        print("1. Run the Streamlit app: streamlit run streamlit_app.py")
        print("2. Navigate to 'Mechanism Classification' page")
        print("3. Start classifying drug-target relationships!")
    else:
        print("\n⚠️  Setup incomplete. API key required for classification features.")
    
    print("\n📚 For more help, see the README.md file")

if __name__ == "__main__":
    main()

