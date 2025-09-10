#!/usr/bin/env python3
"""
Enhanced Drug-Target Graph with MOA-based Relationships
- Adds MOA (Mechanism of Action) nodes and relationships
- Creates SIMILAR_MOA relationships between drugs
- Enables drug discovery based on mechanisms
"""

from neo4j import GraphDatabase
import logging
import time
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MOARelationshipEnhancer:
    def __init__(self):
        """Initialize the MOA relationship enhancer"""
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        self.database = NEO4J_DATABASE
        logger.info("Connected to Neo4j database")

    def create_moa_nodes(self):
        """Create MOA nodes from existing drug data"""
        logger.info("Creating MOA nodes...")
        with self.driver.session(database=self.database) as session:
            # Create MOA constraint first
            try:
                session.run("CREATE CONSTRAINT moa_name IF NOT EXISTS FOR (m:MOA) REQUIRE m.name IS UNIQUE")
            except:
                pass  # Constraint might already exist
            
            # Create MOA nodes from drugs
            result = session.run("""
                MATCH (d:Drug)
                WHERE d.moa IS NOT NULL AND d.moa <> '' AND d.moa <> 'Unknown'
                WITH DISTINCT d.moa as moa_name
                MERGE (m:MOA {name: moa_name})
                RETURN count(m) as moa_count
            """)
            
            moa_count = result.single()['moa_count']
            logger.info(f"Created {moa_count} MOA nodes")
            
            # Create HAS_MOA relationships
            session.run("""
                MATCH (d:Drug), (m:MOA)
                WHERE d.moa IS NOT NULL AND d.moa = m.name
                MERGE (d)-[:HAS_MOA]->(m)
            """)
            
            logger.info("Created HAS_MOA relationships")

    def create_moa_similarity_relationships(self):
        """Create relationships between drugs with similar MOAs"""
        logger.info("Creating MOA-based drug similarity relationships...")
        with self.driver.session(database=self.database) as session:
            # Create SIMILAR_MOA relationships between drugs sharing the same MOA
            result = session.run("""
                MATCH (d1:Drug)-[:HAS_MOA]->(m:MOA)<-[:HAS_MOA]-(d2:Drug)
                WHERE d1.name < d2.name  // Avoid duplicate relationships
                MERGE (d1)-[:SIMILAR_MOA {mechanism: m.name}]->(d2)
                RETURN count(*) as similarity_count
            """)
            
            similarity_count = result.single()['similarity_count']
            logger.info(f"Created {similarity_count} SIMILAR_MOA relationships")

    def create_moa_target_insights(self):
        """Create insights connecting MOAs to common targets"""
        logger.info("Creating MOA-target insight relationships...")
        with self.driver.session(database=self.database) as session:
            # Create TARGETS_VIA relationships from MOA to targets
            session.run("""
                MATCH (m:MOA)<-[:HAS_MOA]-(d:Drug)-[:TARGETS]->(t:Target)
                WITH m, t, count(d) as drug_count
                WHERE drug_count >= 2  // Only if multiple drugs with same MOA target this
                MERGE (m)-[:TARGETS_VIA {drug_count: drug_count}]->(t)
            """)
            
            logger.info("Created MOA-target insight relationships")

    def create_therapeutic_classes(self):
        """Create therapeutic class relationships based on MOA patterns"""
        logger.info("Creating therapeutic class relationships...")
        with self.driver.session(database=self.database) as session:
            # Group MOAs into therapeutic classes based on common keywords
            therapeutic_classes = {
                "Receptor Antagonist": ["antagonist", "blocker", "inhibitor"],
                "Enzyme Inhibitor": ["inhibitor", "reductase", "synthetase", "kinase"],
                "Receptor Agonist": ["agonist", "activator", "stimulator"],
                "Channel Modulator": ["channel", "transporter", "pump"],
                "Antimetabolite": ["antimetabolite", "analog", "nucleoside"],
                "DNA/RNA Targeting": ["dna", "rna", "topoisomerase", "polymerase"],
                "Immunomodulator": ["immune", "interferon", "interleukin", "antibody"],
                "Hormonal": ["hormone", "steroid", "receptor", "endocrine"]
            }
            
            for class_name, keywords in therapeutic_classes.items():
                # Create therapeutic class node
                session.run("""
                    MERGE (tc:TherapeuticClass {name: $class_name})
                """, class_name=class_name)
                
                # Link MOAs to therapeutic classes based on keywords
                for keyword in keywords:
                    session.run("""
                        MATCH (m:MOA), (tc:TherapeuticClass {name: $class_name})
                        WHERE toLower(m.name) CONTAINS toLower($keyword)
                        MERGE (m)-[:BELONGS_TO_CLASS]->(tc)
                    """, class_name=class_name, keyword=keyword)
            
            logger.info("Created therapeutic class relationships")

    def create_drug_repurposing_insights(self):
        """Create relationships for drug repurposing opportunities"""
        logger.info("Creating drug repurposing insight relationships...")
        with self.driver.session(database=self.database) as session:
            # Find drugs with similar target profiles but different indications
            session.run("""
                MATCH (d1:Drug)-[:TARGETS]->(t:Target)<-[:TARGETS]-(d2:Drug)
                WHERE d1.name < d2.name
                WITH d1, d2, count(t) as common_targets
                WHERE common_targets >= 2
                
                // Check if they have different indications
                MATCH (d1)-[:TREATS]->(i1:Indication)
                MATCH (d2)-[:TREATS]->(i2:Indication)
                WHERE i1.name <> i2.name
                
                MERGE (d1)-[:REPURPOSING_CANDIDATE {
                    shared_targets: common_targets,
                    confidence: 'medium'
                }]->(d2)
            """)
            
            # Find drugs with same MOA but different phases (development opportunities)
            session.run("""
                MATCH (d1:Drug)-[:HAS_MOA]->(m:MOA)<-[:HAS_MOA]-(d2:Drug)
                WHERE d1.name < d2.name 
                AND d1.phase <> d2.phase
                AND (d1.phase = 'Approved' OR d2.phase = 'Approved')
                
                MERGE (d1)-[:DEVELOPMENT_OPPORTUNITY {
                    mechanism: m.name,
                    phase_difference: d1.phase + ' vs ' + d2.phase
                }]->(d2)
            """)
            
            logger.info("Created drug repurposing insight relationships")

    def add_moa_statistics(self):
        """Add statistical properties to MOA nodes"""
        logger.info("Adding MOA statistics...")
        with self.driver.session(database=self.database) as session:
            # Add drug count to each MOA
            session.run("""
                MATCH (m:MOA)<-[:HAS_MOA]-(d:Drug)
                WITH m, count(d) as drug_count
                SET m.drug_count = drug_count
            """)
            
            # Add target diversity to each MOA
            session.run("""
                MATCH (m:MOA)<-[:HAS_MOA]-(d:Drug)-[:TARGETS]->(t:Target)
                WITH m, count(DISTINCT t) as target_diversity
                SET m.target_diversity = target_diversity
            """)
            
            # Add average phase score for each MOA
            session.run("""
                MATCH (m:MOA)<-[:HAS_MOA]-(d:Drug)
                WITH m, d.phase as phase
                WITH m, 
                    CASE phase
                        WHEN 'Approved' THEN 4
                        WHEN 'Phase 3' THEN 3
                        WHEN 'Phase 2' THEN 2
                        WHEN 'Phase 1' THEN 1
                        ELSE 0
                    END as phase_score
                WITH m, avg(phase_score) as avg_phase_score
                SET m.avg_development_stage = avg_phase_score
            """)
            
            logger.info("Added MOA statistics")

    def run_enhancement(self):
        """Run the complete MOA relationship enhancement"""
        logger.info("Starting MOA relationship enhancement...")
        start_time = time.time()
        
        try:
            self.create_moa_nodes()
            self.create_moa_similarity_relationships()
            self.create_moa_target_insights()
            self.create_therapeutic_classes()
            self.create_drug_repurposing_insights()
            self.add_moa_statistics()
            
            end_time = time.time()
            logger.info(f"MOA enhancement completed in {end_time - start_time:.2f} seconds")
            
            # Print summary statistics
            self.print_enhancement_summary()
            
        except Exception as e:
            logger.error(f"Error during MOA enhancement: {e}")
            raise
        finally:
            self.driver.close()

    def print_enhancement_summary(self):
        """Print summary of the enhancement"""
        logger.info("Enhancement Summary:")
        with self.driver.session(database=self.database) as session:
            # Count MOA nodes
            moa_count = session.run("MATCH (m:MOA) RETURN count(m) as count").single()['count']
            logger.info(f"  - MOA nodes: {moa_count}")
            
            # Count therapeutic classes
            class_count = session.run("MATCH (tc:TherapeuticClass) RETURN count(tc) as count").single()['count']
            logger.info(f"  - Therapeutic classes: {class_count}")
            
            # Count SIMILAR_MOA relationships
            similar_count = session.run("MATCH ()-[:SIMILAR_MOA]->() RETURN count(*) as count").single()['count']
            logger.info(f"  - Drug similarity relationships: {similar_count}")
            
            # Count repurposing candidates
            repurposing_count = session.run("MATCH ()-[:REPURPOSING_CANDIDATE]->() RETURN count(*) as count").single()['count']
            logger.info(f"  - Repurposing candidates: {repurposing_count}")
            
            # Count development opportunities
            dev_count = session.run("MATCH ()-[:DEVELOPMENT_OPPORTUNITY]->() RETURN count(*) as count").single()['count']
            logger.info(f"  - Development opportunities: {dev_count}")

if __name__ == "__main__":
    enhancer = MOARelationshipEnhancer()
    enhancer.run_enhancement()

