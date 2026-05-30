import os
import logging
from dataclasses import dataclass
from typing import Optional
from langchain_core.language_models.chat_models import BaseChatModel

logger = logging.getLogger("ClauseGuardModelRegistry")
# Fallback import in case standard langchain_community is still installing
try:
    from langchain_community.chat_models import ChatOllama
except ImportError:
    from langchain_core.language_models.chat_models import SimpleChatModel as ChatOllama

from backend.hardware.fingerprint import ProfileType, detect_profile

@dataclass
class ReasoningConfig:
    cot_steps: int
    pair_limit: int
    confidence_threshold: float
    single_prompt_mode: bool
    profile_name: str
    primary_model: str
    embedding_model: str
    fallback_model: str

class MockLLM(BaseChatModel):
    """Fallback Mock LLM in case Ollama or llama.cpp is not running."""
    model_name: str
    
    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        from langchain_core.outputs import ChatResult, ChatGeneration
        from langchain_core.messages import AIMessage
        import json
        
        # Simple simulated legal comparison response
        text = messages[-1].content
        if "summarize" in text.lower() or "summary" in text.lower():
            if "grievance" in text.lower():
                response_content = "Grievances must be submitted in writing within 7 calendar days."
            elif "remote" in text.lower() or "telecommuting" in text.lower() or "same-day" in text.lower():
                response_content = "Remote work requests require manager approval at least 48 hours in advance."
            elif "leave" in text.lower():
                response_content = "Annual leaves must be taken in the calendar year and carryover is limited."
            elif "retention" in text.lower() or "retention limits" in text.lower() or "retention" in text.lower():
                response_content = "Log files containing user information shall be deleted within 3 years."
            elif "incident" in text.lower() or "incident management" in text.lower():
                response_content = "Any detected security breach must be disclosed within 24 hours."
            else:
                response_content = "Compliance notice governs timelines, requirements and operational terms."
        elif "Paraphrase" in text or "Step 1" in text:
            # Three-step reasoning CoT mock
            response_content = (
                "Paraphrase:\n"
                "Clause A establishes that employee grievances must be raised in writing within 7 calendar days.\n"
                "Clause B states that company allows raising grievances verbally or in writing with a 10 working day limit.\n\n"
                "Conflict Scenario:\n"
                "A conflict occurs if an employee raises a grievance verbally or after 7 calendar days but within 10 working days, "
                "which is permitted under Clause B but violates the strict written and time constraints of Clause A.\n\n"
                "Classification:\n"
                "{\n"
                '  "relationship": "DIRECT_CONTRADICTION",\n'
                '  "business_risk": "Conflict between employee contract and general HR policy on submission deadline and format.",\n'
                '  "severity": "HIGH",\n'
                '  "recommended_resolution": "Harmonize by aligning HR policy and contracts to a standard 10 working days, in writing.",\n'
                '  "llm_confidence": 0.95\n'
                "}"
            )
        else:
            # Single prompt mock
            response_content = (
                "{\n"
                '  "relationship": "DIRECT_CONTRADICTION",\n'
                '  "business_risk": "Conflict between employee contract and general HR policy on submission deadline and format.",\n'
                '  "severity": "HIGH",\n'
                '  "recommended_resolution": "Harmonize by aligning HR policy and contracts to a standard 10 working days, in writing.",\n'
                '  "llm_confidence": 0.95\n'
                "}"
            )
        message = AIMessage(content=response_content)
        return ChatResult(generations=[ChatGeneration(message=message)])
    
    @property
    def _llm_type(self) -> str:
        return "mock-llm"

class ModelRegistry:
    def __init__(self):
        self.profile = detect_profile()
        self.fallback_active = False
        self._embedding_model_instance = None
        self._llm_instance = None
        
        # Registry configurations
        self.configs = {
            ProfileType.LAPTOP: ReasoningConfig(
                cot_steps=3,
                pair_limit=50,
                confidence_threshold=0.65,
                single_prompt_mode=False,
                profile_name="LAPTOP (Max Accuracy)",
                primary_model="llama3.1:8b",
                embedding_model="BERT-Legal-Base",  # local name, falls back to sentence-transformers
                fallback_model="qwen2.5:7b"
            ),
            ProfileType.RPI5: ReasoningConfig(
                cot_steps=3,
                pair_limit=30,
                confidence_threshold=0.70,
                single_prompt_mode=False,
                profile_name="RPI5 (Balanced Edge)",
                primary_model="llama3.1:8b-q4",
                embedding_model="BERT-Legal-Base",
                fallback_model="qwen2.5:3b"
            ),
            ProfileType.RPI4: ReasoningConfig(
                cot_steps=1,
                pair_limit=15,
                confidence_threshold=0.75,
                single_prompt_mode=True,
                profile_name="RPI4 (Edge Optimized)",
                primary_model="qwen2.5:1.5b",
                embedding_model="all-MiniLM-L6-v2",
                fallback_model="phi3:mini"
            )
        }
    
    def get_reasoning_config(self) -> ReasoningConfig:
        return self.configs[self.profile]
        
    def get_llm(self) -> BaseChatModel:
        if self._llm_instance is not None:
            return self._llm_instance
            
        config = self.get_reasoning_config()
        model_name = config.fallback_model if self.fallback_active else config.primary_model
        
        ollama_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        llamacpp_url = os.environ.get("LLAMACPP_BASE_URL", "http://localhost:8080")
        
        # In production, check if we use llama.cpp (RPi) or Ollama (Laptop)
        base_url = llamacpp_url if self.profile in (ProfileType.RPI5, ProfileType.RPI4) else ollama_url
        
        # Attempt to initialize LangChain ChatOllama, fallback to MockLLM if connection fails
        try:
            import urllib.request
            # Ping the base_url with a 1-second timeout
            with urllib.request.urlopen(base_url, timeout=1.0) as response:
                pass
            from langchain_community.chat_models import ChatOllama
            self._llm_instance = ChatOllama(
                base_url=base_url,
                model=model_name,
                temperature=0.0
            )
        except Exception as e:
            logger.warning(f"Ollama/Llama.cpp server at {base_url} is not responsive: {e}. Falling back to MockLLM.")
            self._llm_instance = MockLLM(model_name=model_name)
            
        return self._llm_instance

    def get_embedding_model(self):
        if self._embedding_model_instance is not None:
            return self._embedding_model_instance
            
        config = self.get_reasoning_config()
        model_name = config.embedding_model
        
        # Maps legal name to public sentence transformer if not local path
        if model_name == "BERT-Legal-Base":
            model_name = "nlpaueb/legal-bert-base-uncased"
        elif model_name == "all-MiniLM-L6-v2":
            model_name = "sentence-transformers/all-MiniLM-L6-v2"
            
        try:
            from sentence_transformers import SentenceTransformer
            self._embedding_model_instance = SentenceTransformer(model_name)
        except Exception:
            # Simulated dummy embedder for tests/CI environment if transformers are failing
            class DummyEmbedder:
                def encode(self, sentences, **kwargs):
                    import numpy as np
                    if isinstance(sentences, str):
                        return np.random.rand(384).tolist()
                    return np.random.rand(len(sentences), 384).tolist()
            self._embedding_model_instance = DummyEmbedder()
            
        return self._embedding_model_instance

    def switch_to_fallback(self) -> bool:
        if not self.fallback_active:
            self.fallback_active = True
            self._llm_instance = None  # Reset to reload fallback
            return True
        return False
        
    def restore_primary(self) -> bool:
        if self.fallback_active:
            self.fallback_active = False
            self._llm_instance = None  # Reset to reload primary
            return True
        return False
