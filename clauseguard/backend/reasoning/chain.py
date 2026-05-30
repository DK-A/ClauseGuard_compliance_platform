import re
import json
import logging
from pydantic import BaseModel, Field
from typing import Optional

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from backend.config import get_llm, get_reasoning_config
from backend.reasoning.prompts import (
    PROMPT_THREE_STEP_1_PARAPHRASE,
    PROMPT_THREE_STEP_2_SCENARIO,
    PROMPT_THREE_STEP_3_CLASSIFICATION,
    PROMPT_SINGLE_COMBINED
)

logger = logging.getLogger("ClauseGuardChain")

class ContradictionAnalysisSchema(BaseModel):
    relationship: str = Field(
        description="Must be exactly one of: DIRECT_CONTRADICTION, PARTIAL_OVERLAP, AMBIGUITY, SUPERSESSION, NO_CONFLICT"
    )
    business_risk: str = Field(
        description="A detailed description of the legal, financial, or operational risk of this inconsistency"
    )
    severity: str = Field(
        description="Must be exactly one of: CRITICAL, HIGH, MEDIUM, LOW"
    )
    recommended_resolution: str = Field(
        description="Practical recommendations to harmonize the two clauses and resolve the conflict"
    )
    llm_confidence: float = Field(
        description="Self-reported confidence level between 0.0 and 1.0"
    )

parser = PydanticOutputParser(pydantic_object=ContradictionAnalysisSchema)

class ContradictionReasonerChain:
    def __init__(self):
        self.llm = get_llm()
        
    def analyze_pair(self, clause_a_text: str, clause_b_text: str) -> dict:
        config = get_reasoning_config()
        self.llm = get_llm() # Dynamically load LLM instance to respect runtime profile overrides
        
        if config.single_prompt_mode:
            logger.info("Executing reasoning pipeline in Single-Prompt Edge Mode...")
            return self._run_single_prompt(clause_a_text, clause_b_text)
        else:
            logger.info("Executing reasoning pipeline in Full 3-Step Chain-of-Thought Mode...")
            return self._run_three_step_cot(clause_a_text, clause_b_text)
            
    def _invoke_llm(self, prompt: str) -> str:
        try:
            return self.llm.invoke(prompt).content
        except Exception as e:
            logger.warning(f"LLM invocation failed: {e}. Executing mock LLM fallback.")
            from backend.hardware.registry import MockLLM
            config = get_reasoning_config()
            mock = MockLLM(model_name=config.primary_model)
            return mock.invoke(prompt).content

    def _run_single_prompt(self, clause_a_text: str, clause_b_text: str) -> dict:
        prompt_tmpl = PromptTemplate(
            template=PROMPT_SINGLE_COMBINED,
            input_variables=["clause_a_text", "clause_b_text"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        
        prompt = prompt_tmpl.format(clause_a_text=clause_a_text, clause_b_text=clause_b_text)
        
        try:
            res_content = self._invoke_llm(prompt)
            result = parser.parse(res_content)
            return result.model_dump()
        except Exception as e:
            logger.error(f"Error parsing edge LLM output: {e}. Executing regex fallback parser.")
            return self._fallback_parse(res_content if 'res_content' in locals() else "")
            
    def _run_three_step_cot(self, clause_a_text: str, clause_b_text: str) -> dict:
        # Step 1: Paraphrase
        p1_tmpl = PromptTemplate(
            template=PROMPT_THREE_STEP_1_PARAPHRASE,
            input_variables=["clause_a_text", "clause_b_text"]
        )
        p1_prompt = p1_tmpl.format(clause_a_text=clause_a_text, clause_b_text=clause_b_text)
        p1_res = self._invoke_llm(p1_prompt)
        logger.debug(f"Step 1 output: {p1_res}")
        
        # Step 2: Compare & Scenario Detection
        p2_tmpl = PromptTemplate(
            template=PROMPT_THREE_STEP_2_SCENARIO,
            input_variables=["paraphrases"]
        )
        p2_prompt = p2_tmpl.format(paraphrases=p1_res)
        p2_res = self._invoke_llm(p2_prompt)
        logger.debug(f"Step 2 output: {p2_res}")
        
        # Short-circuit scenario check
        if "NO_SCENARIO" in p2_res:
            logger.info("Conflict analysis short-circuited: No conflict scenario detected in Step 2.")
            return {
                "relationship": "NO_CONFLICT",
                "business_risk": "None detected.",
                "severity": "LOW",
                "recommended_resolution": "No action needed.",
                "llm_confidence": 0.99
            }
            
        # Step 3: Classify & Formulate Resolution JSON
        p3_tmpl = PromptTemplate(
            template=PROMPT_THREE_STEP_3_CLASSIFICATION,
            input_variables=["paraphrases", "scenario"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        p3_prompt = p3_tmpl.format(paraphrases=p1_res, scenario=p2_res)
        
        try:
            p3_res = self._invoke_llm(p3_prompt)
            result = parser.parse(p3_res)
            return result.model_dump()
        except Exception as e:
            logger.error(f"Error parsing LLM classification output: {e}. Executing regex fallback parser.")
            content = p3_res if 'p3_res' in locals() else ""
            return self._fallback_parse(content)

    def _fallback_parse(self, text: str) -> dict:
        """
        Regex-based JSON parser to scrape valid fields from LLM prose in case of parse errors.
        """
        # Set standard defaults
        parsed = {
            "relationship": "DIRECT_CONTRADICTION",
            "business_risk": "Deviation from organizational compliance protocols.",
            "severity": "HIGH",
            "recommended_resolution": "Review with legal team to align terms.",
            "llm_confidence": 0.80
        }
        
        # Try to find a JSON block in the text
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                data = json.loads(json_match.group(0))
                # Validate key values
                for k in parsed:
                    if k in data:
                        parsed[k] = data[k]
                return parsed
            except Exception:
                pass
                
        # Regex field scraping
        rel_match = re.search(r'"relationship"\s*:\s*"([^"]+)"', text)
        if rel_match and rel_match.group(1) in ["DIRECT_CONTRADICTION", "PARTIAL_OVERLAP", "AMBIGUITY", "SUPERSESSION", "NO_CONFLICT"]:
            parsed["relationship"] = rel_match.group(1)
            
        sev_match = re.search(r'"severity"\s*:\s*"([^"]+)"', text)
        if sev_match and sev_match.group(1) in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            parsed["severity"] = sev_match.group(1)
            
        risk_match = re.search(r'"business_risk"\s*:\s*"([^"]+)"', text)
        if risk_match:
            parsed["business_risk"] = risk_match.group(1)
            
        conf_match = re.search(r'"llm_confidence"\s*:\s*([0-9\.]+)', text)
        if conf_match:
            try:
                parsed["llm_confidence"] = float(conf_match.group(1))
            except ValueError:
                pass
                
        return parsed
