import subprocess
import sys
from openai import OpenAI
import os
import json

client = OpenAI()

# --- Intelligent memory (indexed by error type) ---
history = {
    "IMPORT_ERROR": [],
    "SYNTAX_ERROR": [],
    "TEST_ERROR": [],
    "UNKNOWN_ERROR": []
}

# --- System state ---
state = {
    "last_error": None,
    "tests_passed": False,
    "iterations": 0,
    "last_action": None,
    "error_type": None,
    "error_message": None
}

STATE_FILE = "state.json"
HISTORY_FILE = "history.json"

def load_persistence():
    global state, history
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                state.update(json.load(f))
        except Exception as e:
            print(f"⚠️ Failed to load state: {e}")
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    history.clear()
                    history.update(data)
        except Exception as e:
            print(f"⚠️ Failed to load history: {e}")

def save_persistence():
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)
    except Exception as e:
        print(f"⚠️ Failed to save state: {e}")
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f)
    except Exception as e:
        print(f"⚠️ Failed to save history: {e}")

def run_code():
    result = subprocess.run(
        ["python", "-I", "main.py"],
        capture_output=True,
        text=True
    )
    return result

def install_missing_dependency(error: str):
    import re
    match = re.search(r"No module named '([^']+)'", error)
    if match:
        pkg = match.group(1)
        print(f"📦 Installing missing package: {pkg}")
        subprocess.run(["uv", "pip", "install", pkg])

def classify_error(error: str) -> dict:
    if not error:
        return {"type": None, "message": None}

    if "No module named" in error:
        return {"type": "IMPORT_ERROR", "message": error}

    if "SyntaxError" in error:
        return {"type": "SYNTAX_ERROR", "message": error}

    if "AssertionError" in error or "FAILED" in error:
        return {"type": "TEST_ERROR", "message": error}

    return {"type": "UNKNOWN_ERROR", "message": error}

def execute_tool(action: str, error: str):
    if action == "INSTALL_DEP":
        install_missing_dependency(error)
    elif action == "RUN_TESTS":
        return run_tests()
    elif action == "FIX_CODE":
        return fix_code(error)

import re

def clean_code(code: str) -> str:
    match = re.search(r"```(?:python)?\n(.*?)```", code, re.DOTALL)
    if match:
        return match.group(1).strip()
    return code.strip()

# --- Multi-agent functions ---
def coder_agent(current_code: str, error: str) -> str:
    prompt = f"""
    You are a Python developer.

    CURRENT CODE:
    {current_code}

    ERROR:
    {error}

    RELEVANT PREVIOUS ATTEMPTS (same error type):
    {sorted(history.get(classify_error(error)["type"], []), key=lambda x: x.get("score", 0), reverse=True)}

    Fix ONLY what is necessary.
    Do NOT repeat previous fixes.
    Return ONLY raw Python code.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return clean_code(response.choices[0].message.content)


def reviewer_agent(code: str) -> str:
    prompt = f"""
    Review the following Python code and improve it if needed.
    Do NOT change functionality unless required.
    Return ONLY raw Python code.

    CODE:
    {code}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return clean_code(response.choices[0].message.content)


def tester_agent(code: str) -> str:
    prompt = f"""
    Write pytest tests for the following Python code.
    Return ONLY valid Python test code.

    CODE:
    {code}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return clean_code(response.choices[0].message.content)

def planner_agent(state: dict) -> list:
    prompt = f"""
    You are a planning agent controlling an autonomous coding system.

    STATE:
    - last_error: {state.get("error_type")}
    - message: {state.get("error_message")}
    - tests_passed: {state.get("tests_passed")}
    - last_action: {state.get("last_action")}
    - iteration: {state.get("iterations")}

    Decide a short plan (1-3 steps max) using these actions:
    - RUN_CODE
    - FIX_CODE
    - INSTALL_DEP
    - RUN_TESTS
    - STOP

    Rules:
    - If IMPORT_ERROR → INSTALL_DEP first
    - If SYNTAX_ERROR → FIX_CODE
    - If code runs → RUN_TESTS
    - If tests pass → STOP
    - Avoid repeating same action

    Return the plan as a Python list, e.g.:
    ["INSTALL_DEP", "RUN_CODE"]
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.choices[0].message.content.strip()

    try:
        import json
        plan = json.loads(text)
        if isinstance(plan, list):
            return plan
    except (json.JSONDecodeError, ValueError, TypeError):
        pass

    return ["RUN_CODE"]

def fix_code(error):
    with open("main.py", "r") as f:
        current_code = f.read()

    # avoid identical rewrites (simple diff protection)
    original_code = current_code

    print("🧠 Coder agent fixing code...")
    code = coder_agent(current_code, error)

    print("🔍 Reviewer agent reviewing code...")
    code = reviewer_agent(code)

    print("🧪 Tester agent generating tests...")
    test_code = tester_agent(code)

    with open("test_main.py", "w") as f:
        f.write(test_code)

    err_type = classify_error(error)["type"] or "UNKNOWN_ERROR"
    history.setdefault(err_type, [])
    history[err_type].append({
        "error": error[:500],
        "code": code[:1000],
        "success": False,
        "score": 0
    })

    # limit memory size per type
    if len(history[err_type]) > 5:
        history[err_type] = history[err_type][-5:]

    # simple diff protection
    if code.strip() == original_code.strip():
        print("⚠️ No changes detected, forcing new attempt hint")

    return code

def generate_test():
    if not os.path.exists("test_main.py"):
        print("🧪 Generating test file")
        with open("test_main.py", "w") as f:
            f.write("""
def test_basic():
    assert True
""")

def run_tests():
    return subprocess.run(
        ["pytest", "-q"],
        capture_output=True,
        text=True
    )

def loop():
    generate_test()
    load_persistence()

    for i in range(10):
        state["iterations"] = i + 1
        print(f"🔁 Iteration {i+1}")

        plan = planner_agent(state)
        print(f"🧭 Planner plan: {plan}")

        for action in plan:
            state["last_action"] = action
            print(f"⚙️ Executing: {action}")

            if action == "RUN_CODE":
                result = run_code()
                if result.returncode == 0:
                    print("✅ Code runs")
                    # capture error type before reset
                    err_type = state.get("error_type")

                    state["last_error"] = None
                    state["error_type"] = None
                    state["error_message"] = None

                    # reward last memory
                    if err_type and history.get(err_type):
                        history[err_type][-1]["success"] = True
                        history[err_type][-1]["score"] += 1
                else:
                    print("❌ Error detected")
                    print(result.stderr)
                    state["last_error"] = result.stderr
                    err = classify_error(result.stderr)
                    state["error_type"] = err["type"]
                    state["error_message"] = err["message"]
                    break

            elif action == "RUN_TESTS":
                test_result = run_tests()
                if test_result.returncode == 0:
                    print("✅ Tests passed")
                    state["tests_passed"] = True
                    # strong reward for passing tests
                    for err_type, entries in history.items():
                        if entries:
                            entries[-1]["success"] = True
                            entries[-1]["score"] += 2
                    save_persistence()
                    return
                else:
                    print("❌ Tests failed")
                    print(test_result.stderr)
                    state["last_error"] = test_result.stderr
                    err = classify_error(test_result.stderr)
                    state["error_type"] = err["type"]
                    state["error_message"] = err["message"]
                    # penalize last attempt
                    err_type = state.get("error_type")
                    if err_type and history.get(err_type):
                        history[err_type][-1]["score"] -= 1
                    break

            elif action == "INSTALL_DEP":
                if state["last_error"]:
                    install_missing_dependency(state["last_error"])

            elif action == "FIX_CODE":
                if state["last_error"]:
                    fixed_code = fix_code(state["last_error"])

                    with open("main.py", "r") as f:
                        current = f.read()

                    if fixed_code.strip() != current.strip():
                        with open("main.py", "w") as f:
                            f.write(fixed_code)
                    else:
                        print("⚠️ Skipping write (no diff)")

            elif action == "STOP":
                print("🛑 Planner decided to stop")
                save_persistence()
                return
        save_persistence()

if __name__ == "__main__":
    loop()