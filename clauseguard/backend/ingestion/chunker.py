import re
import uuid
import json
import logging

logger = logging.getLogger("ClauseGuardChunker")

OBLIGATION_KEYWORDS = {
    "must", "shall", "will", "required", "prohibited", "may", 
    "cannot", "should", "agree", "warrant", "indemnify", 
    "liable", "terminate", "notify", "disclose"
}

def clean_text(text: str) -> str:
    # Normalize whitespaces
    return re.sub(r'\s+', ' ', text).strip()

def sentence_segmenter_fallback(text: str):
    """
    Robust fallback sentence boundary splitter using regexes.
    Useful if spaCy is not fully loaded or if the model isn't downloaded yet.
    """
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [clean_text(s) for s in sentences if s.strip()]

def detect_section_heading(text: str) -> str:
    """
    Checks if a short text line looks like a section heading.
    """
    text_clean = text.strip()
    if len(text_clean) < 100 and (
        re.match(r'^(?:[0-9]+(?:\.[0-9]+)*)\s+[A-Z]', text_clean) or 
        re.match(r'^[A-Z][A-Za-z\s]{2,50}$', text_clean) or
        "section" in text_clean.lower() or "article" in text_clean.lower()
    ):
        return text_clean
    return ""

def classify_clause_type(text: str) -> str:
    """
    Classifies clause type using heuristic obligation markers.
    """
    text_lower = text.lower()
    if any(k in text_lower for k in ["prohibit", "cannot", "must not", "shall not", "no party shall"]):
        return "prohibition"
    elif any(k in text_lower for k in ["except", "unless", "provided that", "excluding"]):
        return "exception"
    elif any(k in text_lower for k in ["mean", "define", "refers to", "under this agreement"]):
        return "definition"
    elif any(k in text_lower for k in ["may", "permit", "entitled", "has the right"]):
        return "permission"
    elif any(k in text_lower for k in ["must", "shall", "will", "required", "obligated", "agree"]):
        return "obligation"
    return "obligation"  # Default fallback

def extract_named_entities_fallback(text: str) -> dict:
    """
    Fallback NER regex matcher for roles, dates, timeframes, and values.
    """
    entities = {
        "PERSON": [],
        "ORG": [],
        "DATE": [],
        "MONEY": [],
        "TIME": []
    }
    
    # Matches currency numbers like ₹10L, $500,000, 10,00,000
    money_matches = re.findall(r'(?:[\$€£₹]|\bRs\.?\b)\s?\d+(?:[.,\d]*\d+)?(?:\s?(?:lakhs?|crores?|million|billion|k))?', text)
    entities["MONEY"] = [m.strip() for m in money_matches]
    
    # Matches dates like 12 months, 7 days, 30 days, August 13-14, 2026
    date_matches = re.findall(r'\b(?:\d{1,2}\s+(?:days?|months?|years?|weeks?|calendar\s+days|working\s+days)|(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}(?:\s*,\s*\d{4})?)\b', text, re.IGNORECASE)
    entities["DATE"] = [d.strip() for d in date_matches]
    
    # Matches roles/orgs
    orgs = ["clauseguard", "client", "contractor", "company", "party", "either party", "vendor"]
    for org in orgs:
        if org in text.lower():
            entities["ORG"].append(org.capitalize())
            
    return entities

def chunk_document(parsed_pages, source_document: str):
    """
    Two-pass intelligent chunking.
    - Pass 1: Sentence segmentation and obligation grouping.
    - Pass 2: Metadata and heuristic feature extraction.
    """
    nlp = None
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
    except Exception:
        logger.warning("spaCy en_core_web_sm model not loaded. Falling back to regex segmenter.")

    clauses = []
    current_section = "General"
    
    for page in parsed_pages:
        page_num = page["page_number"]
        page_text = page["text"]
        
        # Detect section headings in the page
        lines = page_text.split("\n")
        for line in lines:
            heading = detect_section_heading(line)
            if heading:
                current_section = heading
                
        # Pass 1: Sentence boundary extraction
        if nlp:
            doc = nlp(page_text)
            sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
        else:
            sentences = sentence_segmenter_fallback(page_text)
            
        current_clause_group = []
        
        for sent in sentences:
            sent_clean = clean_text(sent)
            if not sent_clean:
                continue
                
            words = set(re.findall(r'\b\w+\b', sent_clean.lower()))
            has_obligation = not words.isdisjoint(OBLIGATION_KEYWORDS)
            is_list_start = bool(re.match(r'^(?:\d+[\.\)]|[a-zA-Z][\.\)]|\b[ixvIXV]+[\.\)])', sent_clean))
            
            if (has_obligation or is_list_start) and current_clause_group:
                # Flush the preceding accumulated group as a single logical clause
                clause_text = " ".join(current_clause_group)
                if len(clause_text) > 20:  # Skip trivial snippets
                    clauses.append(build_clause_object(clause_text, source_document, current_section, page_num, nlp))
                current_clause_group = [sent_clean]
            else:
                current_clause_group.append(sent_clean)
                
        # Flush any remaining text on the page
        if current_clause_group:
            clause_text = " ".join(current_clause_group)
            if len(clause_text) > 20:
                clauses.append(build_clause_object(clause_text, source_document, current_section, page_num, nlp))
                
    return clauses

def build_clause_object(text: str, doc_name: str, section: str, page_num: int, nlp=None) -> dict:
    """
    Builds structured Clause dict and performs metadata extraction (Pass 2).
    """
    clause_type = classify_clause_type(text)
    
    # Extract entities
    entities = {
        "PERSON": [],
        "ORG": [],
        "DATE": [],
        "MONEY": [],
        "TIME": []
    }
    
    if nlp:
        try:
            doc = nlp(text)
            for ent in doc.ents:
                if ent.label_ in entities:
                    entities[ent.label_].append(ent.text)
        except Exception:
            entities = extract_named_entities_fallback(text)
    else:
        entities = extract_named_entities_fallback(text)
        
    # Remove duplicates from entities lists
    for k in entities:
        entities[k] = list(set(entities[k]))
        
    return {
        "text": text,
        "clause_type": clause_type,
        "named_entities": entities,
        "section_heading": section,
        "page_number": page_num,
        "vector_id": str(uuid.uuid4())
    }
