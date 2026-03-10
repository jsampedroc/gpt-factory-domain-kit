# main.py — AI SOFTWARE FACTORY (STABLE, HARDENED, PROFESSIONAL)
import sys
import json
import yaml
import re
import os
import subprocess
import time
import hashlib
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict 
from dotenv import load_dotenv
from datetime import datetime
from ai.codegen.template_java_generator import TemplateJavaGenerator
from ai.pipeline.state_manager import StateManager
from ai.pipeline.task_executor import TaskExecutor
from ai.pipeline.pipeline_engine import PipelineEngine, PipelineStep
from ai.utils.logging_helper import Tee
from ai.utils.architecture_logger import ArchitectureLogger
from ai.debug.pipeline_trace_logger import PipelineTraceLogger
from ai.validators.layer_contracts import LayerContracts

from ai.validators.structural_code_guard import StructuralCodeGuard
from ai.validators.field_validator import FieldValidator

from ai.domain.semantic_domain_agent import SemanticDomainAgent
from ai.graph.task_graph_builder import TaskGraphBuilder
from ai.analysis.import_dependency_analyzer import ImportDependencyAnalyzer
import ast  
from collections import defaultdict
from ai.knowledge.domain_memory import DomainMemory
from ai.knowledge.compile_memory import CompileMemory
from ai.graph.code_dependency_graph import CodeDependencyGraph
from ai.agents.refactor_agent import RefactorAgent
from ai.agents.runtime_feedback_agent import RuntimeFeedbackAgent  # TODO: implement this module
from ai.agents.evolution_agent import EvolutionAgent
from ai.agents.code_generation_agent import CodeGenerationAgent
from ai.domain.domain_model_validator import validate_domain_model
from ai.graph.dependency_graph_builder import DependencyGraphBuilder

from ai.planning.domain_graph_builder import DomainGraphBuilder
from ai.planning.semantic_code_graph_builder import SemanticCodeGraphBuilder
from ai.planning.spec_graph_builder import SpecGraphBuilder
from ai.planning.deterministic_spec_generator import DeterministicSpecGenerator
from ai.planning.code_planner import CodePlanner
from ai.planning.impact_analyzer import ImpactAnalyzer

from ai.codegen.import_resolver import resolve_imports
from ai.codegen.ast_java_generator import ASTJavaGenerator
from ai.codegen.java_type_resolver import JavaTypeResolver
from ai.agents.file_codegen_agent import FileCodeGenerationAgent
from ai.codegen.llm_code_generator import LLMCodeGenerator
from ai.domain.business_capability_agent import BusinessCapabilityAgent
from ai.planning.usecase_planner_agent import UseCasePlannerAgent
from ai.domain.semantic_type_detector import TypeDiscoveryEngine
from ai.domain.semantic_type_detector import detect_semantic_types

from ai.domain.aggregate_lifecycle_agent import AggregateLifecycleAgent
from ai.codegen.deterministic_skeleton_builder import DeterministicSkeletonBuilder

# ---- AGGREGATE & BOUNDED CONTEXT DETECTORS ----
from ai.domain.aggregate_detector import AggregateDetector
from ai.domain.bounded_context_detector import BoundedContextDetector
from ai.domain.module_architecture_agent import ModuleArchitectureAgent








# ------------------ Agents ------------------

class ProjectPlannerAgent:
    """
    High-level planning agent that can pre-structure the idea before
    the domain modeling phase. This mimics the planning step used in
    systems like Devin / Manus.
    """

    def run(self, factory):
        try:
            plan = factory.executor.run_task(
                "project_planner",
                idea=factory.idea,
                base_package=factory.base_package
            )

            if isinstance(plan, str):
                return json.loads(plan)

            return plan

        except Exception:
            # Planner is optional — fallback to raw idea
            return {"idea": factory.idea}

class DomainAgent:
    def run(self, factory):
        raw = factory.executor.run_task(
            "model_domain",
            idea=factory.idea,
            base_package=factory.base_package,
        )
        domain_model = json.loads(raw)
        return domain_model


class SemanticAgent:
    """
    Delegates semantic enrichment to the SemanticDomainAgent module.
    This keeps semantic logic outside the orchestrator layer.
    """

    def __init__(self):
        self.agent = SemanticDomainAgent()

    def run(self, factory, domain_model):
        return self.agent.run(domain_model)



class ArchitectureReasoningAgent:
    """
    Decides the architecture style (hexagonal, modular_monolith, simple)
    based on the detected domain complexity.
    """

    def run(self, factory, domain_model):

        dm = domain_model.get("domain_model", domain_model)

        entity_count = len(dm.get("entities", []))
        aggregates = len(dm.get("aggregates", []))

        if aggregates > 3:
            style = "hexagonal"
        elif entity_count > 12:
            style = "modular_monolith"
        else:
            style = "simple"

        return {
            "architecture_style": style
        }

class ArchitectureAgent:
    def run(self, factory, domain_model):
        return {
            "file_inventory": factory.generate_inventory(domain_model)
        }


class CodeGenerationAgent:
    def run(self, factory, inventory):
        """
        Generates files in batches by architectural layer to improve LLM coherence.
        Order: domain → application → infrastructure.
        Each batch still runs in parallel internally.
        """

        # --- Dependency‑aware ordering using task graph ---
        task_graph = getattr(factory.state, "task_graph", None)

        if task_graph and isinstance(task_graph, list):

            graph = {}
            indegree = {}

            for t in task_graph:
                if not isinstance(t, dict):
                    continue

                p = t.get("path")
                deps = t.get("depends_on", []) or []

                if not p:
                    continue

                graph[p] = set(deps)
                indegree.setdefault(p, 0)

                for d in deps:
                    indegree.setdefault(d, 0)
                    indegree[p] += 1

            # Kahn topological sort
            queue = [p for p, deg in indegree.items() if deg == 0]
            ordered_paths = []

            while queue:
                node = queue.pop(0)
                ordered_paths.append(node)

                for target, deps in graph.items():
                    if node in deps:
                        indegree[target] -= 1
                        deps.remove(node)
                        if indegree[target] == 0:
                            queue.append(target)

            if ordered_paths:
                path_index = {p: i for i, p in enumerate(ordered_paths)}
                inventory = sorted(
                    inventory,
                    key=lambda x: path_index.get(x.get("path"), len(path_index))
                )

                factory.log(f"🧠 Dependency‑aware scheduling applied ({len(ordered_paths)} tasks)")

        batches = {
            "domain": [],
            "application": [],
            "infrastructure": [],
            "other": []
        }

        for item in inventory:
            path = item["path"]

            # Support modular structure modules/<module>/...
            if path.startswith("modules/"):
                parts = path.split("/", 2)
                if len(parts) >= 3:
                    path = parts[2]

            if path.startswith("domain/"):
                batches["domain"].append(item)
            elif path.startswith("application/"):
                batches["application"].append(item)
            elif path.startswith("infrastructure/"):
                batches["infrastructure"].append(item)
            else:
                batches["other"].append(item)

        ordered_batches = [
            ("domain", batches["domain"]),
            ("application", batches["application"]),
            ("infrastructure", batches["infrastructure"]),
            ("other", batches["other"]),
        ]

        total = len(inventory)
        workers = min(4, os.cpu_count() or 4)
        index = 0

        for layer, items in ordered_batches:

            if not items:
                continue

            factory.log(f"🧱 Generating {layer} layer ({len(items)} files)")

            with ThreadPoolExecutor(max_workers=workers) as pool:
                futures = []

                for item in items:
                    index += 1
                    futures.append(
                        pool.submit(
                            factory._generate_single_file,
                            item,
                            index,
                            total
                        )
                    )

                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        factory.log(f"⚠️ Code generation task failed: {e}")
                        factory.log("↻ Retrying file generation sequentially")

                        try:
                            item = getattr(e, "item", None)
                            if item:
                                factory._generate_single_file(item, 0, total)
                        except Exception as retry_err:
                            factory.log(f"❌ Retry failed: {retry_err}")


class CompileAgent:
    def run(self, factory):
        success, output = factory._compile_project()
        return success, output


class CompileFixAgent:
    def run(self, factory, compile_output):
        patterns = []

        try:
            memory = getattr(factory, "compile_memory", None)
            if memory:
                patterns = memory.get_patterns()
        except Exception:
            patterns = []

        fixed = factory.executor.run_task(
            "fix_compile_error",
            error_log=compile_output,
            known_patterns=json.dumps(patterns),
            base_package=factory.base_package
        )

        # store learned compile error pattern
        try:
            memory = getattr(factory, "compile_memory", None)
            if memory and fixed:
                memory.record(
                    error=compile_output[:500],
                    fix=json.dumps(fixed)[:500] if fixed else ""
                )
        except Exception:
            pass

        return fixed


# ------------------ Test Agent ------------------
# ------------------ Test Agent ------------------
class TestAgent:
    """
    Generates and runs tests for the generated code.
    If tests fail, it can request fixes from the LLM.
    """

    def run(self, factory):
        backend_path = factory.output_root / "backend"

        if not backend_path.exists():
            factory.log("⚠️ Backend directory not found, skipping tests")
            return True, ""

        try:
            factory.log("🧪 Running Maven tests...")

            result = subprocess.run(
                ["mvn", "-q", "test"],
                cwd=backend_path,
                capture_output=True,
                text=True
            )

            output = result.stdout + "\n" + result.stderr

            if result.returncode == 0:
                factory.log("✅ Tests passed")
                return True, output
            else:
                factory.log("❌ Tests failed")
                factory.log(output)
                return False, output

        except FileNotFoundError:
            factory.log("⚠️ Maven not installed, skipping tests")
            return True, ""


# ------------------ Test Generator Agent ------------------
class TestGeneratorAgent:
    """
    Generates basic JUnit tests for generated services and controllers.
    This improves QA loops in the factory pipeline.
    """

    def run(self, factory, inventory):
        generated = 0

        for item in inventory:
            rel = item.get("path")

            if not rel or not rel.endswith(".java"):
                continue

            if "/service/" not in rel and "/rest/" not in rel:
                continue

            test_rel = rel.replace(".java", "Test.java")

            try:
                factory.executor.run_task(
                    "generate_test",
                    path=test_rel,
                    source_path=rel,
                    base_package=factory.base_package
                )
                generated += 1
            except Exception:
                continue

        factory.log(f"🧪 Test generator created {generated} tests")


# ------------------ Critic Agent ------------------
class CriticAgent:
    """
    Reviews generated code and can trigger improvement cycles.
    """

    def run(self, factory):
        try:
            report = factory.executor.run_task(
                "critic_codebase",
                idea=factory.idea,
                base_package=factory.base_package
            )

            if isinstance(report, str):
                try:
                    report = json.loads(report)
                except Exception:
                    report = {"summary": report}

            return report

        except Exception as e:
            factory.log(f"⚠️ Critic phase skipped: {e}")
            return None



# ------------------ Repair Agent ------------------
class RepairAgent:
    """
    Attempts to repair issues detected by the critic.
    """

    def run(self, factory, critic_report):
        try:
            # If critic provides specific problematic files, repair them individually
            files = critic_report.get("files") if isinstance(critic_report, dict) else None

            if files and isinstance(files, list):
                factory.log(f"🛠 Targeted repair for {len(files)} files")

                for path in files:
                    try:
                        factory.executor.run_task(
                            "repair_file",
                            path=path,
                            report=json.dumps(critic_report),
                            base_package=factory.base_package
                        )
                    except Exception as e:
                        factory.log(f"⚠️ File repair skipped for {path}: {e}")

                return True

            # fallback: repair entire codebase
            result = factory.executor.run_task(
                "repair_codebase",
                report=json.dumps(critic_report),
                base_package=factory.base_package
            )

            return result

        except Exception as e:
            factory.log(f"⚠️ Repair phase skipped: {e}")
            return None


# ------------------ Architecture Guard Agent ------------------
class ArchitectureGuardAgent:
    """
    Validates that generated code respects architectural layer boundaries.
    Prevents domain from importing infrastructure, etc.
    """

    FORBIDDEN_IMPORTS = {
        "domain": [".infrastructure.", ".rest.", ".persistence."],
        "application": [".rest."]
    }

    def run(self, factory, inventory):
        violations = []

        for item in inventory:
            rel = item.get("path")
            if not rel or not rel.endswith(".java"):
                continue

            layer = rel.split("/")[0]

            file_path = factory.resolve_output_path(rel)
            if not file_path.exists():
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
            except Exception:
                continue

            forbidden = self.FORBIDDEN_IMPORTS.get(layer, [])

            for f in forbidden:
                if f in content:
                    violations.append((rel, f))

        if violations:
            factory.log(f"🚨 Architecture violations detected: {len(violations)}")
            for v in violations:
                factory.log(f"  - {v[0]} imports forbidden dependency {v[1]}")
        else:
            factory.log("🛡 Architecture guard passed")

        return len(violations) == 0


# ------------------ Orchestrator ------------------

class FactoryOrchestrator:

    def __init__(self, factory):
        self.factory = factory
        self.project_planner = ProjectPlannerAgent()
        self.domain_agent = DomainAgent()
        # Skeleton builder must receive the SoftwareFactory instance, not the orchestrator
        self.skeleton_builder = DeterministicSkeletonBuilder(factory)
        self.semantic_agent = SemanticAgent()
        self.aggregate_detector = AggregateDetector()
        self.bounded_context_detector = BoundedContextDetector()
        self.capability_agent = BusinessCapabilityAgent()
        self.usecase_planner = UseCasePlannerAgent()
        self.aggregate_lifecycle_agent = AggregateLifecycleAgent()
        self.module_architecture_agent = ModuleArchitectureAgent()
        self.architecture_reasoning_agent = ArchitectureReasoningAgent()
        self.architecture_agent = ArchitectureAgent()
        self.codegen_agent = CodeGenerationAgent()
        self.critic_agent = CriticAgent()
        self.repair_agent = RepairAgent()
        self.architecture_guard = ArchitectureGuardAgent()
        self.compile_agent = CompileAgent()
        self.compile_fix_agent = CompileFixAgent()
        self.test_agent = TestAgent()
        self.test_generator_agent = TestGeneratorAgent()
        self.task_graph_builder = TaskGraphBuilder()
        self.import_dependency_analyzer = ImportDependencyAnalyzer()
        self.code_dependency_graph = CodeDependencyGraph()
        self.deterministic_spec_generator = DeterministicSpecGenerator()
        
        self.ast_generator = ASTJavaGenerator()
        self.field_validator = FieldValidator()
        self.structural_guard = StructuralCodeGuard()
        self.file_codegen_agent = FileCodeGenerationAgent(factory)

        self.code_planner = CodePlanner()
        self.refactor_agent = RefactorAgent()
        self.runtime_feedback_agent = RuntimeFeedbackAgent()  # TODO: implement this module
        self.evolution_agent = EvolutionAgent()
        self.domain_graph_builder = DomainGraphBuilder()
        self.spec_graph_builder = SpecGraphBuilder()
        self.semantic_code_graph_builder = SemanticCodeGraphBuilder()  
        self.semantic_agent = SemanticAgent()
        

        # compile error learning memory
        try:
            self.compile_memory = CompileMemory()
        except Exception:
            self.compile_memory = None

        # ---- ARCHITECTURE LOGGER ----
        # (removed duplicate initialization; logger is on the factory)
        


    def run(self):

        f = self.factory

        # attach compile memory so agents can use it
        if getattr(self, "compile_memory", None):
            setattr(f, "compile_memory", self.compile_memory)

        f.log("🧠 Orchestrator starting")

        try:
            if getattr(f, "trace_logger", None):
                f.trace_logger.log_step("START", {"idea": f.idea})
        except Exception:
            pass

        # ---- BOOTSTRAP (project skeleton) ----
        f._bootstrap_pom()
        f._bootstrap_domain_kernel()

        previous_domain = None
        if f.spec_file.exists():
            try:
                data = json.loads(f.spec_file.read_text())
                previous_domain = data.get("domain_model")
            except Exception:
                previous_domain = None

        if StateManager.load_specs(f.spec_file, f.state):
            f.log("📦 Loaded cached domain model and architecture")
        else:
            # ---- PROJECT PIPELINE (planning → domain → architecture) ----

            def step_plan(factory):
                plan = self.project_planner.run(factory)
                if isinstance(plan, dict) and plan.get("idea"):
                    factory.idea = plan["idea"]
                return plan

            def step_domain(factory):
                domain_model = self.domain_agent.run(factory)
                domain_model = self.semantic_agent.run(factory, domain_model)

                # ---- AGGREGATE DETECTION ----
                try:
                    domain_model = self.aggregate_detector.detect(domain_model)
                    dm = domain_model.get("domain_model", domain_model)
                    aggs = dm.get("aggregates", [])
                    factory.log(f"🧱 Aggregate roots detected ({len(aggs)})")
                    # ---- AGGREGATE LIFECYCLE GENERATION ----
                    try:
                        lifecycle_usecases = self.aggregate_lifecycle_agent.run(domain_model)

                        if lifecycle_usecases:
                            existing = getattr(factory.state, "usecases", [])
                            existing.extend(lifecycle_usecases)
                            factory.state.usecases = existing

                            factory.log(
                                f"🔁 Aggregate lifecycle generated ({len(lifecycle_usecases)} use cases)"
                            )

                    except Exception as e:
                        factory.log(f"⚠️ Lifecycle generation skipped: {e}")
                except Exception as e:
                    factory.log(f"⚠️ Aggregate detection skipped: {e}")

                # ---- BOUNDED CONTEXT DETECTION ----
                try:
                    domain_model = self.bounded_context_detector.detect(domain_model)
                    dm = domain_model.get("domain_model", domain_model)
                    contexts = dm.get("bounded_contexts", {})
                    factory.log(f"🧭 Bounded contexts detected ({len(contexts)})")
                except Exception as e:
                    factory.log(f"⚠️ Bounded context detection skipped: {e}")

                # ---- MODULE ARCHITECTURE ----
                try:
                    domain_model = self.module_architecture_agent.run(domain_model)
                    dm = domain_model.get("domain_model", domain_model)
                    modules = dm.get("modules", {})
                    factory.log(f"📦 Domain modules detected ({len(modules)})")
                except Exception as e:
                    factory.log(f"⚠️ Module architecture skipped: {e}")

                # ---- BUSINESS CAPABILITY DISCOVERY ----
                try:
                    capabilities = self.capability_agent.run(domain_model)
                    factory.state.capabilities = capabilities
                    factory.log(f"🧠 Business capabilities discovered ({len(capabilities)})")
                except Exception as e:
                    factory.log(f"⚠️ Capability discovery skipped: {e}")

                # ---- USE CASE PLANNING ----
                try:
                    caps = getattr(factory.state, "capabilities", [])
                    usecases = self.usecase_planner.run(domain_model, caps)
                    factory.state.usecases = usecases
                    factory.log(f"🧩 Use cases planned ({len(usecases)})")
                except Exception as e:
                    factory.log(f"⚠️ Use case planning skipped: {e}")

                # ---- TYPE DISCOVERY ENGINE ----
                try:
                    from ai.domain.semantic_type_detector import TypeDiscoveryEngine

                    engine = TypeDiscoveryEngine()
                    discovered = engine.discover(domain_model)

                    if discovered:
                        dm = domain_model.get("domain_model", domain_model)
                        dm.setdefault("value_objects", []).extend(discovered)

                        factory.log(
                            f"🧠 Type discovery created {len(discovered)} value objects"
                        )

                except Exception as e:
                    factory.log(f"⚠️ Type discovery skipped: {e}")



                validate_domain_model(domain_model)
                factory.log("✅ Domain model validated")

                try:
                    if getattr(factory, "trace_logger", None):
                        factory.trace_logger.log_step("DOMAIN_MODEL_VALIDATED", domain_model)
                except Exception:
                    pass


                domain_model = factory.enrich_domain(domain_model)
                # Keep the local AST type resolver in sync with discovered value objects
                try:
                    dm = domain_model.get("domain_model", domain_model)
                    vo_names = [v.get("name") for v in (dm.get("value_objects", []) or []) if v.get("name")]
                    if hasattr(factory, "ast_generator") and hasattr(factory.ast_generator, "set_value_objects"):
                        factory.ast_generator.set_value_objects(vo_names)
                except Exception:
                    pass
                factory.learn_domain(domain_model)

                dm = domain_model.get("domain_model", domain_model)

                factory.log(
                    f"🧠 Semantic enrichment applied "
                    f"(value_objects={len(dm.get('value_objects', []))}, "
                    f"entities={len(dm.get('entities', []))})"
                )

                factory.state.domain_model = domain_model
                dm = domain_model.get("domain_model", domain_model)
                factory.state.aggregates = dm.get("aggregates", [])
                factory.state.bounded_contexts = dm.get("bounded_contexts", {})

                # ---- DOMAIN GRAPH BUILD ----
                try:
                    graph = self.domain_graph_builder.build(domain_model)
                    factory.state.domain_graph = graph
                    factory.log(f"🧩 Domain graph built ({len(graph)} relations)")

                    try:
                        if getattr(factory, "trace_logger", None):
                            factory.trace_logger.log_step("DOMAIN_GRAPH", graph)
                    except Exception:
                        pass


                except Exception as e:
                    factory.log(f"⚠️ Domain graph skipped: {e}")
                
                # ---- SEMANTIC CODE GRAPH BUILD ----
                try:
                    semantic_graph = self.semantic_code_graph_builder.build(domain_model)
                    factory.state.semantic_code_graph = semantic_graph
                    factory.log(f"🧠 Semantic code graph built ({len(semantic_graph)} entities)")

                    try:
                        if getattr(factory, "trace_logger", None):
                            factory.trace_logger.log_step("SEMANTIC_CODE_GRAPH", semantic_graph)
                    except Exception:
                        pass

                except Exception as e:
                    factory.log(f"⚠️ Semantic graph skipped: {e}")

                # ---- SPEC GRAPH BUILD ----
                try:
                    spec_graph = self.spec_graph_builder.build(domain_model)
                    factory.state.spec_graph = spec_graph
                    factory.log(f"📐 Spec graph built ({len(spec_graph)} entities)")
                except Exception as e:
                    factory.log(f"⚠️ Spec graph skipped: {e}")

                # ---- DETERMINISTIC SPEC BUILD ----
                try:
                    deterministic_spec = self.deterministic_spec_generator.build(domain_model)
                    factory.state.deterministic_spec = deterministic_spec
                    factory.log(f"🧾 Deterministic spec built ({len(deterministic_spec)} entities)")
                except Exception as e:
                    factory.log(f"⚠️ Deterministic spec skipped: {e}")

                # ---- CODE PLAN BUILD ----
                try:
                    code_plan = self.code_planner.build(domain_model)
                    factory.state.code_plan = code_plan
                    factory.log(f"🧠 Code plan built ({len(code_plan)} entities)")
                except Exception as e:
                    factory.log(f"⚠️ Code plan skipped: {e}")

                return domain_model

            def step_architecture(factory):
                domain_model = factory.state.domain_model

                architecture_style = self.architecture_reasoning_agent.run(factory, domain_model)
                factory.log(f"🏗 Architecture style selected: {architecture_style['architecture_style']}")

                architecture = self.architecture_agent.run(factory, domain_model)

                task_graph = self.task_graph_builder.build(architecture)
                factory.log(f"🧩 Task graph built ({len(task_graph)} tasks)")
                factory.state.task_graph = task_graph

                from ai.graph.dependency_graph_builder import DependencyGraphBuilder

                graph = DependencyGraphBuilder()
                ordered_inventory = graph.order_inventory(architecture)
                architecture["file_inventory"] = ordered_inventory

                factory.log(f"📦 Dependency ordering applied ({len(ordered_inventory)} files)")

                factory.state.architecture = architecture

                StateManager.save_specs(
                    factory.spec_file,
                    factory.state.domain_model,
                    factory.state.architecture,
                    factory.state.signatures
                )

                return architecture

            pipeline = PipelineEngine([
                PipelineStep("plan_project", step_plan),
                PipelineStep("model_domain", step_domain),
                PipelineStep("design_architecture", step_architecture),
            ])

            pipeline.run(f)

        inventory = f.state.architecture["file_inventory"]

        # Generate deterministic skeletons first
        self.skeleton_builder.build(inventory)

        # ---- IMPACT ANALYSIS ----
        try:
            if previous_domain and f.state.domain_model:
                old_entities = {e.get("name") for e in previous_domain.get("entities", [])}
                new_entities = {e.get("name") for e in f.state.domain_model.get("domain_model", f.state.domain_model).get("entities", [])}

                changed_entities = new_entities.symmetric_difference(old_entities)

                if changed_entities:
                    f.log(f"🧠 Impact analysis detected changes in: {sorted(changed_entities)}")

                    graph = getattr(f.state, "semantic_code_graph", None)

                    if not graph:
                        graph = getattr(f.state, "domain_graph", {})

                    analyzer = ImpactAnalyzer(graph)

                    impacted = analyzer.compute_impacted_files(inventory, changed_entities)

                    if impacted:
                        inventory = [i for i in inventory if i.get("path") in impacted]
                        f.log(f"⚡ Selective regeneration: {len(inventory)} impacted files")
        except Exception as e:
            f.log(f"⚠️ Impact analysis skipped: {e}")

        # ---- CODE GENERATION AGENTS ----
        f.log("⚙️ Starting parallel code generation")
        self.codegen_agent.run(f, inventory)

        f.log("🚀 Code generation finished")

        # ---- ARCHITECTURE TREE LOG ----
        try:
            src_root = (
                f.output_root
                / "backend"
                / "src"
                / "main"
                / "java"
                / Path(f.base_package_path)
            )
            tree_file = f.output_root / "architecture_tree.txt"

            if not src_root.exists():
                f.log(f"⚠️ Source root not found for architecture tree: {src_root}")
                return

            f.log(f"📦 Generating architecture tree from root: {src_root}")

            # prefer the logger attached to the factory instance
            logger = getattr(f, "architecture_logger", None)
            if logger is None:
                raise RuntimeError("ArchitectureLogger not initialized in SoftwareFactory")

            logger.log_tree(src_root, tree_file)

            if not tree_file.exists():
                raise RuntimeError(f"tree file was not created: {tree_file}")

            f.log(f"📦 Architecture tree written to {tree_file}")

            # ---- ARCHITECTURE MARKDOWN REPORT ----
            try:
                md_file = f.output_root / "architecture.md"

                lines = ["# Generated Architecture", "", "## Project Structure", ""]

                for path in sorted(src_root.rglob("*.java")):
                    rel = path.relative_to(src_root)
                    pkg = str(rel.parent).replace("/", ".")
                    class_name = path.stem
                    lines.append(f"- `{pkg}.{class_name}`")

                md_file.write_text("\n".join(lines), encoding="utf-8")

                f.log(f"🧾 Architecture markdown written to {md_file}")

                # ---- DIAGNOSTIC REPORTS (DEBUGGING FACTORY STRUCTURE) ----
                try:
                    inventory_file = f.output_root / "inventory.json"
                    domain_graph_file = f.output_root / "domain_graph.json"
                    semantic_graph_file = f.output_root / "semantic_code_graph.json"

                    # inventory
                    try:
                        with inventory_file.open("w", encoding="utf-8") as fp:
                            json.dump(inventory, fp, indent=2)
                    except Exception:
                        pass

                    # domain graph
                    try:
                        with domain_graph_file.open("w", encoding="utf-8") as fp:
                            json.dump(getattr(f.state, "domain_graph", {}), fp, indent=2)
                    except Exception:
                        pass

                    # semantic code graph
                    try:
                        with semantic_graph_file.open("w", encoding="utf-8") as fp:
                            json.dump(getattr(f.state, "semantic_code_graph", {}), fp, indent=2)
                    except Exception:
                        pass

                    f.log("📊 Diagnostic reports generated (inventory, domain_graph, semantic_code_graph)")

                except Exception as e:
                    f.log(f"⚠️ Diagnostic report generation skipped: {e}")

            except Exception as e:
                f.log(f"⚠️ Architecture markdown generation skipped: {e}")
        except Exception as e:
            f.log(f"⚠️ Architecture tree logging skipped: {e}")

        # ---- ARCHITECTURE GUARD PHASE ----
        try:
            self.architecture_guard.run(f, inventory)
        except Exception as e:
            f.log(f"⚠️ Architecture guard skipped: {e}")

        # ---- CRITIC REVIEW PHASE ----
        try:
            critic_report = self.critic_agent.run(f)

            if critic_report:
                issues = critic_report.get("issues") if isinstance(critic_report, dict) else None
                if issues:
                    f.log(f"🧠 Critic review completed ({len(issues)} issues detected)")
                else:
                    f.log("🧠 Critic review completed")

                # attempt automatic repair
                repair_result = self.repair_agent.run(f, critic_report)

                if repair_result:
                    f.log("🔧 Repair agent applied improvements")

        except Exception as e:
            f.log(f"⚠️ Critic/repair phase skipped: {e}")

        # ---- CODE DEPENDENCY ANALYSIS (post-generation) ----
        try:
            nodes, edges = self.import_dependency_analyzer.build_graph(f, inventory)
            f.log(f"🔎 Import dependency scan completed ({len(edges)} relations detected)")
        except Exception as e:
            f.log(f"⚠️ Import dependency scan skipped: {e}")

        # ---- TEST GENERATION PHASE ----
        try:
            self.test_generator_agent.run(f, inventory)
        except Exception as e:
            f.log(f"⚠️ Test generation skipped: {e}")

        # ---- TEST PHASE ----
        try:
            tests_ok, test_output = self.test_agent.run(f)

            if not tests_ok:
                f.log("⚠️ Test failures detected (continuing to compile loop)")
        except Exception as e:
            f.log(f"⚠️ Test phase skipped: {e}")

        # ---- COMPILE AND FIX LOOP ----
        MAX_FIX_ATTEMPTS = 5
        for attempt in range(MAX_FIX_ATTEMPTS):

            success, compile_output = self.compile_agent.run(f)

            if success:
                break

            f.log(f"🧠 Compile fix attempt {attempt+1}/{MAX_FIX_ATTEMPTS}")

            fixed = self.compile_fix_agent.run(f, compile_output)

            if not fixed:
                break

        if success:
            f.log("✨ PROJECT GENERATED AND VERIFIED")

            # ---- AUTONOMOUS REFACTOR PHASE ----
            try:
                self.refactor_agent.run(f)
                f.log("🧠 Refactor agent completed")
            except Exception as e:
                f.log(f"⚠️ Refactor phase skipped: {e}")

            # ---- RUNTIME FEEDBACK PHASE ----
            try:
                runtime_report = self.runtime_feedback_agent.run(f)

                evolve = self.evolution_agent.run(f, runtime_report)

                if evolve:
                    f.log("🔁 Evolution cycle triggered")

                f.log("📊 Runtime feedback analysis completed")

            except Exception as e:
                f.log(f"⚠️ Runtime feedback skipped: {e}")

        else:
            f.log("⚠️ Project generated but compilation still failing")

        f.log("🏁 Orchestrator finished")


# ------------------ Pipeline State ------------------
class PipelineState:
    def __init__(self, idea: str, project_name: str):
        self.idea = idea
        self.project_name = project_name
        self.project_slug = re.sub(r"[^a-zA-Z0-9]", "", project_name.lower())

        # ---- CORE DOMAIN ARTIFACTS ----
        self.domain_model = {}
        self.aggregates = []
        self.bounded_contexts = {}
        self.modules = {}

        # ---- ARCHITECTURE ----
        self.architecture = {}
        self.inventory = []

        # ---- DOMAIN GRAPHS ----
        self.domain_graph = {}
        self.semantic_code_graph = {}
        self.task_graph = []

        # ---- PLANNING GRAPHS ----
        self.spec_graph = {}
        self.deterministic_spec = {}
        self.code_plan = {}

        # ---- BUSINESS MODEL ----
        self.capabilities = []
        self.usecases = []

        # ---- ADVANCED DOMAIN (future engines) ----
        self.domain_events = []
        self.sagas = []
        self.processes = []

        # ---- INCREMENTAL BUILD ----
        self.signatures = {}


# ------------------ Software Factory ------------------
class SoftwareFactory:



    def __init__(self, idea: str):
        load_dotenv()
        self.idea = idea
        self.executor = TaskExecutor()

        with open("config/architecture.yaml", "r", encoding="utf-8") as f:
            self.arch_config = yaml.safe_load(f)

        self.project_name = self.arch_config["project"]["name"]
        self.project_slug = re.sub(r"[^a-zA-Z0-9]", "", self.project_name.lower())

        # ✅ ROOT OF GENERATED OUTPUT (used by save_to_disk for build artifacts)
        self.output_root = Path("outputs") / self.project_slug
        self.output_root.mkdir(parents=True, exist_ok=True)

        self.base_package = f"com.{self.project_slug}"
        self.base_package_path = self.base_package.replace(".", "/")

        # Keep existing naming for logs/specs
        self.out_dir = self.output_root

        self.spec_file = Path("specs") / f"{self.project_slug}.json"
        Path("specs").mkdir(exist_ok=True)

        self.state = PipelineState(self.idea, self.project_name)

        contracts_path = Path("config/layer_contracts.yaml")
        self.contracts = LayerContracts.load(contracts_path) if contracts_path.exists() else None
        # --- Domain learning memory ---
        try:
            self.domain_memory = DomainMemory()
        except Exception:
            self.domain_memory = None

        # local generators and validators (must always exist)
        self.ast_generator = ASTJavaGenerator()
        self.field_validator = FieldValidator()
        self.template_generator = TemplateJavaGenerator()
        self.structural_guard = StructuralCodeGuard()
        self.architecture_logger = ArchitectureLogger()

        # ---- PIPELINE TRACE LOGGER ----
        try:
            self.trace_logger = PipelineTraceLogger(self.output_root)
        except Exception:
            self.trace_logger = None

    # ------------------------------------------------
    def _compile_project(self):
        """
        Attempts to compile the generated Spring Boot project using Maven.
        Returns (success, output).
        """
        backend_path = self.output_root / "backend"

        if not backend_path.exists():
            self.log("⚠️ Backend directory not found, skipping compilation")
            return True, ""

        try:
            self.log("🔧 Running Maven compilation...")

            result = subprocess.run(
                ["mvn", "-q", "-DskipTests", "package"],
                cwd=backend_path,
                capture_output=True,
                text=True
            )

            output = result.stdout + "\n" + result.stderr

            if result.returncode == 0:
                self.log("✅ Maven compilation successful")
                return True, output
            else:
                self.log("❌ Maven compilation failed")
                self.log(output)
                return False, output

        except FileNotFoundError:
            self.log("⚠️ Maven not installed or not available in PATH")
            return True, ""

    # ------------------------------------------------
    def log(self, msg: str):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

    # ------------------------------------------------
    def _normalize_rel(self, relative_path: str) -> str:
        return relative_path.replace("\\", "/").lstrip("/")

    # ------------------------------------------------
    def resolve_output_path(self, relative_path: str) -> Path:
        """
        Resolves Java output path while supporting modular architecture.

        modules/<module>/domain/... → com.<project>.<module>.domain...
        """

        rp = self._normalize_rel(relative_path)

        parts = rp.split("/")

        # modules/<module>/...
        if parts and parts[0] == "modules" and len(parts) >= 3:
            module = parts[1]
            rest = parts[2:]

            return (
                self.out_dir
                / "backend/src/main/java"
                / self.base_package_path
                / module
                / Path(*rest)
            )

        # default (non modular)
        return (
            self.out_dir
            / "backend/src/main/java"
            / self.base_package_path
            / rp
        )

    # ------------------------------------------------
    def _expected_package_for(self, rel: str) -> str:
        rel = self._normalize_rel(rel)

        if not rel.endswith(".java"):
            raise ValueError(f"expected .java path, got: {rel}")

        parts = rel.split("/")[:-1]

        # modules/<module>/...
        if parts and parts[0] == "modules" and len(parts) >= 3:
            module = parts[1]
            rest = parts[2:]
            return self.base_package + "." + module + "." + ".".join(rest)

        if not parts:
            return self.base_package

        return self.base_package + "." + ".".join(parts)

    # ------------------------------------------------
    def _strip_package_line(self, java_code: str) -> str:
        # remove "package ...;" line (if present), keep everything else
        return re.sub(r"^\s*package\s+[a-zA-Z0-9_.]+\s*;\s*\n+", "", java_code, flags=re.MULTILINE)

    # ------------------------------------------------
    def resolve_generation_mode(self, item):

        desc = (item.get("description") or "").strip().upper()

        if desc in {"ENUM", "GLOBAL_ENUM", "SHARED_ENUM"}:
            return (
                "MODE_DOMAIN_ENUM",
                "domain/shared/ExampleEnum.java",
                (
                    "GENERATION MODE: MODE_DOMAIN_ENUM\n"
                    "STRICT RULES (NON-NEGOTIABLE):\n"
                    "- Plain Java enum\n"
                    "- NO annotations\n"
                    "- NO frameworks\n"
                    "- NO Lombok\n"
                    "- Enum values in UPPER_SNAKE_CASE\n"
                    "- Follow the golden sample EXACTLY\n"
                )
            )

        if desc == "ENTITY":
            return (
                "MODE_DOMAIN_ENTITY",
                "domain/Example.java",
                ""
            )

        if desc == "ID RECORD":
            return (
                "MODE_ID",
                "domain/valueobject/ExampleId.java",
                (
                    "GENERATION MODE: MODE_ID\n"
                    "STRICT RULES (NON-NEGOTIABLE):\n"
                    "- Use final class (NOT record)\n"
                    "- Field name MUST be 'value'\n"
                    "- Field type MUST be UUID\n"
                    "- Implements ValueObject\n"
                    "- private final UUID value;\n"
                    "- Constructor must validate using Objects.requireNonNull(value)\n"
                    "- Provide method: public UUID value()\n"
                    "- Provide static factory method: newId() returning new <Id>(UUID.randomUUID())\n"
                    "- NO annotations\n"
                    "- NO frameworks\n"
                    "- NO Lombok\n"
                )
            )

        if desc == "VALUEOBJECT":
            return (
                "MODE_VALUE_OBJECT",
                "domain/valueobject/ExampleValueObject.java",
                (
                    "GENERATION MODE: MODE_VALUE_OBJECT\n"
                    "STRICT RULES (NON-NEGOTIABLE):\n"
                    "- Use final class\n"
                    "- private final field(s)\n"
                    "- Validate invariants in constructor\n"
                    "- Throw IllegalArgumentException when invalid\n"
                    "- Use Objects.requireNonNull\n"
                    "- Implement ValueObject\n"
                    "- Provide getter method(s)\n"
                    "- NO Lombok\n"
                    "- NO frameworks\n"
                )
            )

        if desc == "REPOSITORY INTERFACE":
            return ("MODE_DOMAIN_REPOSITORY_PORT", "domain/ExampleRepository.java", "")

        if desc == "SERVICE":
            return ("MODE_APPLICATION_SERVICE", "application/ExampleService.java", "")

        if desc == "USECASE":
            return ("MODE_APPLICATION_USECASE", "application/ExampleUseCase.java", "")

        if desc == "DOMAIN SERVICE":
            return ("MODE_DOMAIN_SERVICE", "domain/ExampleDomainService.java", "")

        if desc == "MAPPER":
            return ("MODE_MAPPER", "application/ExampleMapper.java", "")

        if desc == "DTO_REQUEST":
            return ("MODE_DTO_REQUEST", "application/ExampleRequest.java", "")

        if desc == "DTO_RESPONSE":
            return ("MODE_DTO_RESPONSE", "application/ExampleResponse.java", "")

        if desc == "JPA_ENTITY":
            return ("MODE_JPA_ENTITY", "infrastructure/ExampleJpaEntity.java", "")

        if desc == "SPRING_DATA_REPOSITORY":
            return ("MODE_SPRING_DATA_REPOSITORY", "infrastructure/SpringDataExampleRepository.java", "")

        if desc == "JPA_ADAPTER":
            return ("MODE_JPA_ADAPTER", "infrastructure/JpaExampleRepositoryAdapter.java", "")

        if desc == "CONTROLLER":
            return ("MODE_REST_CONTROLLER", "infrastructure/ExampleController.java", "")

        return ("MODE_UNKNOWN", None, "")

    # ------------------------------------------------
    def clean_llm_output(self, text: str) -> str:
        if not text:
            return ""
        text = text.strip()
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
        return text.strip()

    # ------------------------------------------------
    def _remove_unused_objects_import(self, content: str) -> str:
        # Remove "import java.util.Objects;" if class doesn't use Objects.requireNonNull
        if "Objects.requireNonNull" not in content:
            content = re.sub(r"\nimport java\.util\.Objects;\n", "\n", content)
        return content

    def _enforce_no_lombok_or_hibernate(self, rel: str, content: str):
        # Lombok must NEVER appear
        if re.search(r"\blombok\.", content) or re.search(r"@\s*(Getter|Setter|Builder|Data|Value)\b", content):
            raise RuntimeError(f"Lombok forbidden (found in {rel})")

        # Hibernate-specific annotations forbidden
        if "org.hibernate." in content or re.search(r"@\s*(CreationTimestamp|UpdateTimestamp)\b", content):
            raise RuntimeError(f"Hibernate-specific annotations forbidden (found in {rel})")

    def _enforce_springdata_uses_jpa_entity(self, rel: str, content: str):
        reln = self._normalize_rel(rel)
        if "/infrastructure/persistence/spring/" not in reln:
            return

        # Must not import domain.model.*
        if ".domain.model." in content:
            raise RuntimeError(f"SpringData repo must not reference domain model (found in {rel})")

        # Must extend JpaRepository<SomethingJpaEntity, UUID>
        m = re.search(r"extends\s+JpaRepository\s*<\s*([A-Za-z0-9_]+)\s*,\s*([A-Za-z0-9_\.]+)\s*>", content)
        if not m:
            raise RuntimeError(f"SpringData repo must extend JpaRepository<...> (found in {rel})")

        entity_type = m.group(1)
        id_type = m.group(2)
        if not entity_type.endswith("JpaEntity"):
            raise RuntimeError(f"SpringData repo generic must be *JpaEntity (found {entity_type} in {rel})")
        if not (id_type == "UUID" or id_type.endswith(".UUID")):
            raise RuntimeError(f"SpringData repo ID generic must be UUID (found {id_type} in {rel})")

    def _enforce_expected_package(self, rel: str, content: str):
        reln = self._normalize_rel(rel)
        if not reln.endswith(".java"):
            return
        expected = self._expected_package_for(reln)
        # Must have exact package line
        if not re.search(rf"^\s*package\s+{re.escape(expected)}\s*;\s*$", content, flags=re.MULTILINE):
            raise RuntimeError(
                f"Invalid package declaration in {rel}. Expected: package {expected};"
            )

        # Must not contain com.example anywhere (fail-fast)
        if "package com.example" in content or "import com.example" in content:
            raise RuntimeError(f"Forbidden com.example detected in {rel}")

    # ------------------------------------------------
    def save_to_disk(self, relative_path: str, content: str, is_protected: bool = False):
        rel = self._normalize_rel(relative_path)

        # Build/root artifacts
        if rel.startswith("backend/") and not rel.endswith(".java"):
            full_path = self.output_root / rel
        else:
            full_path = self.resolve_output_path(rel)

        # Domain kernel is write-once
        if rel.startswith("domain/") and full_path.exists() and not is_protected:
            raise RuntimeError(f"Refusing to overwrite domain file (write-once): {rel}")

        # Java validation
        if full_path.suffix == ".java" and not is_protected:
            content = self.clean_llm_output(content)

            # Guard against POM/XML hallucinations
            if any(tag in content for tag in ("<project>", "<dependencies>", "<build>")):
                raise RuntimeError(f"Invalid Java output for {rel}: looks like XML/POM")

            # Hard rules
            self._enforce_no_lombok_or_hibernate(rel, content)
            self._enforce_springdata_uses_jpa_entity(rel, content)

            # Hygiene
            content = self._remove_unused_objects_import(content)

            # Contract validation (if configured)
            if self.contracts:
                self.contracts.validate_or_raise(rel, content)

            # Enforce correct package (engine-driven, no post-fix)
            self._enforce_expected_package(rel, content)

            # Enforce IDs are final classes (never records)
            if rel.startswith("domain/valueobject/") and rel.endswith("Id.java"):
                if re.search(r"\brecord\s+", content):
                    raise RuntimeError(f"ID value objects must be final classes, not records (found record in {rel})")

        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content.strip() + "\n", encoding="utf-8")

    # ------------------------------------------------
    def generate_inventory(self, model):

        inventory = []

        # unwrap if needed
        dm = model.get("domain_model", model)

        modules = dm.get("modules") or {}

        # fallback when modules not defined
        if not modules:
            modules = {
                "core": {
                    "entities": [e.get("name") for e in dm.get("entities", [])]
                }
            }

        # map entity -> module (first module wins)
        entity_module = {}

        for module_name, module_data in modules.items():
            for entity in module_data.get("entities", []):
                if entity in entity_module:
                    continue  # prevent duplicates across modules
                entity_module[entity] = module_name

        seen_entities = set()

        entity_map = {e.get("name"): e for e in dm.get("entities", [])}

        # ---------------- ENUMS ----------------
        for enum in dm.get("global_enums", []):
            inventory.append({
                "path": f"domain/shared/{enum['name']}.java",
                "entity": enum["name"],
                "description": "ENUM",
                "values": enum.get("values", []),
            })

        # ---------------- VALUE OBJECTS ----------------
        # Place VOs inside the module when they are used by exactly one module.
        # Keep them global only when shared across multiple modules.
        from collections import defaultdict
        vo_usage_modules = defaultdict(set)

        for ent_name, ent in entity_map.items():
            module_name = entity_module.get(ent_name)
            if not module_name:
                continue

            for field in ent.get("fields", []):
                typ = field.get("type", "")
                if not typ:
                    continue

                # extract inner type for generics like List<Allergy>
                inner_types = []
                if "<" in typ and ">" in typ:
                    inner = typ.split("<", 1)[1].rsplit(">", 1)[0]
                    inner_types = [t.strip() for t in inner.split(",") if t.strip()]
                    outer = typ.split("<", 1)[0].strip()
                    candidate_types = [outer] + inner_types
                else:
                    candidate_types = [typ.strip()]

                for candidate in candidate_types:
                    if candidate in {vo.get("name") for vo in dm.get("value_objects", [])}:
                        vo_usage_modules[candidate].add(module_name)

        for vo in dm.get("value_objects", []):
            vo_name = vo["name"]
            used_in = vo_usage_modules.get(vo_name, set())

            if len(used_in) == 1:
                owner_module = next(iter(used_in))
                vo_path = f"modules/{owner_module}/domain/valueobject/{vo_name}.java"
                vo_module = owner_module
            else:
                vo_path = f"domain/valueobject/{vo_name}.java"
                vo_module = None

            inventory.append({
                "path": vo_path,
                "entity": vo_name,
                "description": "VALUEOBJECT",
                "fields": vo.get("fields", []),
                "module": vo_module,
            })

        layers = [
            ("domain/valueobject", "{name}Id.java", "ID RECORD"),
            ("domain/model", "{name}.java", "ENTITY"),
            ("domain/repository", "{name}Repository.java", "REPOSITORY INTERFACE"),
            ("domain/service", "{name}DomainService.java", "DOMAIN SERVICE"),

            ("application/usecase", "{name}UseCase.java", "USECASE"),
            ("application/dto", "{name}Request.java", "DTO_REQUEST"),
            ("application/dto", "{name}Response.java", "DTO_RESPONSE"),
            ("application/mapper", "{name}Mapper.java", "MAPPER"),

            ("infrastructure/persistence/entity", "{name}JpaEntity.java", "JPA_ENTITY"),
            ("infrastructure/persistence/spring", "SpringData{name}Repository.java", "SPRING_DATA_REPOSITORY"),
            ("infrastructure/persistence/adapter", "Jpa{name}RepositoryAdapter.java", "JPA_ADAPTER"),

            ("infrastructure/rest", "{name}Controller.java", "CONTROLLER"),
        ]

        seen = set()

        for entity_name, module_name in entity_module.items():

            if entity_name in seen_entities:
                continue

            seen_entities.add(entity_name)

            ent = entity_map.get(entity_name)
            if not ent:
                continue

            for folder, tpl, desc in layers:

                rel_path = f"modules/{module_name}/{folder}/{tpl.format(name=entity_name)}"

                if rel_path in seen:
                    continue

                seen.add(rel_path)

                item_fields = ent.get("fields", [])

                if desc == "ID RECORD":
                    item_fields = [{"name": "value", "type": "UUID"}]

                inventory.append({
                    "path": rel_path,
                    "entity": entity_name,
                    "description": desc,
                    "module": module_name,
                    "fields": item_fields,
                })

        # deterministic ordering
        def _order_key(item):
            path = item.get("path", "")

            if "domain/valueobject/" in path and not path.endswith("Id.java"):
                return 1

            if path.endswith("Id.java"):
                return 2

            if "/domain/model/" in path:
                return 3

            if "/domain/repository/" in path:
                return 4

            if "/domain/service/" in path:
                return 5

            if "/application/usecase/" in path:
                return 6

            if "/infrastructure/persistence/" in path:
                return 7

            if "/infrastructure/rest/" in path:
                return 8

            return 50

        # ---- DUPLICATE PATH GUARD ----
        paths = [i.get("path") for i in inventory]
        dup = [p for p in set(paths) if paths.count(p) > 1]
        if dup:
            raise RuntimeError(f"Duplicate inventory paths detected: {dup}")

        inventory = sorted(inventory, key=_order_key)

        return inventory

    # ------------------------------------------------
    def _bootstrap_pom(self):
        pom_xml = (
            '<project xmlns="http://maven.apache.org/POM/4.0.0"\n'
            '         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"\n'
            '         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0\n'
            '                             http://maven.apache.org/xsd/maven-4.0.0.xsd">\n\n'
            "  <modelVersion>4.0.0</modelVersion>\n\n"
            f"  <groupId>{self.base_package}</groupId>\n"
            f"  <artifactId>{self.project_slug}</artifactId>\n"
            "  <version>0.0.1-SNAPSHOT</version>\n\n"
            "  <properties>\n"
            "    <java.version>17</java.version>\n"
            "    <spring.boot.version>3.2.4</spring.boot.version>\n"
            "    <mapstruct.version>1.5.5.Final</mapstruct.version>\n"
            "  </properties>\n\n"
            "  <dependencyManagement>\n"
            "    <dependencies>\n"
            "      <dependency>\n"
            "        <groupId>org.springframework.boot</groupId>\n"
            "        <artifactId>spring-boot-dependencies</artifactId>\n"
            "        <version>${spring.boot.version}</version>\n"
            "        <type>pom</type>\n"
            "        <scope>import</scope>\n"
            "      </dependency>\n"
            "    </dependencies>\n"
            "  </dependencyManagement>\n\n"
            "  <dependencies>\n"
            "    <dependency>\n"
            "      <groupId>org.springframework.boot</groupId>\n"
            "      <artifactId>spring-boot-starter-web</artifactId>\n"
            "    </dependency>\n"
            "    <dependency>\n"
            "      <groupId>org.springframework.boot</groupId>\n"
            "      <artifactId>spring-boot-starter-data-jpa</artifactId>\n"
            "    </dependency>\n"
            "    <dependency>\n"
            "      <groupId>org.springframework.boot</groupId>\n"
            "      <artifactId>spring-boot-starter-validation</artifactId>\n"
            "    </dependency>\n"
            "    <dependency>\n"
            "      <groupId>org.mapstruct</groupId>\n"
            "      <artifactId>mapstruct</artifactId>\n"
            "      <version>${mapstruct.version}</version>\n"
            "    </dependency>\n"
            "  </dependencies>\n\n"
            "  <build>\n"
            "    <plugins>\n"
            "      <plugin>\n"
            "        <groupId>org.apache.maven.plugins</groupId>\n"
            "        <artifactId>maven-compiler-plugin</artifactId>\n"
            "        <version>3.11.0</version>\n"
            "        <configuration>\n"
            "          <release>17</release>\n"
            "        </configuration>\n"
            "      </plugin>\n"
            "\n"
            "      <plugin>\n"
            "        <groupId>org.springframework.boot</groupId>\n"
            "        <artifactId>spring-boot-maven-plugin</artifactId>\n"
            "      </plugin>\n"
            "    </plugins>\n"
            "  </build>\n\n"
            "</project>\n"
        )
        self.save_to_disk("backend/pom.xml", pom_xml, is_protected=True)

    def _bootstrap_domain_kernel(self):
        value_object_code = (
            f"package {self.base_package}.domain.shared;\n\n"
            "import java.io.Serializable;\n\n"
            "public interface ValueObject extends Serializable {\n"
            "}\n"
        )
        self.save_to_disk("domain/shared/ValueObject.java", value_object_code, is_protected=True)

        entity_code = (
            f"package {self.base_package}.domain.shared;\n\n"
            "import java.util.Objects;\n\n"
            "public abstract class Entity<ID extends ValueObject> {\n\n"
            "    protected final ID id;\n\n"
            "    protected Entity(ID id) {\n"
            "        this.id = Objects.requireNonNull(id);\n"
            "    }\n\n"
            "    public ID id() {\n"
            "        return id;\n"
            "    }\n"
            "}\n"
        )
        self.save_to_disk("domain/shared/Entity.java", entity_code, is_protected=True)

    # ------------------------------------------------


    # ------------------------------------------------

    # Domain enrichment hook
    def enrich_domain(self, domain_model: dict) -> dict:
        """
        Hook for future domain enrichment.
        Example uses:
        - domain graph improvements
        - pattern detection
        - aggregate inference
        """
        return domain_model


    # ------------------------------------------------
    # Domain learning memory
    def learn_domain(self, domain_model: dict):

        if not getattr(self, "domain_memory", None):
            return

        try:
            dm = domain_model.get("domain_model", domain_model)

            signals = {
                "entities": [e.get("name") for e in dm.get("entities", [])],
                "value_objects": [v.get("name") for v in dm.get("value_objects", [])],
                "aggregates": [a.get("aggregate") for a in dm.get("aggregates", [])],
            }

            # store learned domain pattern
            self.domain_memory.record(signals)

        except Exception as e:
            self.log(f"⚠️ Domain learning skipped: {e}")



    def _generate_single_file(self, item, index, total):
        rel_path = item["path"]
        file_name = Path(rel_path).name

        output_path = self.resolve_output_path(rel_path)

        # --- Context enrichment for LLM ---
        domain_graph = getattr(self.state, "domain_graph", {})
        semantic_graph = getattr(self.state, "semantic_code_graph", {})
        task_graph = getattr(self.state, "task_graph", [])

        # find task dependencies for this file
        deps = []
        for t in task_graph:
            if isinstance(t, dict) and t.get("path") == rel_path:
                deps = t.get("depends_on", []) or []
                break

        # --- Use deterministic module/layer detection from inventory metadata ---
        module = item.get("module")
        # --- safety fallback: derive module from path if inventory did not set it ---
        if not module:
            parts = rel_path.split("/")
            if parts and parts[0] == "modules" and len(parts) >= 2:
                module = parts[1]

        parts = rel_path.split("/")

        # fallback layer detection only
        if parts and parts[0] == "modules" and len(parts) >= 3:
            layer = parts[2]
        else:
            layer = parts[0] if parts else None

        context_payload = json.dumps({
            "name": item["entity"],
            "kind": item["description"],
            "fields": item.get("fields", []),
            "values": item.get("values", []),
            "path": rel_path,
            "layer": layer,
            "module": module,
            "module_package": f"{self.base_package}.{module}" if module else self.base_package,
            "base_package": self.base_package,
            "expected_package": self._expected_package_for(rel_path),
            "domain_relations": domain_graph.get(item["entity"], []),
            "semantic_relations": semantic_graph.get(item["entity"], []),
            "spec_fields": getattr(self.state, "spec_graph", {}).get(item["entity"], {}).get("fields", []),
            "deterministic_spec": getattr(self.state, "deterministic_spec", {}).get(item["entity"], {}),
            "code_plan": getattr(self.state, "code_plan", {}).get(item["entity"], {}),
            "task_dependencies": deps,
        }, sort_keys=True)

        # --- incremental generation signature ---
        model = getattr(self.executor, "model_name", "unknown")
        signature_raw = rel_path + context_payload + model
        
        signature = hashlib.sha256(signature_raw.encode()).hexdigest()

        prev_sig = self.state.signatures.get(rel_path)
        if prev_sig and prev_sig == signature and output_path.exists():
            self.log(f"⏭️ Incremental skip (no changes) {file_name}")
            return

        self.log(f"[{index}/{total}] Fabricating {file_name}")

        _, golden_rel, strict = self.resolve_generation_mode(item)

        # ---- AST DETERMINISTIC GENERATION (ANTI-HALLUCINATION) ----
        try:
            mode = item.get("description")

            if mode == "ENTITY":
                # Use fields from inventory (source of truth) instead of deterministic_spec
                fields = item.get("fields", [])

                pkg = self._expected_package_for(rel_path)

                # ensure entities are generated inside the module package
                if module:
                    pkg = f"{self.base_package}.{module}.domain.model"

                class_name = Path(rel_path).stem

                code = self.ast_generator.generate_class(
                    pkg,
                    class_name,
                    fields,
                    base_package=self.base_package,
                    module=module
                )

                self.log(f"🧩 AST generator used for {class_name}")

                self.save_to_disk(rel_path, code)
                self.state.signatures[rel_path] = signature
                return
        except Exception:
            pass

        # ---- TEMPLATE GENERATION (HYBRID MODE) ----
        try:

            mode = item.get("description")
            pkg = self._expected_package_for(rel_path)
            class_name = Path(rel_path).stem
            entity = item.get("entity")

            if mode == "JPA_ENTITY":

                code = self.template_generator.generate_jpa_entity(
                    pkg,
                    class_name,
                    item.get("fields", [])
                )

                try:
                    code = resolve_imports(
                        code,
                        item.get("fields", []),
                        self.base_package,
                        module
                    )
                except Exception as e:
                    try:
                        self.log(f"⚠️ resolve_imports failed for {file_name}: {e}")
                    except Exception:
                        pass

                self.log(f"🧱 Template generator used for {class_name}")

                self.save_to_disk(rel_path, code)
                self.state.signatures[rel_path] = signature
                return

            if mode in {"SERVICE", "USECASE", "DOMAIN SERVICE"}:

                code = self.template_generator.generate_service(
                    pkg,
                    class_name,
                    entity,
                    self.base_package,
                    module=module
                )

                try:
                    code = resolve_imports(
                        code,
                        item.get("fields", []),
                        self.base_package,
                        module
                    )
                except Exception:
                    pass

                self.log(f"🧱 Template generator used for {class_name}")

                self.save_to_disk(rel_path, code)
                self.state.signatures[rel_path] = signature
                return

            if mode == "REPOSITORY INTERFACE":

                code = self.template_generator.generate_repository(
                    pkg,
                    entity,
                    base_package=self.base_package,
                    module=module
                )

                try:
                    code = resolve_imports(
                        code,
                        item.get("fields", []),
                        self.base_package,
                        module
                    )
                except Exception:
                    pass

                self.log(f"🧱 Template generator used for {class_name}")

                self.save_to_disk(rel_path, code)
                self.state.signatures[rel_path] = signature
                return

            if mode == "SPRING_DATA_REPOSITORY":

                code = self.template_generator.generate_spring_data_repository(
                    pkg,
                    entity,
                    base_package=self.base_package,
                    module=module
                )

                try:
                    code = resolve_imports(
                        code,
                        item.get("fields", []),
                        self.base_package,
                        module
                    )
                except Exception:
                    pass

                self.log(f"🧱 Template generator used for {class_name}")

                self.save_to_disk(rel_path, code)
                self.state.signatures[rel_path] = signature
                return

            if mode == "CONTROLLER":

                code = self.template_generator.generate_controller(
                    pkg,
                    class_name,
                    entity,
                    self.base_package,
                    module=module
                )

                try:
                    code = resolve_imports(
                        code,
                        item.get("fields", []),
                        self.base_package,
                        module
                    )
                except Exception:
                    pass

                self.log(f"🧱 Template generator used for {class_name}")

                self.save_to_disk(rel_path, code)
                self.state.signatures[rel_path] = signature
                return

            # --- Begin inserted DTO and Mapper generation logic ---
            if mode in {"DTO_REQUEST", "DTO_RESPONSE"}:

                code = self.ast_generator.generate_class(
                    pkg,
                    class_name,
                    item.get("fields", []),
                    base_package=self.base_package,
                    module=module
                )

                try:
                    code = resolve_imports(
                        code,
                        item.get("fields", []),
                        self.base_package,
                        module
                    )
                except Exception:
                    pass

                self.log(f"🧩 AST DTO generator used for {class_name}")

                self.save_to_disk(rel_path, code)
                self.state.signatures[rel_path] = signature
                return

            if mode == "MAPPER":

                code = self.template_generator.generate_mapper(
                    pkg,
                    class_name,
                    entity,
                    self.base_package,
                    module=module
                )

                try:
                    code = resolve_imports(
                        code,
                        item.get("fields", []),
                        self.base_package,
                        module
                    )
                except Exception:
                    pass

                self.log(f"🧱 Template generator used for {class_name}")

                self.save_to_disk(rel_path, code)
                self.state.signatures[rel_path] = signature
                return
            # --- End inserted DTO and Mapper generation logic ---

        except Exception:
            pass

        expected_pkg = self._expected_package_for(rel_path)

        mandatory_header = (
            "MANDATORY (NON-NEGOTIABLE):\n"
            f"- The FIRST non-comment line MUST be exactly: package {expected_pkg};\n"
            "- DO NOT use com.example anywhere.\n"
            "- DO NOT change the package even if golden sample shows something else.\n\n"
        )

        golden = ""
        if golden_rel:
            p = Path("config/golden_samples") / golden_rel
            if p.exists():
                golden_body = self._strip_package_line(p.read_text(encoding="utf-8"))
                golden = (
                    "\n=== GOLDEN SAMPLE (FOLLOW EXACTLY, CHANGE NAMES ONLY) ===\n"
                    + golden_body
                    + "\n=== END GOLDEN SAMPLE ===\n"
                )

        prompt = mandatory_header + strict + "\n" + golden

        # --- LLM cache directory ---
        cache_dir = Path(".llm_cache")
        cache_dir.mkdir(exist_ok=True)

        # --- deterministic cache key (include model/provider) ---
        model = getattr(self.executor, "model_name", "unknown")
        cache_key_raw = rel_path + prompt + context_payload + model
        cache_key = hashlib.sha256(cache_key_raw.encode()).hexdigest()
        cache_file = cache_dir / f"{cache_key}.java"

        if cache_file.exists():
            self.log(f"⚡ Cache hit for {file_name}")
            code = cache_file.read_text(encoding="utf-8")
        else:
            code = self.executor.run_task(
                "write_code",
                path=rel_path,
                desc=prompt,
                base_package=self.base_package,
                context_data=context_payload,
            )

            try:
                cache_file.write_text(code, encoding="utf-8")
            except Exception:
                pass

        from ai.validators.code_verifier import verify_java_code
        from ai.validators.code_auto_fix import auto_fix_java_code

        verification = verify_java_code(code)

        verification = verify_java_code(code)

        if not verification["valid"]:
            self.log(f"⚠️ Verification issues in {file_name}: {verification['issues']}")
            code = auto_fix_java_code(code, verification["issues"])

            # verify again
            verification = verify_java_code(code)
            if not verification["valid"]:
                self.log(f"❌ Verification still failing for {file_name}")

        # ---- FIELD VALIDATION AGAINST DETERMINISTIC SPEC ----
        try:
            mode = item.get("description")

            # validate only domain / dto classes
            if mode in {"ENTITY", "DTO_REQUEST", "DTO_RESPONSE"}:
                spec = getattr(self.state, "deterministic_spec", {}).get(item["entity"], {})
                ok, invalid_fields = self.field_validator.validate(code, spec)

                if not ok:
                    self.log(f"🚫 Invalid fields detected in {file_name}: {invalid_fields}")
        except Exception:
            pass

        # ---- STRUCTURAL GUARD (ANTI-HALLUCINATION) ----
        try:

            spec = getattr(self.state, "deterministic_spec", {}).get(item["entity"], {})

            issues = self.structural_guard.validate(
                code,
                spec,
                self.base_package
            )

            if issues:
                self.log(f"🚫 Structural issues detected in {file_name}: {issues}")

        except Exception:
            pass


        # ---- AUTO IMPORT RESOLUTION ----
        try:
            code = resolve_imports(
                code,
                item.get("fields", []),
                self.base_package,
                module
            )
        except Exception:
            pass

        self.save_to_disk(rel_path, code)
        # store new generation signature
        self.state.signatures[rel_path] = signature

    # ------------------------------------------------

# ------------------ Entrypoint ------------------
if __name__ == "__main__":

    factory = SoftwareFactory(" ".join(sys.argv[1:]))

    # ---- TERMINAL LOG CAPTURE ----
    try:
        log_file = factory.output_root / "execution.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        tee = Tee(log_file)
        sys.stdout = tee
        sys.stderr = tee

        factory.log(f"📝 Logging terminal output to {log_file}")
    except Exception as e:
        print(f"⚠️ Could not initialize Tee logger: {e}")

    orchestrator = FactoryOrchestrator(factory)

    # Attach orchestrator reference to factory after agents created
    factory.orchestrator = orchestrator

    try:
        orchestrator.run()
    finally:
        # restore stdout
        try:
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            tee.close()
        except Exception:
            pass