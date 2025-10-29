#!/usr/bin/env python3
"""
Simple test script for cascade prediction setup - Windows compatible
"""
import os
import sys
from cascade_predictor import BiologicalCascadePredictor
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE

# Set UTF-8 encoding for Windows console
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def main():
    print("\n=== Cascade Prediction Setup ===\n")
    
    # Get API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("ERROR: GEMINI_API_KEY not found in environment")
        print("Please create .env file with: GEMINI_API_KEY=your-key")
        return
    
    print(f"1. API Key: Found ({len(api_key)} characters)")
    
    # Initialize predictor
    print("2. Initializing predictor...")
    try:
        predictor = BiologicalCascadePredictor(
            gemini_api_key=api_key,
            neo4j_uri=NEO4J_URI,
            neo4j_user=NEO4J_USER,
            neo4j_password=NEO4J_PASSWORD,
            neo4j_database=NEO4J_DATABASE
        )
        print("   SUCCESS: Predictor initialized")
    except Exception as e:
        print(f"   ERROR: {e}")
        return
    
    try:
        # Create schema
        print("\n3. Creating cascade schema in Neo4j...")
        success = predictor.create_cascade_schema()
        if success:
            print("   SUCCESS: Schema created")
        else:
            print("   WARNING: Schema may already exist or error occurred")
        
        # Test prediction
        print("\n4. Testing cascade prediction (aspirin -> PTGS2)...")
        print("   This will take 5-15 seconds...")
        
        cascade = predictor.predict_and_store(
            drug_name="aspirin",
            target_name="PTGS2",
            depth=2,
            additional_context="Aspirin irreversibly inhibits COX-2 enzyme"
        )
        
        if cascade:
            print("\n=== PREDICTION SUCCESSFUL! ===")
            print(f"\nDirect Effects: {len(cascade.direct_effects)}")
            for i, effect in enumerate(cascade.direct_effects[:3], 1):
                print(f"  {i}. {effect.entity_name} ({effect.entity_type})")
                print(f"     Effect: {effect.effect_type}")
                print(f"     Confidence: {effect.confidence:.2f}")
            
            print(f"\nSecondary Effects: {len(cascade.secondary_effects)}")
            for i, effect in enumerate(cascade.secondary_effects[:3], 1):
                print(f"  {i}. {effect.entity_name} ({effect.entity_type})")
                print(f"     Effect: {effect.effect_type}")
                print(f"     Confidence: {effect.confidence:.2f}")
            
            print(f"\nAverage Confidence: {cascade.total_confidence:.2f}")
            print(f"Prediction Source: {cascade.prediction_source}")
            
            # Get statistics
            print("\n5. Database Statistics:")
            stats = predictor.get_cascade_statistics()
            print(f"   Total cascade relationships: {stats.get('total_cascade_relationships', 0)}")
            print(f"   Unique drug-target pairs: {stats.get('unique_drug_target_pairs', 0)}")
            print(f"   Average confidence: {stats.get('average_confidence', 0):.2f}")
            
            print("\n=== SETUP COMPLETE! ===")
            print("\nYou can now:")
            print("1. Run the Streamlit app: streamlit run streamlit_app.py")
            print("2. Navigate to Cascade Analysis page")
            print("3. Start predicting cascades!")
            
        else:
            print("\n   ERROR: Prediction failed")
            
    except Exception as e:
        print(f"\n   ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        predictor.close()
        print("\nConnection closed.")

if __name__ == "__main__":
    main()


