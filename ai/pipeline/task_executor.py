# ai/pipeline/task_executor.py
import os
import sys
import time

from ai.llm.llm_config import build_llm_client, get_model_config
from ai.llm.grounding import build_grounded_prompt

import ai.agents as agents


class TaskExecutor:

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

        task_map = {

            # DOMAIN
            "model_domain": tasks.build_domain_model_task,
            "identify_shared_types": tasks.build_shared_types_task,

            # NEW PIPELINE LAYERS
            "type_registry": tasks.build_type_registry_task,
            "dependency_graph": tasks.build_dependency_graph_task,

            # ARCHITECTURE
            "create_inventory": tasks.build_architecture_task,

            # CODE GENERATION
            "write_code": tasks.build_code_generation_task,
            "write_mapper": tasks.build_mapper_task,
            "write_tests": tasks.build_write_tests_task,

            # QUALITY
            "audit_code": tasks.build_audit_task,
            "heal_code": tasks.build_heal_code_task,

            # DEBUG
            "project_debug": tasks.build_project_debug_task,
            "generate_systemic_fix": tasks.build_systemic_fix_task,

            # BOOTSTRAP
            "create_skeleton": tasks.build_create_skeleton_task,

            # ARBITRATION
            "arbitration": tasks.build_arbitration_task,
        }

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

        task_def = task_map[task_key](**task_args)

        # -------------------------------------------------------
        # AGENT RESOLUTION
        # -------------------------------------------------------

        role_key = agent_override if agent_override else task_def["agent"]

        agent_map = {
            "domain_reasoner": agents.build_domain_reasoner,
            "architect": agents.build_software_architect,
            "backend_builder": agents.build_backend_builder,
            "frontend_builder": agents.build_frontend_builder,
            "qa_agent": agents.build_qa_agent,
            "sre_agent": agents.build_sre_agent,
            "principal_architect": agents.build_principal_architect
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

                    wait = 30 * (attempt + 1)

                    print(
                        f"\n⏳ API LIMIT ({provider}). "
                        f"Waiting {wait}s before retry {attempt+1}/{max_retries}"
                    )

                    time.sleep(wait)

                    continue

                print(f"\n🚫 CRITICAL API ERROR ({provider}): {e}")

                sys.exit(1)

        print(f"❌ Task '{task_key}' failed after {max_retries} attempts.")

        sys.exit(1)