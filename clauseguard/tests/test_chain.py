import pytest
from backend.reasoning.chain import ContradictionReasonerChain, ContradictionAnalysisSchema

def test_pydantic_schema_validation():
    # Verify standard output parsing keys
    keys = list(ContradictionAnalysisSchema.__annotations__.keys())
    assert "relationship" in keys
    assert "business_risk" in keys
    assert "severity" in keys
    assert "recommended_resolution" in keys
    assert "llm_confidence" in keys

def test_reasoner_mock_fallback_parser():
    chain = ContradictionReasonerChain()
    
    raw_response = """
    Here is the classification result in raw prose:
    {
      "relationship": "DIRECT_CONTRADICTION",
      "business_risk": "Conflict on grievance deadline.",
      "severity": "CRITICAL",
      "recommended_resolution": "Harmonize to 10 days.",
      "llm_confidence": 0.99
    }
    """
    
    parsed = chain._fallback_parse(raw_response)
    assert parsed["relationship"] == "DIRECT_CONTRADICTION"
    assert parsed["severity"] == "CRITICAL"
    assert parsed["llm_confidence"] == 0.99
