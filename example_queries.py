#!/usr/bin/env python3
"""
Example queries and analyses for the Drug-Target Graph Database
"""

from drug_target_graph import DrugTargetGraphBuilder
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD
import pandas as pd

def main():
    """Run example queries and analyses"""
    
    # Initialize the graph builder
    graph_builder = DrugTargetGraphBuilder(
        uri=NEO4J_URI,
        user=NEO4J_USER,
        password=NEO4J_PASSWORD
    )
    
    try:
        print("=" * 60)
        print("DRUG-TARGET GRAPH ANALYSIS EXAMPLES")
        print("=" * 60)
        
        # Get basic statistics
        print("\n1. BASIC STATISTICS")
        print("-" * 30)
        stats = graph_builder.get_graph_statistics()
        print(f"Total Drugs: {stats['drug_count']:,}")
        print(f"Total Targets: {stats['target_count']:,}")
        print(f"Total Relationships: {stats['relationship_count']:,}")
        
        # Show top drugs by target count
        print(f"\nTop 5 Drugs by Number of Targets:")
        for i, drug in enumerate(stats['top_drugs'][:5], 1):
            print(f"  {i}. {drug['drug']}: {drug['target_count']} targets")
        
        # Show top targets by drug count
        print(f"\nTop 5 Targets by Number of Drugs:")
        for i, target in enumerate(stats['top_targets'][:5], 1):
            print(f"  {i}. {target['target']}: {target['drug_count']} drugs")
        
        # Example 1: Find drugs targeting a specific target
        print("\n\n2. FINDING DRUGS BY TARGET")
        print("-" * 30)
        target_name = "DRD2"  # Dopamine receptor D2
        drugs = graph_builder.find_drugs_by_target(target_name)
        print(f"Drugs targeting {target_name} ({len(drugs)} found):")
        for drug in drugs[:10]:  # Show first 10
            print(f"  - {drug['drug']} (MOA: {drug['moa']}, Phase: {drug['phase']})")
        
        # Example 2: Find targets for a specific drug
        print("\n\n3. FINDING TARGETS FOR A DRUG")
        print("-" * 30)
        drug_name = "acetaminophen"
        targets = graph_builder.find_targets_by_drug(drug_name)
        print(f"Targets for {drug_name} ({len(targets)} found):")
        for target in targets:
            print(f"  - {target['target']}")
        
        # Example 3: Find common targets between two drugs
        print("\n\n4. FINDING COMMON TARGETS")
        print("-" * 30)
        drug1, drug2 = "acetaminophen", "ibuprofen"
        common_targets = graph_builder.find_common_targets(drug1, drug2)
        print(f"Common targets between {drug1} and {drug2} ({len(common_targets)} found):")
        for target in common_targets:
            print(f"  - {target['target']}")
        
        # Example 4: Advanced analysis - Find drugs with similar target profiles
        print("\n\n5. ADVANCED ANALYSIS")
        print("-" * 30)
        
        # Find drugs that target multiple targets (polypharmacology)
        with graph_builder.driver.session() as session:
            polypharmacology_drugs = session.run("""
                MATCH (d:Drug)-[:TARGETS]->(t:Target)
                WITH d, count(t) as target_count
                WHERE target_count >= 5
                RETURN d.name as drug, d.moa as moa, d.phase as phase, target_count
                ORDER BY target_count DESC
                LIMIT 10
            """).data()
            
            print("Drugs with 5+ targets (Polypharmacology):")
            for drug in polypharmacology_drugs:
                print(f"  - {drug['drug']}: {drug['target_count']} targets (MOA: {drug['moa']})")
        
        # Example 5: Find targets that are commonly co-targeted
        with graph_builder.driver.session() as session:
            co_targeted = session.run("""
                MATCH (d:Drug)-[:TARGETS]->(t1:Target)
                MATCH (d)-[:TARGETS]->(t2:Target)
                WHERE t1.name < t2.name
                WITH t1, t2, count(d) as drug_count
                WHERE drug_count >= 3
                RETURN t1.name as target1, t2.name as target2, drug_count
                ORDER BY drug_count DESC
                LIMIT 10
            """).data()
            
            print(f"\nCommonly co-targeted target pairs (3+ drugs):")
            for pair in co_targeted:
                print(f"  - {pair['target1']} + {pair['target2']}: {pair['drug_count']} drugs")
        
        # Example 6: Phase analysis
        print("\n\n6. DEVELOPMENT PHASE ANALYSIS")
        print("-" * 30)
        with graph_builder.driver.session() as session:
            phase_stats = session.run("""
                MATCH (d:Drug)
                WHERE d.phase IS NOT NULL AND d.phase <> ''
                RETURN d.phase as phase, count(d) as drug_count
                ORDER BY drug_count DESC
            """).data()
            
            print("Drugs by development phase:")
            for phase in phase_stats:
                print(f"  - {phase['phase']}: {phase['drug_count']} drugs")
        
        # Example 7: Mechanism of Action analysis
        print("\n\n7. MECHANISM OF ACTION ANALYSIS")
        print("-" * 30)
        with graph_builder.driver.session() as session:
            moa_stats = session.run("""
                MATCH (d:Drug)
                WHERE d.moa IS NOT NULL AND d.moa <> ''
                RETURN d.moa as moa, count(d) as drug_count
                ORDER BY drug_count DESC
                LIMIT 10
            """).data()
            
            print("Top mechanisms of action:")
            for moa in moa_stats:
                print(f"  - {moa['moa']}: {moa['drug_count']} drugs")
        
        print("\n" + "=" * 60)
        print("ANALYSIS COMPLETE")
        print("=" * 60)
        print("\nThese examples demonstrate the power of graph databases for drug discovery!")
        print("You can extend these queries to find drug repurposing opportunities,")
        print("identify potential drug combinations, and understand drug mechanisms.")
        
    except Exception as e:
        print(f"Error during analysis: {e}")
    finally:
        graph_builder.close()

if __name__ == "__main__":
    main()
