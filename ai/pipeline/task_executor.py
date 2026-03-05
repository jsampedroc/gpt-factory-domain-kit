# ai/pipeline/task_executor.py
import sys
import time

from ai.llm.llm_config import build_llm_client, get_model_config
from ai.llm.grounding import build_grounded_prompt


from ai.agents.software_architect import build_software_architect
from ai.agents.backend_builder import build_backend_builder
from ai.agents.frontend_builder import build_frontend_builder
from ai.agents.qa_agent import build_qa_agent
from ai.agents.sre_agent import build_sre_agent
from ai.agents.principal_architect import build_principal_architect



class TaskExecutor:

    TASK_MAP = {
        # DOMAIN
        "model_domain": lambda tasks, **k: tasks.build_domain_model_task(**k),
        "identify_shared_types": lambda tasks, **k: tasks.build_shared_types_task(**k),

        # NEW PIPELINE LAYERS
        "type_registry": lambda tasks, **k: tasks.build_type_registry_task(**k),
        "dependency_graph": lambda tasks, **k: tasks.build_dependency_graph_task(**k),

        # ARCHITECTURE
        "create_inventory": lambda tasks, **k: tasks.build_architecture_task(**k),

        # CODE GENERATION
        "write_code": lambda tasks, **k: tasks.build_code_generation_task(**k),
        "write_mapper": lambda tasks, **k: tasks.build_mapper_task(**k),
        "write_tests": lambda tasks, **k: tasks.build_write_tests_task(**k),

        # QUALITY
        "audit_code": lambda tasks, **k: tasks.build_audit_task(**k),
        "heal_code": lambda tasks, **k: tasks.build_heal_code_task(**k),
        # COMPILE FIX
        "fix_compile_error": lambda tasks, **k: tasks.build_compile_fix_task(**k),

        # DEBUG
        "project_debug": lambda tasks, **k: tasks.build_project_debug_task(**k),
        "generate_systemic_fix": lambda tasks, **k: tasks.build_systemic_fix_task(**k),

        # BOOTSTRAP
        "create_skeleton": lambda tasks, **k: tasks.build_create_skeleton_task(**k),

        # ARBITRATION
        "arbitration": lambda tasks, **k: tasks.build_arbitration_task(**k),
    }

    def __init__(self):
        """
        Industrial Task Executor.
        Supports hybrid LLM providers (OpenAI / DeepSeek / Local).
        """
        pass


    def run_task(self, task_key, context_data="", agent_override=None, **kwargs):

        # Late import (avoid circular imports)
        import ai.tasks as tasks

        # -------------------------------------------------------
        # TASK REGISTRY
        # -------------------------------------------------------

        task_map = self.TASK_MAP

        if task_key not in task_map:
            raise ValueError(f"❌ Task '{task_key}' is not mapped in TaskExecutor.")

        # -------------------------------------------------------
        # ARGUMENT SYNCHRONIZATION
        # -------------------------------------------------------

        task_args = kwargs.copy()

        task_args["context_data"] = context_data

        if "domain_kit" not in task_args:
            task_args["domain_kit"] = context_data

        # -------------------------------------------------------
        # BUILD TASK
        # -------------------------------------------------------

        task_def = task_map[task_key](tasks, **task_args)

        # -------------------------------------------------------
        # AGENT RESOLUTION
        # -------------------------------------------------------

        role_key = agent_override if agent_override else task_def["agent"]

        agent_map = {
            "domain_reasoner": build_domain_reasoner,
            "architect": build_software_architect,
            "backend_builder": build_backend_builder,
            "frontend_builder": build_frontend_builder,
            "qa_agent": build_qa_agent,
            "sre_agent": build_sre_agent,
            "principal_architect": build_principal_architect,
        }

        if role_key not in agent_map:
            raise ValueError(f"❌ Agent '{role_key}' is not defined.")

        agent_config = agent_map[role_key]()

        # -------------------------------------------------------
        # MODEL CONFIGURATION
        # -------------------------------------------------------

        model_params = get_model_config(agent_config["tier"])

        provider = model_params.pop("provider")

        client = build_llm_client(provider=provider)

        # -------------------------------------------------------
        # PROMPT BUILDING
        # -------------------------------------------------------

        system_rules = (
            agent_config.get("system")
            or f"You are a {agent_config['role']}. {agent_config['backstory']}"
        )

        full_prompt = build_grounded_prompt(
            system_rules=system_rules,
            context_data=context_data,
            task_prompt=task_def["description"]
        )

        # -------------------------------------------------------
        # LLM CALL
        # -------------------------------------------------------

        max_retries = 3
        base_wait = 10

        for attempt in range(max_retries):

            try:

                print(
                    f"   [LLM] {task_key} via {role_key} "
                    f"({provider}/{model_params['model']})..."
                )

                response = client.chat.completions.create(
                    messages=[{"role": "user", "content": full_prompt}],
                    **model_params
                )

                if response and response.choices:

                    content = response.choices[0].message.content

                    if content:
                        return content

                print("   ⚠️ Empty response received. Retrying...")

            except Exception as e:

                err = str(e).lower()

                if "rate limit" in err or "429" in err or "quota" in err:

                    wait = base_wait * (attempt + 1)

                    print(
                        f"\n⏳ API LIMIT ({provider}). "
                        f"Waiting {wait}s before retry {attempt+1}/{max_retries}"
                    )

                    time.sleep(wait)

                    continue

                raise RuntimeError(
                    f"Critical API error from {provider}: {e}"
                )

        raise RuntimeError(
            f"Task '{task_key}' failed after {max_retries} attempts."
        )