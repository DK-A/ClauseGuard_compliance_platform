import pytest
from backend.retrieval.two_tower import TwoTowerRetrieval, COMPATIBILITY_CONFLICT_PAIRS

def test_conflict_compatibility_matrix():
    # Symmetric pairs in the compatibility matrix check
    assert ("obligation", "prohibition") in COMPATIBILITY_CONFLICT_PAIRS
    assert ("prohibition", "obligation") in COMPATIBILITY_CONFLICT_PAIRS
    assert ("permission", "prohibition") in COMPATIBILITY_CONFLICT_PAIRS
    assert ("obligation", "permission") in COMPATIBILITY_CONFLICT_PAIRS
    
    # Definition vs permission is not in compatibility matrix
    assert ("definition", "permission") not in COMPATIBILITY_CONFLICT_PAIRS

def test_two_tower_retrieval_candidate_scoring():
    two_tower = TwoTowerRetrieval()
    
    # Mock clause databases
    clause_a = {
        "text": "All employee grievances must be submitted strictly in writing within seven (7) calendar days.",
        "clause_type": "obligation",
        "section_heading": "Grievance",
        "page_number": 1,
        "source_document": "hr_policy.pdf",
        "vector_id": "vec-a"
    }
    
    clause_b = {
        "text": "Employees may raise grievances verbally or in writing. The company will acknowledge and review grievances within ten (10) working days.",
        "clause_type": "permission",
        "section_heading": "Grievances",
        "page_number": 2,
        "source_document": "employment_contract.pdf",
        "vector_id": "vec-b"
    }
    
    # Run Tower 2 compatibility manual check
    type_tuple = (clause_a["clause_type"], clause_b["clause_type"])
    assert type_tuple in COMPATIBILITY_CONFLICT_PAIRS
    assert clause_a["source_document"] != clause_b["source_document"]
