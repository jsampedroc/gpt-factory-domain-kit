# ai/llm/grounding.py

def build_grounded_prompt(*, system_rules, context_data, task_prompt):
    """
    Industrial-grade prompt builder designed to enforce strict context-based 
    reasoning and prevent model hallucinations.
    """
    return f"""[SYSTEM]
{system_rules}

[BUSINESS CONTEXT & DOMAIN KIT]
{context_data}

[TASK]
{task_prompt}

[OUTPUT CONTRACT]
- Provide ONLY the direct content of the requested file.
- DO NOT use Markdown code blocks (e.g., NEVER use ```java or ```json).
- DO NOT include any introductions, conversational filler, or closing remarks.
- Strictly adhere to the naming conventions and package structures defined in the context.
- If the output is JSON, it must be valid and directly parseable by Python's json library.
""".strip()