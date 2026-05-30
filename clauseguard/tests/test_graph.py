import pytest
import networkx as nx
from backend.graph.builder import ContradictionGraphBuilder

def test_graph_builder_indexing():
    builder = ContradictionGraphBuilder()
    
    # 1. Add mock nodes
    builder.add_clause_node(
        clause_id=1,
        text="All grievances must be in writing in 7 calendar days.",
        doc_source="hr_policy.pdf",
        clause_type="obligation",
        page_number=1,
        section="Grievances",
        entity_metadata={"DATE": ["7 calendar days"]}
    )
    
    builder.add_clause_node(
        clause_id=2,
        text="Grievances can be raised verbally within 10 working days.",
        doc_source="employment_contract.pdf",
        clause_type="permission",
        page_number=2,
        section="Grievance Benefits",
        entity_metadata={"DATE": ["10 working days"]}
    )
    
    # 2. Add edges
    builder.add_contradiction_edge(
        edge_id=10,
        clause_a_id=1,
        clause_b_id=2,
        contradiction_type="DIRECT_CONTRADICTION",
        severity="CRITICAL",
        confidence=0.96,
        status="open"
    )
    
    assert builder.graph.has_node(1)
    assert builder.graph.has_node(2)
    assert builder.graph.has_edge(1, 2)
    
    # 3. Retrieve clusters
    cluster = builder.get_cluster(1)
    assert len(cluster["nodes"]) == 2
    assert len(cluster["edges"]) == 1
    
    # 4. Transitive paths
    builder.add_clause_node(
        clause_id=3,
        text="Grievance logs shall be archived for 3 years.",
        doc_source="compliance_gdpr.pdf",
        clause_type="obligation",
        page_number=2,
        section="Data Policy",
        entity_metadata={"TIME": ["3 years"]}
    )
    
    builder.add_contradiction_edge(
        edge_id=11,
        clause_a_id=2,
        clause_b_id=3,
        contradiction_type="PARTIAL_OVERLAP",
        severity="MEDIUM",
        confidence=0.84,
        status="open"
    )
    
    chains = builder.get_chain(1)
    assert len(chains) >= 1
    assert [1, 2, 3] in chains or [3, 2, 1] in chains
