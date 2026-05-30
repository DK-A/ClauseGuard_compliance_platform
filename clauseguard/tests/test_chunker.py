import pytest
from backend.ingestion.chunker import chunk_document, clean_text, classify_clause_type

def test_clean_text():
    assert clean_text("  hello    world  ") == "hello world"
    assert clean_text("line\nbreak") == "line break"

def test_classify_clause_type():
    assert classify_clause_type("The contractor shall execute works.") == "obligation"
    assert classify_clause_type("No party is prohibited from disclosing information.") == "prohibition"
    assert classify_clause_type("The company may terminate services.") == "permission"
    assert classify_clause_type("Under this agreement, lookup means index validation.") == "definition"
    assert classify_clause_type("Provided that vendor gives a 30-day notice.") == "exception"

def test_chunk_document():
    # Simple list mock
    mock_pages = [
        {"text": "1. Grievance procedure shall be raised. Must notify supervisor within 7 days.", "page_number": 1}
    ]
    clauses = chunk_document(mock_pages, "hr_policy.pdf")
    
    assert len(clauses) >= 1
    first = clauses[0]
    assert "text" in first
    assert first["clause_type"] in ["obligation", "prohibition", "permission", "definition", "exception"]
    assert first["page_number"] == 1
    assert "DATE" in first["named_entities"]
