#!/usr/bin/env python3
"""
Test Suite for Figma Design Queries
Tests all Neo4j queries mapped from Figma designs to ensure they work correctly.

Usage:
    python test_figma_queries.py
"""

import sys
import json
import os
from typing import Dict, List, Any, Optional
from neo4j import GraphDatabase
from datetime import datetime

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try to import config from parent directory
try:
    from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE
except ImportError:
    # Try environment variables as fallback
    NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://127.0.0.1:7687')
    NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
    NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', '')
    NEO4J_DATABASE = os.getenv('NEO4J_DATABASE', 'neo4j')
    
    if not NEO4J_PASSWORD:
        print("⚠️  Warning: config.py not found and NEO4J_PASSWORD not set.")
        print("   Please either:")
        print("   1. Ensure config.py exists in project root with Neo4j credentials")
        print("   2. Set environment variables: NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE")
        sys.exit(1)

# Test configuration
TEST_DRUG_NAME = "ASPIRIN"  # Primary test drug
TEST_TARGET_NAME = "PTGS1"  # Primary test target
TEST_SEARCH_TERM = "aspirin"  # For search queries

class QueryTester:
    """Test suite for Figma design queries"""
    
    def __init__(self, uri: str, user: str, password: str, database: str):
        """Initialize Neo4j connection"""
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database
        self.test_results: List[Dict[str, Any]] = []
        
    def close(self):
        """Close database connection"""
        self.driver.close()
    
    def run_query(self, query: str, params: Dict[str, Any], description: str) -> Dict[str, Any]:
        """Run a query and return results"""
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(query, **params)
                data = result.data()
                return {
                    "success": True,
                    "data": data,
                    "row_count": len(data),
                    "error": None
                }
        except Exception as e:
            return {
                "success": False,
                "data": None,
                "row_count": 0,
                "error": str(e)
            }
    
    def test_query(self, query_name: str, query: str, params: Dict[str, Any], 
                   expected_fields: List[str] = None, 
                   min_rows: int = 0,
                   description: str = "") -> Dict[str, Any]:
        """Test a query and validate results"""
        print(f"\n🧪 Testing: {query_name}")
        if description:
            print(f"   {description}")
        
        result = self.run_query(query, params, description)
        
        test_result = {
            "query_name": query_name,
            "description": description,
            "query": query,
            "params": params,
            "success": result["success"],
            "row_count": result["row_count"],
            "has_data": result["row_count"] > 0,
            "error": result["error"],
            "timestamp": datetime.now().isoformat()
        }
        
        # Validate expected fields if provided
        if result["success"] and result["data"] and expected_fields:
            first_row = result["data"][0]
            missing_fields = [field for field in expected_fields if field not in first_row]
            test_result["missing_fields"] = missing_fields
            test_result["all_fields_present"] = len(missing_fields) == 0
            
            if missing_fields:
                print(f"   ⚠️  Missing fields: {missing_fields}")
        else:
            test_result["missing_fields"] = []
            test_result["all_fields_present"] = True
        
        # Validate minimum rows
        if result["success"]:
            test_result["meets_min_rows"] = result["row_count"] >= min_rows
            if result["row_count"] < min_rows:
                print(f"   ⚠️  Expected at least {min_rows} rows, got {result['row_count']}")
        
        # Print results
        if result["success"]:
            print(f"   ✅ Query executed successfully")
            print(f"   📊 Rows returned: {result['row_count']}")
            if result["data"] and len(result["data"]) > 0:
                print(f"   📋 Sample output keys: {list(result['data'][0].keys())}")
        else:
            print(f"   ❌ Query failed: {result['error']}")
        
        self.test_results.append(test_result)
        return test_result
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("📊 TEST SUMMARY")
        print("="*80)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for t in self.test_results if t["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"\nTotal Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for test in self.test_results:
                if not test["success"]:
                    print(f"   - {test['query_name']}: {test['error']}")
        
        print("\n" + "="*80)
    
    def save_results(self, filename: str = "figma_queries_test_results.json"):
        """Save test results to JSON file"""
        with open(filename, 'w') as f:
            json.dump({
                "test_date": datetime.now().isoformat(),
                "test_drug": TEST_DRUG_NAME,
                "test_target": TEST_TARGET_NAME,
                "total_tests": len(self.test_results),
                "passed": sum(1 for t in self.test_results if t["success"]),
                "failed": sum(1 for t in self.test_results if not t["success"]),
                "results": self.test_results
            }, f, indent=2)
        print(f"\n💾 Test results saved to: {filename}")


def run_all_tests():
    """Run all Figma design query tests"""
    
    print("="*80)
    print("🧪 FIGMA DESIGN QUERIES TEST SUITE")
    print("="*80)
    print(f"Test Drug: {TEST_DRUG_NAME}")
    print(f"Test Target: {TEST_TARGET_NAME}")
    print(f"Test Search Term: {TEST_SEARCH_TERM}")
    print("\n📝 Note: Network Visualization query skipped (will be handled by dedicated endpoint)")
    
    # Initialize tester
    tester = QueryTester(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE)
    
    try:
        # Test connection
        print("\n🔌 Testing Neo4j connection...")
        test_conn = tester.run_query("RETURN 1 as test", {}, "Connection test")
        if not test_conn["success"]:
            print("❌ Failed to connect to Neo4j")
            return
        print("✅ Connected to Neo4j")
        
        # ============================================
        # DESIGN 1: Basic Information Tab
        # ============================================
        print("\n" + "="*80)
        print("📋 DESIGN 1: Basic Information Tab")
        print("="*80)
        
        # Test 1.1: Basic Information
        tester.test_query(
            "Design 1 - Basic Information",
            """
            MATCH (d:Drug {name: $drug_name})
            RETURN d.name as name,
                   d.disease_area as disease_area,
                   d.vendor as vendor,
                   d.phase as development_phase,
                   d.purity as purity,
                   d.indication as indication
            """,
            {"drug_name": TEST_DRUG_NAME},
            expected_fields=["name", "disease_area", "vendor", "development_phase", "purity", "indication"],
            min_rows=1,
            description="Get basic drug information"
        )
        
        # Test 1.2: Mechanism of Action
        tester.test_query(
            "Design 1 - Mechanism of Action",
            """
            MATCH (d:Drug {name: $drug_name})
            RETURN d.moa as mechanism_of_action
            """,
            {"drug_name": TEST_DRUG_NAME},
            expected_fields=["mechanism_of_action"],
            min_rows=1,
            description="Get drug MoA"
        )
        
        # Test 1.3: Similar Drugs by MoA
        tester.test_query(
            "Design 1 - Similar Drugs by MoA",
            """
            MATCH (current:Drug {name: $drug_name})
            MATCH (d:Drug)
            WHERE d.moa = current.moa 
              AND d.name <> current.name
              AND d.moa IS NOT NULL
            RETURN d.name as drug_name,
                   d.moa as moa,
                   d.phase as phase
            ORDER BY d.name
            LIMIT $limit
            """,
            {"drug_name": TEST_DRUG_NAME, "limit": 20},
            expected_fields=["drug_name", "moa", "phase"],
            min_rows=0,
            description="Find similar drugs by MoA"
        )
        
        # Test 1.4: SMILES Notation
        tester.test_query(
            "Design 1 - SMILES Notation",
            """
            MATCH (d:Drug {name: $drug_name})
            RETURN d.smiles as smiles_notation
            """,
            {"drug_name": TEST_DRUG_NAME},
            expected_fields=["smiles_notation"],
            min_rows=1,
            description="Get SMILES notation"
        )
        
        # Test 1.5: Drug Search
        tester.test_query(
            "Design 1 - Drug Search",
            """
            MATCH (d:Drug)
            WHERE toLower(d.name) CONTAINS toLower($search_term)
            RETURN d.name as drug_name,
                   d.moa as moa,
                   d.phase as phase
            ORDER BY d.name
            LIMIT $limit
            """,
            {"search_term": TEST_SEARCH_TERM, "limit": 20},
            expected_fields=["drug_name", "moa", "phase"],
            min_rows=1,
            description="Search drugs by name"
        )
        
        # ============================================
        # DESIGN 2: Biological Targets Tab
        # ============================================
        print("\n" + "="*80)
        print("📋 DESIGN 2: Biological Targets Tab")
        print("="*80)
        
        # Test 2.1: Total Targets Count
        tester.test_query(
            "Design 2 - Total Targets Count",
            """
            MATCH (d:Drug {name: $drug_name})-[:TARGETS]->(t:Target)
            RETURN count(DISTINCT t) as total_targets
            """,
            {"drug_name": TEST_DRUG_NAME},
            expected_fields=["total_targets"],
            min_rows=1,
            description="Get total number of targets"
        )
        
        # Test 2.2: Targets Table (Paginated)
        tester.test_query(
            "Design 2 - Targets Table (Paginated)",
            """
            MATCH (d:Drug {name: $drug_name})-[r:TARGETS]->(t:Target)
            RETURN t.name as target,
                   r.relationship_type as relationship_type,
                   r.mechanism as mechanism,
                   r.target_class as target_class,
                   r.confidence as confidence
            ORDER BY t.name
            SKIP $skip
            LIMIT $limit
            """,
            {"drug_name": TEST_DRUG_NAME, "skip": 0, "limit": 10},
            expected_fields=["target", "relationship_type", "mechanism", "target_class", "confidence"],
            min_rows=1,
            description="Get paginated targets table"
        )
        
        # ============================================
        # DESIGN 3: Biological Targets Tab with Sidebar
        # ============================================
        print("\n" + "="*80)
        print("📋 DESIGN 3: Biological Targets Tab with Sidebar")
        print("="*80)
        
        # Test 3.1: Target Detail Sidebar
        tester.test_query(
            "Design 3 - Target Detail Sidebar",
            """
            MATCH (d:Drug {name: $drug_name})-[r:TARGETS]->(t:Target {name: $target_name})
            RETURN r.relationship_type as relationship_type,
                   r.mechanism as mechanism,
                   r.target_class as target_class,
                   r.target_subclass as target_subclass,
                   r.confidence as confidence,
                   r.reasoning as scientific_reasoning,
                   r.classification_source as source,
                   r.classification_timestamp as timestamp
            """,
            {"drug_name": TEST_DRUG_NAME, "target_name": TEST_TARGET_NAME},
            expected_fields=["relationship_type", "mechanism", "target_class", "confidence"],
            min_rows=0,  # May be 0 if not classified yet
            description="Get target detail information"
        )
        
        # ============================================
        # DESIGN 4: Drug Target Network Tab
        # ============================================
        print("\n" + "="*80)
        print("📋 DESIGN 4: Drug Target Network Tab")
        print("="*80)
        
        # Test 4.1: Network Statistics
        tester.test_query(
            "Design 4 - Network Statistics",
            """
            MATCH (d:Drug {name: $drug_name})-[r:TARGETS]->(t:Target)
            RETURN 
                count(CASE WHEN r.relationship_type = 'Primary/On-Target' THEN 1 END) as primary_effects,
                count(CASE WHEN r.relationship_type = 'Secondary/Off-Target' THEN 1 END) as secondary_effects,
                count(CASE WHEN r.relationship_type = 'Unknown' OR r.relationship_type IS NULL THEN 1 END) as unknown_type,
                count(CASE WHEN r.classified = false OR r.classified IS NULL THEN 1 END) as unclassified,
                count(CASE WHEN r.classified IS NULL THEN 1 END) as under_analysis,
                count(t) as total_targets
            """,
            {"drug_name": TEST_DRUG_NAME},
            expected_fields=["primary_effects", "secondary_effects", "unknown_type", "unclassified", "under_analysis", "total_targets"],
            min_rows=1,
            description="Get network statistics"
        )
        
        # Test 4.2: Network Visualization Data - SKIPPED
        # NOTE: Network visualization will be handled by dedicated endpoint
        print("\n⏭️  Skipping: Design 4 - Network Visualization Data (handled by endpoint)")
        
        # ============================================
        # DESIGN 5: Similar Drugs Tab
        # ============================================
        print("\n" + "="*80)
        print("📋 DESIGN 5: Similar Drugs Tab")
        print("="*80)
        
        # Test 5.1: Similar Drugs Table
        tester.test_query(
            "Design 5 - Similar Drugs Table",
            """
            MATCH (d1:Drug {name: $drug_name})-[:TARGETS]->(t:Target)<-[:TARGETS]-(d2:Drug)
            WHERE d2.name <> $drug_name
            WITH d2, count(t) as common_targets
            ORDER BY common_targets DESC
            LIMIT $limit
            RETURN d2.name as drug, 
                   d2.moa as mechanism_of_action, 
                   d2.phase as development_phase, 
                   common_targets as shared_targets
            """,
            {"drug_name": TEST_DRUG_NAME, "limit": 19},
            expected_fields=["drug", "mechanism_of_action", "development_phase", "shared_targets"],
            min_rows=1,
            description="Get similar drugs based on shared targets"
        )
        
        # ============================================
        # DESIGN 6: Search Targets - Target Information Tab
        # ============================================
        print("\n" + "="*80)
        print("📋 DESIGN 6: Search Targets - Target Information Tab")
        print("="*80)
        
        # Test 6.1: Target Basic Information Card
        tester.test_query(
            "Design 6 - Target Basic Information",
            """
            MATCH (t:Target {name: $target_name})<-[r:TARGETS]-(d:Drug)
            WITH 
              count(r) as total_interactions,
              count(CASE WHEN r.classified = true THEN 1 END) as classified_interactions,
              head([x IN collect(r.target_class) WHERE x IS NOT NULL]) as target_class,
              head([x IN collect(r.target_subclass) WHERE x IS NOT NULL]) as target_subclass,
              count(DISTINCT d) as targeting_drugs
            RETURN 
              target_class,
              target_subclass,
              targeting_drugs,
              total_interactions,
              classified_interactions,
              CASE WHEN total_interactions = 0 THEN 0 
                   ELSE round((toFloat(classified_interactions) / toFloat(total_interactions)) * 100) END as classification_progress
            """,
            {"target_name": TEST_TARGET_NAME},
            expected_fields=["target_class", "target_subclass", "targeting_drugs", "total_interactions", "classified_interactions", "classification_progress"],
            min_rows=1,
            description="Get target-level basic information"
        )
        
        # Test 6.2: Drugs Table (Paginated)
        tester.test_query(
            "Design 6 - Drugs Table (Paginated)",
            """
            MATCH (t:Target {name: $target_name})<-[r:TARGETS]-(d:Drug)
            RETURN 
              d.name as drug_name,
              CASE WHEN r.classified = true THEN 'Classified' ELSE 'Unclassified' END as classification,
              r.mechanism as mechanism,
              d.phase as phase
            ORDER BY d.name
            SKIP $skip
            LIMIT $limit
            """,
            {"target_name": TEST_TARGET_NAME, "skip": 0, "limit": 10},
            expected_fields=["drug_name", "classification", "mechanism", "phase"],
            min_rows=1,
            description="Get paginated drugs targeting the target"
        )
        
        # Test 6.3: Drug Details Expander (Right Panel)
        tester.test_query(
            "Design 6 - Drug Details Expander",
            """
            MATCH (d:Drug {name: $drug_name})
            RETURN d.name as name,
                   d.moa as mechanism,
                   d.phase as phase,
                   d.indication as indication,
                   d.disease_area as disease_area
            """,
            {"drug_name": TEST_DRUG_NAME},
            expected_fields=["name", "mechanism", "phase", "indication", "disease_area"],
            min_rows=1,
            description="Get drug details for expander panel"
        )
        
        # Test 6.4: All Targets for Drug
        tester.test_query(
            "Design 6 - All Targets for Drug",
            """
            MATCH (d:Drug {name: $drug_name})-[:TARGETS]->(t:Target)
            RETURN t.name as target
            ORDER BY t.name
            """,
            {"drug_name": TEST_DRUG_NAME},
            expected_fields=["target"],
            min_rows=1,
            description="Get all targets for a drug"
        )
        
        # ============================================
        # DESIGN 7: Search Targets - Drug Analysis Tab
        # ============================================
        print("\n" + "="*80)
        print("📋 DESIGN 7: Search Targets - Drug Analysis Tab")
        print("="*80)
        
        # Test 7.1: Development Phases Distribution
        tester.test_query(
            "Design 7 - Development Phases Distribution",
            """
            MATCH (t:Target {name: $target_name})<-[r:TARGETS]-(d:Drug)
            WHERE d.phase IS NOT NULL AND d.phase <> ''
            RETURN d.phase as phase, count(d) as drug_count
            ORDER BY drug_count DESC
            """,
            {"target_name": TEST_TARGET_NAME},
            expected_fields=["phase", "drug_count"],
            min_rows=0,  # May be 0 if no phase data
            description="Get drug phase distribution for target"
        )
        
        # Test 7.2: Mechanisms Distribution
        tester.test_query(
            "Design 7 - Mechanisms Distribution",
            """
            MATCH (t:Target {name: $target_name})<-[r:TARGETS]-(d:Drug)
            WHERE r.mechanism IS NOT NULL AND r.mechanism <> ''
            RETURN r.mechanism as mechanism, count(d) as drug_count
            ORDER BY drug_count DESC
            LIMIT $limit
            """,
            {"target_name": TEST_TARGET_NAME, "limit": 20},
            expected_fields=["mechanism", "drug_count"],
            min_rows=0,  # May be 0 if no mechanism data
            description="Get mechanism distribution for target"
        )
        
        # Test 7.3: Detailed Drug Table (Paginated)
        tester.test_query(
            "Design 7 - Detailed Drug Table (Paginated)",
            """
            MATCH (t:Target {name: $target_name})<-[r:TARGETS]-(d:Drug)
            RETURN d.name as drug_name,
                   d.moa as moa,
                   d.phase as phase,
                   r.mechanism as target_mechanism,
                   r.relationship_type as relationship,
                   r.confidence as confidence
            ORDER BY d.name
            SKIP $skip
            LIMIT $limit
            """,
            {"target_name": TEST_TARGET_NAME, "skip": 0, "limit": 10},
            expected_fields=["drug_name", "moa", "phase", "target_mechanism", "relationship", "confidence"],
            min_rows=1,
            description="Get detailed drug table for target analysis"
        )
        
        # ============================================
        # DESIGN 8: MOA Analysis - Search Mechanisms Tab
        # ============================================
        print("\n" + "="*80)
        print("📋 DESIGN 8: MOA Analysis - Search Mechanisms Tab")
        print("="*80)
        
        # Test 8.1: Search by MOA (Alternative query - works without MOA nodes)
        tester.test_query(
            "Design 8 - Search by MOA",
            """
            MATCH (d:Drug)
            WHERE toLower(d.moa) CONTAINS toLower($moa_search)
            WITH d
            MATCH (d)-[:TARGETS]->(t:Target)
            OPTIONAL MATCH (d)-[:TARGETS]->(t2:Target)<-[:TARGETS]-(other:Drug)
            WHERE other.moa = d.moa
            WITH d, count(DISTINCT t) as target_diversity, count(DISTINCT other) as drug_count
            RETURN d.name as drug,
                   d.moa as moa,
                   d.phase as phase,
                   drug_count as drugs_in_moa,
                   target_diversity as target_diversity
            ORDER BY drug_count DESC, d.name
            LIMIT $limit
            """,
            {"moa_search": "inhibitor", "limit": 25},
            expected_fields=["drug", "moa", "phase", "drugs_in_moa", "target_diversity"],
            min_rows=0,  # May be 0 if no MOA matches
            description="Search drugs by mechanism of action"
        )
        
        # ============================================
        # DESIGN 9: MOA Analysis - Therapeutic Class Tab
        # ============================================
        print("\n" + "="*80)
        print("📋 DESIGN 9: MOA Analysis - Therapeutic Class Tab")
        print("="*80)
        
        # Test 9.1: Therapeutic Class Overview (Alternative query - works without TherapeuticClass nodes)
        tester.test_query(
            "Design 9 - Therapeutic Class Overview",
            """
            MATCH (d:Drug)
            WHERE d.moa IS NOT NULL
            WITH d,
                 CASE 
                   WHEN toLower(d.moa) CONTAINS 'inhibitor' THEN 'Inhibitor'
                   WHEN toLower(d.moa) CONTAINS 'agonist' THEN 'Agonist'
                   WHEN toLower(d.moa) CONTAINS 'antagonist' THEN 'Antagonist'
                   WHEN toLower(d.moa) CONTAINS 'blocker' THEN 'Blocker'
                   ELSE 'Other'
                 END as therapeutic_class
            WITH therapeutic_class as class_name,
                 collect(DISTINCT d.moa) as unique_moas,
                 collect(DISTINCT d.name) as unique_drugs
            RETURN class_name,
                   size(unique_moas) as moa_count,
                   size(unique_drugs) as drug_count
            ORDER BY drug_count DESC
            LIMIT $limit
            """,
            {"limit": 10},
            expected_fields=["class_name", "moa_count", "drug_count"],
            min_rows=0,  # May be 0 if no data
            description="Get therapeutic class overview with MOA and drug counts"
        )
        
        # ============================================
        # DESIGN 10: MOA Analysis - Top Mechanisms Tab
        # ============================================
        print("\n" + "="*80)
        print("📋 DESIGN 10: MOA Analysis - Top Mechanisms Tab")
        print("="*80)
        
        # Test 10.1: Top Mechanisms (Alternative query - works without MOA nodes)
        tester.test_query(
            "Design 10 - Top Mechanisms of Action",
            """
            MATCH (d:Drug)
            WHERE d.moa IS NOT NULL AND d.moa <> ''
            WITH d.moa as moa_name, collect(DISTINCT d.name) as drugs
            WITH moa_name, size(drugs) as drug_count,
                 CASE 
                   WHEN toLower(moa_name) CONTAINS 'inhibitor' THEN 'Inhibitor'
                   WHEN toLower(moa_name) CONTAINS 'agonist' THEN 'Agonist'
                   WHEN toLower(moa_name) CONTAINS 'antagonist' THEN 'Antagonist'
                   WHEN toLower(moa_name) CONTAINS 'blocker' THEN 'Blocker'
                   ELSE 'Other'
                 END as therapeutic_class
            OPTIONAL MATCH (d2:Drug {moa: moa_name})-[:TARGETS]->(t:Target)
            RETURN moa_name as moa,
                   drug_count,
                   count(DISTINCT t) as target_count,
                   therapeutic_class
            ORDER BY drug_count DESC
            LIMIT $limit
            """,
            {"limit": 20},
            expected_fields=["moa", "drug_count", "target_count", "therapeutic_class"],
            min_rows=0,  # May be 0 if no data
            description="Get top mechanisms of action with drug and target counts"
        )
        
        # ============================================
        # DESIGN 11: Mechanism Classification - Individual Classification
        # ============================================
        print("\n" + "="*80)
        print("📋 DESIGN 11: Mechanism Classification - Individual Classification Display")
        print("="*80)
        
        # Test 11.1: Get Existing Drug-Target Classification
        tester.test_query(
            "Design 11 - Get Classification for Drug-Target Pair",
            """
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
            """,
            {"drug_name": TEST_DRUG_NAME, "target_name": TEST_TARGET_NAME},
            expected_fields=["relationship_type", "target_class", "target_subclass", "mechanism", "confidence", "reasoning", "source", "timestamp"],
            min_rows=0,  # May be 0 if not classified
            description="Get existing classification for a specific drug-target pair"
        )
        
        # ============================================
        # DESIGN 12: Comprehensive Statistics Dashboard
        # ============================================
        print("\n" + "="*80)
        print("📋 DESIGN 12: Comprehensive Statistics Dashboard")
        print("="*80)
        
        # Test 12.1: Drug Distribution by Development Phase
        tester.test_query(
            "Design 12 - Drug Distribution by Development Phase",
            """
            MATCH (d:Drug)
            WHERE d.phase IS NOT NULL AND d.phase <> ''
            RETURN d.phase as phase, count(d) as drug_count
            ORDER BY drug_count DESC
            """,
            {},
            expected_fields=["phase", "drug_count"],
            min_rows=1,
            description="Get drug distribution by development phase"
        )
        
        # Test 12.2: Top 15 Mechanisms of Action (Alternative query)
        tester.test_query(
            "Design 12 - Top 15 Mechanisms of Action",
            """
            MATCH (d:Drug)
            WHERE d.moa IS NOT NULL AND d.moa <> ''
            WITH d.moa as moa_name, count(d) as drug_count
            RETURN moa_name as moa, drug_count
            ORDER BY drug_count DESC
            LIMIT 15
            """,
            {},
            expected_fields=["moa", "drug_count"],
            min_rows=1,
            description="Get top 15 mechanisms of action by drug count"
        )
        
        # Test 12.3: Top 15 Drugs by Target Count
        tester.test_query(
            "Design 12 - Top 15 Drugs by Target Count",
            """
            MATCH (d:Drug)-[:TARGETS]->(t:Target)
            RETURN d.name as drug, d.moa as moa, d.phase as phase, count(t) as target_count
            ORDER BY target_count DESC
            LIMIT 15
            """,
            {},
            expected_fields=["drug", "moa", "phase", "target_count"],
            min_rows=1,
            description="Get top 15 drugs by target count"
        )
        
        # Test 12.4: Top 15 Targets by Drug Count
        tester.test_query(
            "Design 12 - Top 15 Targets by Drug Count",
            """
            MATCH (d:Drug)-[:TARGETS]->(t:Target)
            RETURN t.name as target, count(d) as drug_count
            ORDER BY drug_count DESC
            LIMIT 15
            """,
            {},
            expected_fields=["target", "drug_count"],
            min_rows=1,
            description="Get top 15 targets by drug count"
        )
        
        # ============================================
        # DESIGN 13: Drug Comparison Tab
        # ============================================
        print("\n" + "="*80)
        print("📋 DESIGN 13: Drug Comparison Tab")
        print("="*80)
        
        # Note: Drug comparison requires multiple queries
        # Testing the core query - Get Drug Details for both drugs
        print("\nNote: Drug comparison involves multiple sequential queries:")
        print("  - Get drug details for each drug")
        print("  - Get targets for each drug")
        print("  - Find common targets")
        
        # Test 13.1: Get Drug 1 Details
        tester.test_query(
            "Design 13 - Get Drug 1 Details",
            """
            MATCH (d:Drug {name: $drug1})
            RETURN d.name as name, d.moa as moa, d.phase as phase
            """,
            {"drug1": TEST_DRUG_NAME},
            expected_fields=["name", "moa", "phase"],
            min_rows=1,
            description="Get details for first drug in comparison"
        )
        
        # Test 13.2: Get Drug 2 Details (using a different test drug)
        tester.test_query(
            "Design 13 - Get Drug 2 Details",
            """
            MATCH (d:Drug {name: $drug2})
            RETURN d.name as name, d.moa as moa, d.phase as phase
            """,
            {"drug2": "ibuprofen"},  # Using a different drug for comparison
            expected_fields=["name", "moa", "phase"],
            min_rows=0,  # May not exist in database
            description="Get details for second drug in comparison"
        )
        
        # Test 13.3: Get Common Targets
        tester.test_query(
            "Design 13 - Get Common Targets",
            """
            MATCH (d1:Drug {name: $drug1})-[:TARGETS]->(t:Target)<-[:TARGETS]-(d2:Drug {name: $drug2})
            RETURN t.name as target
            ORDER BY t.name
            """,
            {"drug1": TEST_DRUG_NAME, "drug2": "ibuprofen"},
            expected_fields=["target"],
            min_rows=0,  # May not have common targets
            description="Find common targets between two drugs"
        )
        
        # ============================================
        # DESIGN 14: Therapeutic Pathways Tab
        # ============================================
        print("\n" + "="*80)
        print("📋 DESIGN 14: Therapeutic Pathways Tab")
        print("="*80)
        
        # Test 14.1: Get Therapeutic Pathway Analysis
        tester.test_query(
            "Design 14 - Get Therapeutic Pathway Analysis",
            """
            MATCH (d:Drug {name: $drug_name})-[:TARGETS]->(t:Target)
            OPTIONAL MATCH (t)<-[:TARGETS]-(other:Drug)
            WHERE other.name <> $drug_name
            RETURN d.name as drug, d.moa as moa, d.phase as phase,
                   t.name as target, count(other) as other_drugs
            ORDER BY other_drugs DESC
            """,
            {"drug_name": TEST_DRUG_NAME},
            expected_fields=["drug", "moa", "phase", "target", "other_drugs"],
            min_rows=1,
            description="Get therapeutic pathways and mechanisms for a drug with target popularity"
        )
        
        # ============================================
        # DESIGN 15: Repurposing Insights Tab
        # ============================================
        print("\n" + "="*80)
        print("📋 DESIGN 15: Repurposing Insights Tab")
        print("="*80)
        
        # Test 15.1: Top 10 Polypharmacology Drugs
        tester.test_query(
            "Design 15 - Top 10 Polypharmacology Drugs",
            """
            MATCH (d:Drug)-[:TARGETS]->(t:Target)
            WITH d, count(t) as target_count
            WHERE target_count > 3
            RETURN d.name as drug, d.moa as moa, d.phase as phase, target_count
            ORDER BY target_count DESC
            LIMIT 10
            """,
            {},
            expected_fields=["drug", "moa", "phase", "target_count"],
            min_rows=1,
            description="Get top 10 drugs by target count for repurposing insights"
        )
        
        # Test 15.2: Top 10 Druggable Targets
        tester.test_query(
            "Design 15 - Top 10 Druggable Targets",
            """
            MATCH (d:Drug)-[:TARGETS]->(t:Target)
            WITH t, count(d) as drug_count
            WHERE drug_count > 2
            RETURN t.name as target, drug_count
            ORDER BY drug_count DESC
            LIMIT 10
            """,
            {},
            expected_fields=["target", "drug_count"],
            min_rows=1,
            description="Get top 10 most druggable targets"
        )
        
        # Print summary
        tester.print_summary()
        
        # Save results
        tester.save_results()
        
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        tester.close()


if __name__ == "__main__":
    run_all_tests()

