# Structured output prompt schemas and parser variables

PROMPT_THREE_STEP_1_PARAPHRASE = """
You are a highly precise legal assistant.
Your task is to analyze the following two organizational clauses and paraphrase them in plain, clear language.
Identify the core obligation, prohibition, or permission established in each clause.

Clause A:
{clause_a_text}

Clause B:
{clause_b_text}

Output the paraphrases exactly in this format:
Paraphrase Clause A: [Paraphrase here]
Paraphrase Clause B: [Paraphrase here]
"""

PROMPT_THREE_STEP_2_SCENARIO = """
Based on the paraphrased clauses, analyze if there is a conflict scenario where complying with Clause A would result in a direct violation of Clause B (or vice versa), or if their compliance terms are logically inconsistent.

Paraphrases:
{paraphrases}

If no conflict scenario can be conceived under any operational context, output exactly "NO_SCENARIO".
Otherwise, describe the specific conflict scenario in detail:
Conflict Scenario: [Conflict details here]
"""

PROMPT_THREE_STEP_3_CLASSIFICATION = """
Based on the paraphrases and conflict scenario, perform a formal contradiction classification.
You must output a structured JSON matching the requested formatting instructions.

Paraphrases:
{paraphrases}

Conflict Scenario:
{scenario}

{format_instructions}
"""

PROMPT_SINGLE_COMBINED = """
You are a highly precise legal assistant operating on an edge resource.
Analyze the following two organizational clauses, identify if there is any semantic contradiction, and perform a complete evaluation in a single step.

Clause A:
{clause_a_text}

Clause B:
{clause_b_text}

Determine if following Clause A would violate Clause B, or if there is an operational overlap/supersession.
You must output a structured JSON matching the requested formatting instructions.

{format_instructions}
"""
