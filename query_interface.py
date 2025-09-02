import pandas as pd
from drug_target_graph import DrugTargetGraphBuilder
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DrugTargetQueryInterface:
    def __init__(self):
        """Initialize the query interface"""
        self.graph_builder = DrugTargetGraphBuilder(
            uri=NEO4J_URI,
            user=NEO4J_USER,
            password=NEO4J_PASSWORD
        )
        
    def close(self):
        """Close the database connection"""
        self.graph_builder.close()
        
    def search_drugs(self, search_term: str, limit: int = 10):
        """Search for drugs by name (partial match)"""
        with self.graph_builder.driver.session() as session:
            result = session.run("""
                MATCH (d:Drug)
                WHERE toLower(d.name) CONTAINS toLower($search_term)
                RETURN d.name as drug, d.moa as moa, d.phase as phase
                ORDER BY d.name
                LIMIT $limit
            """, search_term=search_term, limit=limit)
            return result.data()
            
    def search_targets(self, search_term: str, limit: int = 10):
        """Search for targets by name (partial match)"""
        with self.graph_builder.driver.session() as session:
            result = session.run("""
                MATCH (t:Target)
                WHERE toLower(t.name) CONTAINS toLower($search_term)
                RETURN t.name as target
                ORDER BY t.name
                LIMIT $limit
            """, search_term=search_term, limit=limit)
            return result.data()
            
    def get_drug_details(self, drug_name: str):
        """Get detailed information about a specific drug"""
        with self.graph_builder.driver.session() as session:
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
            
            # Get similar drugs (drugs that target the same targets)
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
            
    def get_target_details(self, target_name: str):
        """Get detailed information about a specific target"""
        with self.graph_builder.driver.session() as session:
            # Get drugs targeting this target
            drugs = session.run("""
                MATCH (d:Drug)-[:TARGETS]->(t:Target {name: $target_name})
                RETURN d.name as drug, d.moa as moa, d.phase as phase
                ORDER BY d.name
            """, target_name=target_name).data()
            
            # Get related targets (targets that are targeted by the same drugs)
            related_targets = session.run("""
                MATCH (d:Drug)-[:TARGETS]->(t:Target {name: $target_name})
                MATCH (d)-[:TARGETS]->(other:Target)
                WHERE other.name <> $target_name
                WITH other, count(d) as common_drugs
                ORDER BY common_drugs DESC
                LIMIT 10
                RETURN other.name as target, common_drugs
            """, target_name=target_name).data()
            
            return {
                "target_name": target_name,
                "drugs": drugs,
                "related_targets": related_targets
            }
            
    def find_drug_combinations(self, target_count: int = 2, min_drugs: int = 3):
        """Find combinations of targets that are targeted by multiple drugs"""
        with self.graph_builder.driver.session() as session:
            result = session.run("""
                MATCH (d:Drug)-[:TARGETS]->(t:Target)
                WITH t, collect(d) as drugs
                WHERE size(drugs) >= $min_drugs
                WITH collect(t) as targets
                WHERE size(targets) >= $target_count
                UNWIND targets as t
                RETURN t.name as target, size([d IN (d:Drug)-[:TARGETS]->(t) | d]) as drug_count
                ORDER BY drug_count DESC
                LIMIT 20
            """, target_count=target_count, min_drugs=min_drugs)
            return result.data()
            
    def get_phase_statistics(self):
        """Get statistics by drug development phase"""
        with self.graph_builder.driver.session() as session:
            result = session.run("""
                MATCH (d:Drug)
                WHERE d.phase IS NOT NULL AND d.phase <> ''
                RETURN d.phase as phase, count(d) as drug_count
                ORDER BY drug_count DESC
            """)
            return result.data()
            
    def get_moa_statistics(self):
        """Get statistics by mechanism of action"""
        with self.graph_builder.driver.session() as session:
            result = session.run("""
                MATCH (d:Drug)
                WHERE d.moa IS NOT NULL AND d.moa <> ''
                RETURN d.moa as moa, count(d) as drug_count
                ORDER BY drug_count DESC
                LIMIT 20
            """)
            return result.data()

def interactive_query():
    """Interactive query interface"""
    interface = DrugTargetQueryInterface()
    
    try:
        while True:
            print("\n" + "="*50)
            print("DRUG-TARGET GRAPH QUERY INTERFACE")
            print("="*50)
            print("1. Search drugs")
            print("2. Search targets")
            print("3. Get drug details")
            print("4. Get target details")
            print("5. Find drug combinations")
            print("6. Phase statistics")
            print("7. MOA statistics")
            print("8. Exit")
            
            choice = input("\nEnter your choice (1-8): ").strip()
            
            if choice == "1":
                search_term = input("Enter drug search term: ").strip()
                results = interface.search_drugs(search_term)
                print(f"\nFound {len(results)} drugs:")
                for drug in results:
                    print(f"- {drug['drug']} (MOA: {drug['moa']}, Phase: {drug['phase']})")
                    
            elif choice == "2":
                search_term = input("Enter target search term: ").strip()
                results = interface.search_targets(search_term)
                print(f"\nFound {len(results)} targets:")
                for target in results:
                    print(f"- {target['target']}")
                    
            elif choice == "3":
                drug_name = input("Enter drug name: ").strip()
                details = interface.get_drug_details(drug_name)
                if details:
                    print(f"\nDrug: {details['drug_info']['name']}")
                    print(f"MOA: {details['drug_info']['moa']}")
                    print(f"Phase: {details['drug_info']['phase']}")
                    print(f"Targets ({len(details['targets'])}): {', '.join(details['targets'])}")
                    print(f"\nSimilar drugs:")
                    for drug in details['similar_drugs'][:5]:
                        print(f"- {drug['drug']} ({drug['common_targets']} common targets)")
                else:
                    print("Drug not found")
                    
            elif choice == "4":
                target_name = input("Enter target name: ").strip()
                details = interface.get_target_details(target_name)
                if details:
                    print(f"\nTarget: {details['target_name']}")
                    print(f"Drugs targeting this target ({len(details['drugs'])}):")
                    for drug in details['drugs'][:10]:
                        print(f"- {drug['drug']} (MOA: {drug['moa']}, Phase: {drug['phase']})")
                    print(f"\nRelated targets:")
                    for target in details['related_targets'][:5]:
                        print(f"- {target['target']} ({target['common_drugs']} common drugs)")
                else:
                    print("Target not found")
                    
            elif choice == "5":
                results = interface.find_drug_combinations()
                print("\nTargets with multiple drugs:")
                for target in results:
                    print(f"- {target['target']}: {target['drug_count']} drugs")
                    
            elif choice == "6":
                results = interface.get_phase_statistics()
                print("\nDrugs by development phase:")
                for phase in results:
                    print(f"- {phase['phase']}: {phase['drug_count']} drugs")
                    
            elif choice == "7":
                results = interface.get_moa_statistics()
                print("\nTop mechanisms of action:")
                for moa in results:
                    print(f"- {moa['moa']}: {moa['drug_count']} drugs")
                    
            elif choice == "8":
                print("Goodbye!")
                break
                
            else:
                print("Invalid choice. Please try again.")
                
    except KeyboardInterrupt:
        print("\nGoodbye!")
    finally:
        interface.close()

if __name__ == "__main__":
    interactive_query()
