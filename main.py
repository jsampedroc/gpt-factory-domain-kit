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
from datetime import datetime
from dotenv import load_dotenv

from ai.pipeline.state_manager import StateManager
from ai.pipeline.task_executor import TaskExecutor
from ai.utils.logging_helper import Tee
from ai.validators.layer_contracts import LayerContracts
from ai.domain.semantic_type_detector import detect_semantic_types
from ai.graph.task_graph_builder import TaskGraphBuilder
import ast
from collections import defaultdict
from ai.knowledge.domain_memory import DomainMemory
from ai.knowledge.compile_memory import CompileMemory
from ai.graph.code_dependency_graph import CodeDependencyGraph
from ai.agents.refactor_agent import RefactorAgent
from ai.agents.runtime_feedback_agent import RuntimeFeedbackAgent  # TODO: implement this module
from ai.agents.evolution_agent import EvolutionAgent
from ai.domain.domain_model_validator import validate_domain_model
from ai.graph.dependency_graph_builder import DependencyGraphBuilder
from ai.codegen.import_resolver import resolve_imports



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
    def run(self, factory, domain_model):
        return detect_semantic_types(domain_model)



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



# ------------------ Import Dependency Analyzer ------------------

class ImportDependencyAnalyzer:
    """
    Reads generated Java files and detects dependencies based on `import` statements.
    This improves ordering for recompilation cycles (similar to Devin-style dependency graphs).
    """

    IMPORT_RE = re.compile(r"import\s+([a-zA-Z0-9_.]+);")

    def build_graph(self, factory, inventory):

        nodes = []
        edges = defaultdict(set)

        for item in inventory:
            nodes.append(item["path"])

        for item in inventory:
            path = item["path"]
            file_path = factory.resolve_output_path(path)

            if not file_path.exists():
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
            except Exception:
                continue

            imports = self.IMPORT_RE.findall(content)

            for imp in imports:
                # convert import package to potential path
                rel = imp.replace(factory.base_package + ".", "")
                rel = rel.replace(".", "/") + ".java"

                for target in nodes:
                    if target.endswith(rel):
                        edges[path].add(target)

        return nodes, edges



# ------------------ Domain Graph Builder ------------------



class DomainGraphBuilder:
    """
    Builds a simple relationship graph between entities based on field types.
    This helps later stages (DTOs, mappers, services) understand domain relations.
    """

    def build(self, domain_model: dict):

        dm = domain_model.get("domain_model", domain_model)

        entities = {e["name"] for e in dm.get("entities", [])}
        graph = defaultdict(set)

        for ent in dm.get("entities", []):
            src = ent.get("name")
            for f in ent.get("fields", []):
                t = f.get("type")

                if not t:
                    continue

                # normalize generic wrappers and nested generics (e.g., List<Student>, List<List<Student>>)
                t = re.sub(r".*<(.+?)>", r"\1", t)
                t = t.split(",")[-1].strip()
                t = re.sub(r".*<(.+?)>", r"\1", t)

                # if generics contain multiple types (e.g., Map<String, Student>) keep the last
                if "," in t:
                    t = t.split(",")[-1].strip()

                if t in entities and t != src:
                    graph[src].add(t)

        return {k: sorted(v) for k, v in graph.items()}
    

 # ------------------ Semantic CodeGraph Builder ------------------   

class SemanticCodeGraphBuilder:
    """
    Builds a richer semantic graph so the generator understands
    entity relationships and avoids hallucinated DTO/service fields.
    """

    def build(self, domain_model: dict):

        dm = domain_model.get("domain_model", domain_model)

        entities = {e.get("name") for e in dm.get("entities", [])}

        graph = {}

        for ent in dm.get("entities", []):
            name = ent.get("name")
            relations = []

            for f in ent.get("fields", []):

                t = f.get("type")
                if not t:
                    continue

                # unwrap generics
                if "<" in t and ">" in t:
                    t = t.split("<")[-1].replace(">", "")

                if t in entities and t != name:
                    relations.append({
                        "target": t,
                        "field": f.get("name")
                    })

            graph[name] = relations

        return graph


# ------------------ Spec Graph Builder ------------------



class SpecGraphBuilder:
    """
    Builds a structured specification graph from the domain model.
    This gives the LLM a deterministic structural spec for entities.
    """

    def build(self, domain_model: dict):
        dm = domain_model.get("domain_model", domain_model)

        graph = {}

        for ent in dm.get("entities", []):
            name = ent.get("name")
            fields = ent.get("fields", []) or []

            graph[name] = {
                "fields": fields,
                "relations": []
            }

        return graph

# ------------------ Deterministic Spec Generator ------------------
class DeterministicSpecGenerator:
    """
    Produces a deterministic structural specification for entities.
    This reduces LLM hallucinations by providing a strict contract
    for fields and relationships before code generation.
    """

    def build(self, domain_model: dict):
        dm = domain_model.get("domain_model", domain_model)

        spec = {}

        for ent in dm.get("entities", []):
            name = ent.get("name")
            fields = ent.get("fields", []) or []

            field_names = [f.get("name") for f in fields if f.get("name")]
            field_types = [f.get("type") for f in fields if f.get("type")]

            # deterministic structural hash for the entity
            try:
                entity_hash = hashlib.sha256(
                    json.dumps(fields, sort_keys=True).encode()
                ).hexdigest()
            except Exception:
                entity_hash = None

            spec[name] = {
                "entity": name,
                "signature": entity_hash,
                "fields": [
                    {
                        "name": f.get("name"),
                        "type": f.get("type"),
                        "required": f.get("required", False)
                    }
                    for f in fields
                ],
                "field_names": field_names,
                "field_types": field_types,
                "allowed_fields": field_names,
                "required_fields": ["id"] if "id" in field_names else []
            }

        return spec


# ------------------ Field Validator ------------------
class FieldValidator:
    """
    Validates that generated entity/DTO code does not introduce fields
    outside the deterministic specification.
    This reduces LLM hallucinations in generated classes.
    """

    FIELD_RE = re.compile(r"private\s+[A-Za-z0-9_<>,\s]+\s+([a-zA-Z0-9_]+)\s*;")

    def validate(self, code: str, deterministic_spec: dict):
        if not deterministic_spec:
            return True, []

        allowed = set(deterministic_spec.get("allowed_fields", []))
        if not allowed:
            return True, []

        found = set(self.FIELD_RE.findall(code))

        invalid = [f for f in found if f not in allowed]

        return len(invalid) == 0, invalid
    
# ------------------ Structural Code Guard ------------------
class StructuralCodeGuard:
    """
    Prevents hallucinated fields, invalid imports,
    and invalid repository/service relationships.
    """

    FIELD_RE = re.compile(r"private\s+[A-Za-z0-9_<>,\s]+\s+([a-zA-Z0-9_]+)\s*;")
    IMPORT_RE = re.compile(r"import\s+([a-zA-Z0-9_.]+);")

    def validate(self, code: str, spec: dict, base_package: str):

        issues = []

        allowed = set(spec.get("allowed_fields", []))

        fields = set(self.FIELD_RE.findall(code))

        invalid_fields = [f for f in fields if allowed and f not in allowed]

        if invalid_fields:
            issues.append({
                "type": "invalid_fields",
                "fields": invalid_fields
            })

        imports = self.IMPORT_RE.findall(code)

        for imp in imports:

            if imp.startswith(base_package):

                if ".domain.model." not in imp and \
                   ".domain.valueobject." not in imp and \
                   ".domain.shared." not in imp and \
                   ".domain.repository." not in imp and \
                   ".application." not in imp and \
                   ".infrastructure." not in imp:

                    issues.append({
                        "type": "invalid_import",
                        "import": imp
                    })

        return issues


# ------------------ AST Java Generator ------------------
class ASTJavaGenerator:

    def __init__(self, value_objects=None):
        self.resolver = JavaTypeResolver(value_objects=value_objects)

    def set_value_objects(self, value_objects):
        self.resolver = JavaTypeResolver(value_objects=value_objects)

    JAVA_STD_IMPORTS = {
        "LocalDate": "java.time.LocalDate",
        "List": "java.util.List",
        "Set": "java.util.Set",
        "UUID": "java.util.UUID",
    }

    def generate_class(self, package_name, class_name, fields, base_package=None):

        imports = set()

        for f in fields:

            t = f.get("type", "")

            if not t:
                continue

            # generics
            if "<" in t:

                outer = t.split("<")[0]
                inner = t.split("<")[1].replace(">", "")

                imp = self.resolver.resolve(outer, base_package)
                if imp and not imp.endswith(class_name):
                    imports.add(imp)

                for inner_type in inner.split(","):

                    inner_type = inner_type.strip()

                    imp = self.resolver.resolve(inner_type, base_package)

                    if imp and not imp.endswith(class_name):
                        imports.add(imp)

            else:

                imp = self.resolver.resolve(t, base_package)

                if imp and not imp.endswith(class_name):
                    imports.add(imp)

        lines = []

        lines.append(f"package {package_name};\n")

        if imports:
            lines.append("\n")
            for imp in sorted(imports):
                lines.append(f"import {imp};\n")

        lines.append("\n")

        lines.append(f"public class {class_name} {{\n")

        for f in fields:
            t = f.get("type", "Object")
            n = f.get("name", "field")
            lines.append(f"    private {t} {n};\n")

        lines.append("\n")

        for f in fields:
            t = f.get("type", "Object")
            n = f.get("name", "field")
            m = n[0].upper() + n[1:]
            lines.append(f"    public {t} get{m}() {{ return {n}; }}\n")

        lines.append("}\n")

        return "".join(lines)


# ------------------ Java Type Resolver ------------------
class JavaTypeResolver:

    """
    Resolves Java type imports deterministically to avoid LLM hallucinations.

    Rules:
    - java.lang types -> no import
    - known JDK types -> import from JDK
    - <Name>Id -> domain.valueobject
    - <Name>Status / <Name>Type -> domain.shared
    - discovered value objects -> domain.valueobject
    - everything else -> domain.model
    """

    JAVA_LANG = {
        "String", "Integer", "Long", "Boolean",
        "Double", "Float", "Short", "Byte",
        "Character"
    }

    JAVA_STD = {
        "LocalDate": "java.time.LocalDate",
        "LocalDateTime": "java.time.LocalDateTime",
        "UUID": "java.util.UUID",
        "List": "java.util.List",
        "Set": "java.util.Set",
        "Map": "java.util.Map",
        "Optional": "java.util.Optional",
    }

    def __init__(self, value_objects=None):
        # value object names discovered from the domain model (e.g., GeoLocation, Money, Address)
        self.value_objects = set(value_objects or [])

    def resolve(self, type_name, base_package):

        if not type_name:
            return None

        # strip whitespace
        type_name = type_name.strip()

        # java.lang
        if type_name in self.JAVA_LANG:
            return None

        # JDK standard imports
        if type_name in self.JAVA_STD:
            return self.JAVA_STD[type_name]

        # domain IDs
        if type_name.endswith("Id"):
            return f"{base_package}.domain.valueobject.{type_name}"

        # enums in shared
        if type_name.endswith("Status") or type_name.endswith("Type"):
            return f"{base_package}.domain.shared.{type_name}"

        # discovered value objects
        if type_name in self.value_objects:
            return f"{base_package}.domain.valueobject.{type_name}"

        # default: entity/model
        return f"{base_package}.domain.model.{type_name}"




# ------------------ Template Java Generator ------------------
class TemplateJavaGenerator:
    """
    Deterministic templates for common backend classes.
    Reduces hallucinations for services, repositories and controllers.
    """

    def generate_service(self, package_name: str, class_name: str, entity: str, base_package: str):
        return (
            f"package {package_name};\n\n"
            f"import {base_package}.domain.repository.{entity}Repository;\n\n"
            f"public class {class_name} {{\n\n"
            f"    private final {entity}Repository repository;\n\n"
            f"    public {class_name}({entity}Repository repository) {{\n"
            f"        this.repository = repository;\n"
            f"    }}\n\n"
            f"}}\n"
        )

    def generate_repository(self, package_name: str, entity: str):
        return (
            f"package {package_name};\n\n"
            f"public interface {entity}Repository {{\n\n"
            f"}}\n"
        )

    def generate_controller(self, pkg, class_name, entity, base_package):
        base = entity
        base_lower = base.lower()
        return f"""
            package {pkg};

            import {base_package}.application.service.{base}Service;
            import {base_package}.application.dto.{base}Request;
            import {base_package}.application.dto.{base}Response;

            import org.springframework.web.bind.annotation.*;

            import java.util.List;

            @RestController
            @RequestMapping("/api/{base_lower}s")
            public class {class_name} {{

                private final {base}Service service;

                public {class_name}({base}Service service) {{
                    this.service = service;
                }}

                @PostMapping
                public {base}Response create(@RequestBody {base}Request request) {{
                    return service.create(request);
                }}

                @GetMapping("/{{id}}")
                public {base}Response get(@PathVariable String id) {{
                    return service.get(id);
                }}

                @GetMapping
                public List<{base}Response> list() {{
                    return service.list();
                }}

                @DeleteMapping("/{{id}}")
                public void delete(@PathVariable String id) {{
                    service.delete(id);
                }}
            }}
        """
    
    
    
    def generate_jpa_entity(self, package_name, class_name, fields):

        lines = []

        lines.append(f"package {package_name};\n\n")
        lines.append("import jakarta.persistence.*;\n")
        lines.append("import java.util.UUID;\n\n")

        lines.append("@Entity\n")
        lines.append(f"public class {class_name} {{\n\n")

        lines.append("    @Id\n")
        lines.append("    private UUID id;\n\n")

        for f in fields:

            name = f.get("name")
            type_ = f.get("type")

            if name == "id":
                continue

            lines.append(f"    private {type_} {name};\n")

        lines.append("}\n")

        return "".join(lines)


# ------------------ Code Planner ------------------
class CodePlanner:
    """
    Builds a deterministic code plan for each entity before generation.
    This reduces LLM hallucinations by pre‑defining structure.
    """

    def build(self, domain_model: dict):
        dm = domain_model.get("domain_model", domain_model)

        plan = {}

        for ent in dm.get("entities", []):
            name = ent.get("name")
            fields = ent.get("fields", []) or []

            plan[name] = {
                "entity": name,
                "fields": fields,
                "has_id": any(f.get("name") == "id" for f in fields),
                "has_relations": any("Id" in (f.get("type") or "") for f in fields),
            }

        return plan


# ------------------ Impact Analyzer ------------------

class ImpactAnalyzer:
    """
    Computes which files are impacted when domain entities change.
    Uses the domain graph and file inventory.
    """

    def __init__(self, domain_graph):
        self.domain_graph = domain_graph or {}

    def compute_impacted_files(self, inventory, changed_entities):
        impacted = set()

        for item in inventory:
            entity = item.get("entity")

            if entity in changed_entities:
                impacted.add(item["path"])
                continue

            relations = self.domain_graph.get(entity, [])
            if any(rel in changed_entities for rel in relations):
                impacted.add(item["path"])

        return impacted

# ------------------ Pipeline Engine ------------------

class PipelineStep:
    def __init__(self, name, fn):
        self.name = name
        self.fn = fn

    def run(self, ctx):
        return self.fn(ctx)


class PipelineEngine:
    """
    Simple declarative pipeline executor so phases can be composed
    without hard‑coding everything inside the orchestrator.
    """

    def __init__(self, steps):
        self.steps = steps

    def run(self, ctx):
        results = {}
        for step in self.steps:
            ctx.log(f"▶ Pipeline step: {step.name}")
            start = time.time()
            try:
                results[step.name] = step.run(ctx)
                duration = time.time() - start
                ctx.log(f"✅ Step completed: {step.name} ({duration:.2f}s)")
            except Exception as e:
                duration = time.time() - start
                ctx.log(f"❌ Pipeline step failed: {step.name} after {duration:.2f}s → {e}")
                raise RuntimeError(f"Pipeline failed at step '{step.name}'") from e
        return results

# ------------------ Orchestrator ------------------

class FactoryOrchestrator:

    def __init__(self, factory):
        self.factory = factory
        self.project_planner = ProjectPlannerAgent()
        self.domain_agent = DomainAgent()
        self.semantic_agent = SemanticAgent()
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
        self.field_validator = FieldValidator()
        self.ast_generator = ASTJavaGenerator()
        self.code_planner = CodePlanner()
        self.refactor_agent = RefactorAgent()
        self.runtime_feedback_agent = RuntimeFeedbackAgent()  # TODO: implement this module
        self.evolution_agent = EvolutionAgent()
        self.domain_graph_builder = DomainGraphBuilder()
        self.spec_graph_builder = SpecGraphBuilder()
        self.semantic_code_graph_builder = SemanticCodeGraphBuilder()       
        # compile error learning memory
        try:
            self.compile_memory = CompileMemory()
        except Exception:
            self.compile_memory = None
        


    def run(self):

        f = self.factory

        # attach compile memory so agents can use it
        if getattr(self, "compile_memory", None):
            setattr(f, "compile_memory", self.compile_memory)

        f.log("🧠 Orchestrator starting")
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

                # ---- DOMAIN GRAPH BUILD ----
                try:
                    graph = self.domain_graph_builder.build(domain_model)
                    factory.state.domain_graph = graph
                    factory.log(f"🧩 Domain graph built ({len(graph)} relations)")
                except Exception as e:
                    factory.log(f"⚠️ Domain graph skipped: {e}")
                
                # ---- SEMANTIC CODE GRAPH BUILD ----
                try:
                    semantic_graph = self.semantic_code_graph_builder.build(domain_model)
                    factory.state.semantic_code_graph = semantic_graph
                    factory.log(f"🧠 Semantic code graph built ({len(semantic_graph)} entities)")
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
        self.domain_model = {}
        self.architecture = {}
        self.domain_graph = {}
        self.semantic_code_graph = {}
        self.task_graph = []

        # graphs and deterministic planning artifacts
        self.spec_graph = {}
        self.deterministic_spec = {}
        self.code_plan = {}

        # incremental generation signatures
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
        All Java code is placed under:
          outputs/<slug>/backend/src/main/java/<base_package_path>/<relative_path>
        Example:
          domain/model/Child.java -> .../com/preschoolmanagement/domain/model/Child.java
        """
        rp = self._normalize_rel(relative_path)
        return self.out_dir / "backend/src/main/java" / self.base_package_path / rp

    # ------------------------------------------------
    def _expected_package_for(self, rel: str) -> str:
        """
        Given rel path like 'domain/model/Child.java' -> 'com.<slug>.domain.model'
        """
        rel = self._normalize_rel(rel)
        if not rel.endswith(".java"):
            raise ValueError(f"expected .java path, got: {rel}")
        parts = rel.split("/")[:-1]  # folder segments
        if not parts:
            # edge-case: file at root under base package
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

        # el modelo puede venir como {domain_model:{...}}
        dm = model.get("domain_model", model)

        # ---------------- ENUMS ----------------
        for enum in dm.get("global_enums", []):
            inventory.append({
                "path": f"domain/shared/{enum['name']}.java",
                "entity": enum["name"],
                "description": "ENUM",
                "values": enum.get("values", []),
            })

        # ---------------- VALUE OBJECTS ----------------
        for vo in dm.get("value_objects", []):
            inventory.append({
                "path": f"domain/valueobject/{vo['name']}.java",
                "entity": vo["name"],
                "description": "VALUEOBJECT",
                "fields": vo.get("fields", []),
            })

        layers = [

            ("domain/model", "{name}.java", "ENTITY"),
            ("domain/valueobject", "{name}Id.java", "ID RECORD"),
            ("domain/repository", "{name}Repository.java", "REPOSITORY INTERFACE"),

            ("application/service", "{name}Service.java", "SERVICE"),
            ("application/dto", "{name}Request.java", "DTO_REQUEST"),
            ("application/dto", "{name}Response.java", "DTO_RESPONSE"),
            ("application/mapper", "{name}Mapper.java", "MAPPER"),

            ("infrastructure/persistence/entity", "{name}JpaEntity.java", "JPA_ENTITY"),
            ("infrastructure/persistence/spring", "SpringData{name}Repository.java", "SPRING_DATA_REPOSITORY"),
            ("infrastructure/persistence/adapter", "Jpa{name}RepositoryAdapter.java", "JPA_ADAPTER"),

            ("infrastructure/rest", "{name}Controller.java", "CONTROLLER"),
        ]

        for ent in dm.get("entities", []):

            for folder, tpl, desc in layers:

                inventory.append({
                    "path": f"{folder}/{tpl.format(name=ent['name'])}",
                    "entity": ent["name"],
                    "description": desc,
                    "fields": ent.get("fields", []),
                })

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

        parts = rel_path.split("/")
        layer = parts[0] if len(parts) > 0 else None
        module = parts[1] if len(parts) > 1 else None

        context_payload = json.dumps({
            "name": item["entity"],
            "kind": item["description"],
            "fields": item.get("fields", []),
            "values": item.get("values", []),
            "path": rel_path,
            "layer": layer,
            "module": module,
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
            spec = getattr(self.state, "deterministic_spec", {}).get(item["entity"], {})
            mode = item.get("description")

            if spec and mode == "ENTITY":
                fields = spec.get("fields", [])
                pkg = self._expected_package_for(rel_path)
                class_name = Path(rel_path).stem

                code = self.ast_generator.generate_class(
                    pkg,
                    class_name,
                    fields,
                    base_package=self.base_package
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
                    code = resolve_imports(code)
                except Exception:
                    pass

                self.log(f"🧱 Template generator used for {class_name}")

                self.save_to_disk(rel_path, code)
                self.state.signatures[rel_path] = signature
                return

            if mode == "SERVICE":

                code = self.template_generator.generate_service(
                    pkg,
                    class_name,
                    entity,
                    self.base_package
                )

                try:
                    code = resolve_imports(code)
                except Exception:
                    pass

                self.log(f"🧱 Template generator used for {class_name}")

                self.save_to_disk(rel_path, code)
                self.state.signatures[rel_path] = signature
                return

            if mode == "REPOSITORY INTERFACE":

                code = self.template_generator.generate_repository(pkg, entity)

                try:
                    code = resolve_imports(code)
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
                    self.base_package
                )

                try:
                    code = resolve_imports(code)
                except Exception:
                    pass

                self.log(f"🧱 Template generator used for {class_name}")

                self.save_to_disk(rel_path, code)
                self.state.signatures[rel_path] = signature
                return

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

        if not verification["valid"]:
            self.log(f"⚠️ Verification issues in {file_name}: {verification['issues']}")
            code = auto_fix_java_code(code, verification["issues"])
            self.log("🔧 Auto-fix applied")

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
            code = resolve_imports(code)
        except Exception:
            pass

        self.save_to_disk(rel_path, code)
        # store new generation signature
        self.state.signatures[rel_path] = signature

    # ------------------------------------------------

# ------------------ Entrypoint ------------------
if __name__ == "__main__":
    factory = SoftwareFactory(" ".join(sys.argv[1:]))
    orchestrator = FactoryOrchestrator(factory)
    # Attach orchestrator reference to factory after agents created
    factory.orchestrator = orchestrator
    orchestrator.run() 