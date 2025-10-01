#!/usr/bin/env python3
"""
Drug-Target Mechanism Classification System
- Uses Gemini API to classify drug-target relationships
- Implements 3-level classification hierarchy
- Stores results in Neo4j relationship properties
"""

import google.generativeai as genai
import json
import logging
import time
from datetime import datetime
from neo4j import GraphDatabase
from typing import Dict, Optional, List
import os
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class MechanismClassification:
    """Data class for mechanism classification results"""
    relationship_type: str  # Primary/On-Target or Secondary/Off-Target
    target_class: str       # Protein, Nucleic Acid, Lipid, Carbohydrate
    target_subclass: str    # Enzyme, Receptor, Ion Channel, etc.
    mechanism: str          # Specific mechanism (Inhibitor, Agonist, etc.)
    confidence: float       # 0.0 to 1.0
    reasoning: str          # Explanation from Gemini
    source: str            # "Gemini_API"
    timestamp: str         # ISO format timestamp

class DrugTargetMechanismClassifier:
    def __init__(self, gemini_api_key: str = None, neo4j_uri: str = None, 
                 neo4j_user: str = None, neo4j_password: str = None, neo4j_database: str = "neo4j"):
        """Initialize the mechanism classifier"""
        
        # Initialize Gemini API
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            
            # Try different model names in order of preference
            model_names = ['gemini-pro', 'gemini-1.5-pro', 'gemini-1.0-pro']
            self.gemini_model = None
            
            for model_name in model_names:
                try:
                    self.gemini_model = genai.GenerativeModel(model_name)
                    logger.info(f"Gemini API initialized successfully with model: {model_name}")
                    break
                except Exception as e:
                    logger.warning(f"Failed to initialize model {model_name}: {e}")
                    continue
            
            if not self.gemini_model:
                logger.error("Failed to initialize any Gemini model")
                self.gemini_model = None
        else:
            logger.warning("No Gemini API key provided - classification will be disabled")
            self.gemini_model = None
        
        # Initialize Neo4j connection
        if neo4j_uri and neo4j_user and neo4j_password:
            self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
            self.database = neo4j_database
            logger.info("Neo4j connection initialized")
        else:
            logger.warning("No Neo4j credentials provided - database updates will be disabled")
            self.driver = None
        
        # Classification templates
        self.classification_prompt = """
You are an expert pharmacologist. Classify the relationship between the drug "{drug_name}" and its target "{target_name}".

Classification Levels:
1. Relationship Type: Primary/On-Target OR Secondary/Off-Target
2. Target Class: Protein, Nucleic Acid, Lipid, OR Carbohydrate  
3. Target Subclass (if Protein): Enzyme, Receptor, Ion Channel, Transporter, Transcription Factor, OR Other
4. Mechanism: Specific action (e.g., Inhibitor, Agonist, Blocker)

RESPOND ONLY WITH VALID JSON:

{{
    "relationship_type": "Primary/On-Target",
    "target_class": "Protein",
    "target_subclass": "Enzyme",
    "mechanism": "Irreversible Inhibitor",
    "confidence": 0.95,
    "reasoning": "Brief explanation here"
}}

Drug: {drug_name}
Target: {target_name}
Context: {additional_context}

JSON Response:"""

    def classify_drug_target_relationship(self, drug_name: str, target_name: str, 
                                        additional_context: str = "") -> Optional[MechanismClassification]:
        """Classify a drug-target relationship using Gemini API"""
        
        if not self.gemini_model:
            logger.error("Gemini API not available for classification")
            return None
        
        try:
            # Prepare the prompt
            prompt = self.classification_prompt.format(
                drug_name=drug_name,
                target_name=target_name,
                additional_context=additional_context or "No additional context provided"
            )
            
            logger.info(f"Classifying relationship: {drug_name} -> {target_name}")
            
            # Query Gemini API
            response = self.gemini_model.generate_content(prompt)
            
            if not response.text:
                logger.error("Empty response from Gemini API")
                return None
            
            # Parse JSON response
            try:
                # Extract JSON from response (in case there's extra text)
                response_text = response.text.strip()
                
                # Remove any markdown formatting
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    if json_end == -1:
                        json_end = len(response_text)
                    response_text = response_text[json_start:json_end].strip()
                elif "```" in response_text:
                    json_start = response_text.find("```") + 3
                    json_end = response_text.find("```", json_start)
                    if json_end == -1:
                        json_end = len(response_text)
                    response_text = response_text[json_start:json_end].strip()
                
                # Extract JSON object
                if "{" in response_text and "}" in response_text:
                    json_start = response_text.find("{")
                    json_end = response_text.rfind("}") + 1
                    response_text = response_text[json_start:json_end]
                
                # Clean up any extra characters
                response_text = response_text.replace('\n', ' ').replace('\r', '')
                
                logger.info(f"Parsing JSON: {response_text[:100]}...")
                classification_data = json.loads(response_text)
                
                # Validate required fields
                required_fields = ['relationship_type', 'target_class', 'mechanism', 'confidence', 'reasoning']
                for field in required_fields:
                    if field not in classification_data:
                        logger.error(f"Missing required field: {field}")
                        return None
                
                # Create classification object
                classification = MechanismClassification(
                    relationship_type=classification_data['relationship_type'],
                    target_class=classification_data['target_class'],
                    target_subclass=classification_data.get('target_subclass', 'Unknown'),
                    mechanism=classification_data['mechanism'],
                    confidence=float(classification_data['confidence']),
                    reasoning=classification_data['reasoning'],
                    source="Gemini_API",
                    timestamp=datetime.now().isoformat()
                )
                
                logger.info(f"Successfully classified {drug_name} -> {target_name}: {classification.mechanism}")
                return classification
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Response text: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error during classification: {e}")
            return None

    def store_classification_in_neo4j(self, drug_name: str, target_name: str, 
                                    classification: MechanismClassification) -> bool:
        """Store classification results in Neo4j relationship properties"""
        
        if not self.driver:
            logger.error("Neo4j driver not available")
            return False
        
        try:
            with self.driver.session(database=self.database) as session:
                # Update the TARGETS relationship with classification properties
                result = session.run("""
                    MATCH (d:Drug {name: $drug_name})-[r:TARGETS]->(t:Target {name: $target_name})
                    SET r.relationship_type = $relationship_type,
                        r.target_class = $target_class,
                        r.target_subclass = $target_subclass,
                        r.mechanism = $mechanism,
                        r.confidence = $confidence,
                        r.reasoning = $reasoning,
                        r.classification_source = $source,
                        r.classification_timestamp = $timestamp,
                        r.classified = true
                    RETURN count(r) as updated_count
                """, 
                    drug_name=drug_name,
                    target_name=target_name,
                    relationship_type=classification.relationship_type,
                    target_class=classification.target_class,
                    target_subclass=classification.target_subclass,
                    mechanism=classification.mechanism,
                    confidence=classification.confidence,
                    reasoning=classification.reasoning,
                    source=classification.source,
                    timestamp=classification.timestamp
                )
                
                updated_count = result.single()['updated_count']
                if updated_count > 0:
                    logger.info(f"Successfully stored classification for {drug_name} -> {target_name}")
                    return True
                else:
                    logger.warning(f"No relationship found to update: {drug_name} -> {target_name}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error storing classification in Neo4j: {e}")
            return False

    def get_existing_classification(self, drug_name: str, target_name: str) -> Optional[Dict]:
        """Check if classification already exists for this drug-target pair"""
        
        if not self.driver:
            return None
        
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run("""
                    MATCH (d:Drug {name: $drug_name})-[r:TARGETS]->(t:Target {name: $target_name})
                    WHERE r.classified = true
                    RETURN r.relationship_type as relationship_type,
                           r.target_class as target_class,
                           r.target_subclass as target_subclass,
                           r.mechanism as mechanism,
                           r.confidence as confidence,
                           r.reasoning as reasoning,
                           r.classification_source as source,
                           r.classification_timestamp as timestamp
                """, drug_name=drug_name, target_name=target_name)
                
                record = result.single()
                if record:
                    return dict(record)
                return None
                
        except Exception as e:
            logger.error(f"Error checking existing classification: {e}")
            return None

    def classify_and_store(self, drug_name: str, target_name: str, 
                          additional_context: str = "", force_reclassify: bool = False) -> Optional[Dict]:
        """Complete workflow: check existing, classify if needed, store results"""
        
        # Check if classification already exists
        if not force_reclassify:
            existing = self.get_existing_classification(drug_name, target_name)
            if existing:
                logger.info(f"Using existing classification for {drug_name} -> {target_name}")
                return existing
        
        # Classify using Gemini API
        classification = self.classify_drug_target_relationship(drug_name, target_name, additional_context)
        if not classification:
            return None
        
        # Store in Neo4j
        if self.driver:
            success = self.store_classification_in_neo4j(drug_name, target_name, classification)
            if not success:
                logger.warning("Failed to store classification in database")
        
        # Return classification as dict
        return {
            'relationship_type': classification.relationship_type,
            'target_class': classification.target_class,
            'target_subclass': classification.target_subclass,
            'mechanism': classification.mechanism,
            'confidence': classification.confidence,
            'reasoning': classification.reasoning,
            'source': classification.source,
            'timestamp': classification.timestamp
        }

    def batch_classify_drug_targets(self, drug_name: str, limit: int = 5) -> List[Dict]:
        """Classify multiple targets for a single drug"""
        
        if not self.driver:
            logger.error("Neo4j driver required for batch classification")
            return []
        
        try:
            # Get all targets for this drug
            with self.driver.session(database=self.database) as session:
                result = session.run("""
                    MATCH (d:Drug {name: $drug_name})-[r:TARGETS]->(t:Target)
                    WHERE r.classified IS NULL OR r.classified = false
                    RETURN t.name as target_name
                    LIMIT $limit
                """, drug_name=drug_name, limit=limit)
                
                targets = [record['target_name'] for record in result]
            
            if not targets:
                logger.info(f"No unclassified targets found for {drug_name}")
                return []
            
            logger.info(f"Batch classifying {len(targets)} targets for {drug_name}")
            
            # Classify each target
            classifications = []
            for target_name in targets:
                classification = self.classify_and_store(drug_name, target_name)
                if classification:
                    classifications.append({
                        'drug_name': drug_name,
                        'target_name': target_name,
                        **classification
                    })
                
                # Add delay to respect API rate limits
                time.sleep(1)
            
            return classifications
            
        except Exception as e:
            logger.error(f"Error in batch classification: {e}")
            return []

    def close(self):
        """Close database connection"""
        if self.driver:
            self.driver.close()

# Example usage and testing
if __name__ == "__main__":
    # Load API key from environment variable
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        logger.error("Please set GEMINI_API_KEY environment variable")
        exit(1)
    
    # Initialize classifier with local Neo4j
    classifier = DrugTargetMechanismClassifier(
        gemini_api_key=api_key,
        neo4j_uri="bolt://127.0.0.1:7687",
        neo4j_user="neo4j", 
        neo4j_password="11223344"
    )
    
    try:
        # Test classification
        result = classifier.classify_and_store("Aspirin", "PTGS1", "COX-1 enzyme")
        if result:
            print("Classification successful:")
            print(json.dumps(result, indent=2))
        else:
            print("Classification failed")
            
    finally:
        classifier.close()
