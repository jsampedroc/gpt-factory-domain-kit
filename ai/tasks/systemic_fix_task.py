# ai/tasks/systemic_fix_task.py

def build_systemic_fix_task(error_log, base_path, **kwargs):
    return {
        "agent": "principal_architect",
        "description": f"""
        TASK: You are a Senior Java Architect.
        
        INPUT ERROR LOG:
        {error_log}
        
        PROJECT PATH: {base_path}
        
        GOAL:
        Analyze the Maven errors and produce a *systemic* fix as a unified diff patch.
        Focus on safe, mechanical fixes (wrong imports, javax->jakarta, wrong package declarations,
        class name != filename, missing Optional/List imports, etc.).
        
        OUTPUT FORMAT (STRICT):
        - Return ONLY a unified diff (git patch) starting with 'diff --git'.
        - The patch MUST ONLY modify files under '{base_path}'.
        - No markdown, no explanations, no extra text.
        """,
        "expected_output": "A unified diff patch (git apply compatible)."
    }