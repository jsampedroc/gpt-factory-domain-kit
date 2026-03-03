# ai/pipeline/task_executor.py
import os
import sys
import time
from ai.llm.llm_config import build_llm_client, get_model_config
from ai.llm.grounding import build_grounded_prompt

# Modular Agent and Task imports
import ai.agents as agents

class TaskExecutor:
    def __init__(self):
        """
        Industrial Task Executor. 
        Dynamic client initialization per call to support hybrid providers (OpenAI/DeepSeek).
        """
        pass

    def run_task(self, task_key, context_data="", agent_override=None, **kwargs):
        """
        Executes an AI task with auto-retry logic and response validation.
        """
        # Late import to prevent circular dependency
        import ai.tasks as tasks
        
        # 1. TASK MAPPING (Sincronizado con tus nombres de archivos)
        task_map = {
            "model_domain": tasks.build_domain_model_task,
            "create_inventory": tasks.build_architecture_task,
            "write_code": tasks.build_code_generation_task,
            "write_tests": tasks.build_write_tests_task,
            "audit_code": tasks.build_audit_task,  # Sincronizado con audit_task.py
            "heal_code": tasks.build_heal_code_task,
            "project_debug": tasks.build_project_debug_task,
            "create_skeleton": tasks.build_create_skeleton_task,
            "arbitration": tasks.build_arbitration_task,
            "write_mapper": tasks.build_mapper_task, # Sincronizado con mapper_task.py
            "identify_shared_types": tasks.build_shared_types_task,
            "generate_systemic_fix": tasks.build_systemic_fix_task, # Sincronizado con systemic_fix_task.py
        }

        if task_key not in task_map:
            raise ValueError(f"❌ Task '{task_key}' is not mapped in TaskExecutor.")

        # 2. ARGUMENT SYNCHRONIZATION
        task_args = kwargs.copy()
        task_args['context_data'] = context_data
        if 'domain_kit' not in task_args:
            task_args['domain_kit'] = context_data

        # 3. BUILD TASK DEFINITION
        task_def = task_map[task_key](**task_args)
        
        # 4. AGENT RESOLUTION
        role_key = agent_override if agent_override else task_def['agent']
        
        agent_map = {
            "domain_reasoner": agents.build_domain_reasoner,
            "architect": agents.build_software_architect,
            "backend_builder": agents.build_backend_builder,
            "qa_agent": agents.build_qa_agent,
            "sre_agent": agents.build_sre_agent,
            "frontend_builder": agents.build_frontend_builder,
            "principal_architect": agents.build_principal_architect
        }
        
        if role_key not in agent_map:
            raise ValueError(f"❌ Agent '{role_key}' is not defined.")
            
        agent_config = agent_map[role_key]()
        
        # 5. LLM CONFIGURATION (Smart vs. Cheap)
        model_params = get_model_config(agent_config["tier"])
        provider = model_params.pop("provider") # Extraemos provider para build_llm_client
        
        # 6. CLIENT INITIALIZATION
        client = build_llm_client(provider=provider)
        
        # 7. GROUNDED PROMPT CONSTRUCTION
        system_rules = agent_config.get('system') or f"You are a {agent_config['role']}. {agent_config['backstory']}"
        full_prompt = build_grounded_prompt(
            system_rules=system_rules,
            context_data=context_data,
            task_prompt=task_def['description']
        )

        # 8. API INVOCATION WITH RETRIES AND VALIDATION
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"   [LLM] {task_key} via {role_key} ({provider}/{model_params['model']})...")
                response = client.chat.completions.create(
                    messages=[{"role": "user", "content": full_prompt}],
                    **model_params
                )
                
                # VALIDACIÓN CRÍTICA CONTRA EL ERROR NoneType
                if response and response.choices and len(response.choices) > 0:
                    content = response.choices[0].message.content
                    if content:
                        return content
                
                print(f"   ⚠️ Received empty response from {provider}. Retrying...")
                
            except Exception as e:
                err_msg = str(e).lower()
                # Manejo de límites de cuota y velocidad
                if "rate limit" in err_msg or "429" in err_msg or "quota" in err_msg:
                    wait_time = 30 * (attempt + 1)
                    print(f"\n⏳ API LIMIT REACHED ({provider}). Waiting {wait_time}s before retry {attempt+1}/{max_retries}...")
                    time.sleep(wait_time)
                    continue
                
                print(f"\n🚫 CRITICAL API ERROR ({provider}): {str(e)}")
                sys.exit(1)

        print(f"❌ Task '{task_key}' failed after {max_retries} attempts.")
        sys.exit(1)