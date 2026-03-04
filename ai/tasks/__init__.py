# ai/tasks/__init__.py
from .domain_model_task import build_domain_model_task
from .architecture_task import build_architecture_task
from .code_generation_task import build_code_generation_task
from .write_tests_task import build_write_tests_task
from .audit_code_task import build_audit_code_task
from .heal_code_task import build_heal_code_task
from .project_debug_task import build_project_debug_task
from .create_skeleton_task import build_create_skeleton_task
from .arbitration_task import build_arbitration_task
from .mapper_task import build_mapper_task
from .shared_types_task import build_shared_types_task
from .audit_task import build_audit_task
from .systemic_fix_task import build_systemic_fix_task
from .dependency_graph_task import build_dependency_graph_task
from .type_registry_task import build_type_registry_task    
from .compile_fix_task import build_compile_fix_task

__all__ = [
    "build_domain_model_task",
    "build_architecture_task",
    "build_code_generation_task",
    "build_write_tests_task",
    "build_audit_code_task",
    "build_heal_code_task",
    "build_project_debug_task",
    "build_create_skeleton_task",
    "build_arbitration_task",
    "build_mapper_task",
    "build_shared_types_task",
    "build_audit_task",
    "build_systemic_fix_task",
    "build_dependency_graph_task",
    "build_type_registry_task",
    "build_compile_fix_task"
]