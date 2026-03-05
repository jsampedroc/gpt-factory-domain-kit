# main.py — AI SOFTWARE FACTORY (STABLE, HARDENED, PROFESSIONAL)
import sys
import json
import yaml
import re
import subprocess
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
from ai.graph.code_dependency_graph import CodeDependencyGraph
from ai.agents.refactor_agent import RefactorAgent
from ai.agents.evolution_agent import EvolutionAgent

try:
    from ai.agents.runtime_feedback_agent import RuntimeFeedbackAgent
except Exception:
    RuntimeFeedbackAgent = None

from ai.agents.project_planner_agent import ProjectPlannerAgent
from ai.agents.domain_agent import DomainAgent
from ai.agents.semantic_agent import SemanticAgent
from ai.agents.architecture_reasoning_agent import ArchitectureReasoningAgent
from ai.agents.architecture_agent import ArchitectureAgent
from ai.agents.code_generation_agent import CodeGenerationAgent
from ai.agents.compile_agent import CompileAgent
from ai.agents.compile_fix_agent import CompileFixAgent
from ai.agents.import_dependency_analyzer import ImportDependencyAnalyzer

# Optional agents (present in the refactored agents package)
try:
    from ai.agents.agent_registry import AgentRegistry
except Exception:
    AgentRegistry = None

try:
    from ai.agents.semantic_compile_fix_agent import SemanticCompileFixAgent
except Exception:
    SemanticCompileFixAgent = None

try:
    from ai.agents.java_llm_repair_agent import JavaLLMRepairAgent
except Exception:
    JavaLLMRepairAgent = None

try:
    from ai.agents.inventory_consistency_agent import InventoryConsistencyAgent
except Exception:
    InventoryConsistencyAgent = None

try:
    from ai.agents.inventory_validator_agent import InventoryValidatorAgent
except Exception:
    InventoryValidatorAgent = None



# ------------------ Orchestrator ------------------

class FactoryOrchestrator:

    def __init__(self, factory):
        self.factory = factory

        # Prefer dynamic registry if available (Devin/Manus style)
        self.agents = None
        if AgentRegistry is not None:
            try:
                self.agents = AgentRegistry.discover()
            except Exception:
                self.agents = None

        def _get(name: str, ctor):
            """
            Unified agent resolver.

            Supports:
            - AgentRegistry returning instances
            - AgentRegistry returning classes
            - agents needing factory
            - agents needing project_root
            - agents with empty constructor
            """

            if isinstance(self.agents, dict) and name in self.agents:
                agent = self.agents[name]

                # If registry returned a CLASS, instantiate it
                if isinstance(agent, type):
                    try:
                        return agent(self.factory)
                    except TypeError:
                        pass

                    try:
                        return agent(self.factory.output_root)
                    except TypeError:
                        pass

                    return agent()

                # If registry returned an INSTANCE
                return agent

            # Try constructor(factory)
            try:
                return ctor(self.factory)
            except TypeError:
                pass

            # Try constructor(project_root)
            try:
                return ctor(self.factory.output_root)
            except TypeError:
                pass

            # Fallback
            return ctor()

        # Core pipeline agents
        self.project_planner = _get("project_planner", ProjectPlannerAgent)
        self.domain_agent = _get("domain", DomainAgent)
        self.semantic_agent = _get("semantic", SemanticAgent)
        self.architecture_reasoning_agent = _get("architecture_reasoning", ArchitectureReasoningAgent)
        self.architecture_agent = _get("architecture", ArchitectureAgent)
        self.codegen_agent = _get("code_generation", CodeGenerationAgent)
        self.compile_agent = _get("compile", CompileAgent)
        self.compile_fix_agent = _get("compile_fix", CompileFixAgent)

        # Optional repair/enrichment agents
        self.semantic_compile_fix_agent = _get("semantic_compile_fix", SemanticCompileFixAgent) if SemanticCompileFixAgent else None
        self.java_llm_repair_agent = _get("java_llm_repair", JavaLLMRepairAgent) if JavaLLMRepairAgent else None
        self.inventory_consistency_agent = _get("inventory_consistency", InventoryConsistencyAgent) if InventoryConsistencyAgent else None
        self.inventory_validator_agent = _get("inventory_validator", InventoryValidatorAgent) if InventoryValidatorAgent else None

        # Tooling / observability
        self.task_graph_builder = TaskGraphBuilder()
        self.import_dependency_analyzer = ImportDependencyAnalyzer()
        self.code_dependency_graph = CodeDependencyGraph()

        # Post-success autonomous improvement loop
        self.refactor_agent = RefactorAgent()
        self.runtime_feedback_agent = RuntimeFeedbackAgent() if RuntimeFeedbackAgent else None
        self.evolution_agent = EvolutionAgent()

    def run(self):

        f = self.factory

        f.log("🧠 Orchestrator starting")
        # ---- BOOTSTRAP (project skeleton) ----
        f._bootstrap_pom()
        f._bootstrap_domain_kernel()

        if StateManager.load_specs(f.spec_file, f.state):
            f.log("📦 Loaded cached domain model and architecture")
        else:

            # ---- PROJECT PLANNING PHASE ----
            plan = self.project_planner.run(f)
            if isinstance(plan, dict) and plan.get("idea"):
                f.idea = plan["idea"]

            domain_model = self.domain_agent.run(f)
            domain_model = self.semantic_agent.run(f, domain_model)

            # --- domain enrichment ---
            domain_model = f.enrich_domain(domain_model)

            # --- domain learning ---
            f.learn_domain(domain_model)

            dm = domain_model.get("domain_model", domain_model)

            f.log(
                f"🧠 Semantic enrichment applied "
                f"(value_objects={len(dm.get('value_objects', []))}, "
                f"entities={len(dm.get('entities', []))})"
            )

            architecture_style = self.architecture_reasoning_agent.run(f, domain_model)

            if isinstance(architecture_style, dict):
                f.log(f"🏗 Architecture style selected: {architecture_style.get('architecture_style','unknown')}")
            else:
                f.log("🏗 Architecture style selected")

            architecture = self.architecture_agent.run(f, domain_model)

            # ---- TASK GRAPH BUILDER (observability) ----
            task_graph = self.task_graph_builder.build(architecture)
            f.log(f"🧩 Task graph built ({len(task_graph)} tasks)")

            # ---- DEPENDENCY GRAPH ORDERING ----
            from ai.graph.dependency_graph_builder import DependencyGraphBuilder

            graph = DependencyGraphBuilder()

            ordered_inventory = graph.order_inventory(architecture)

            architecture["file_inventory"] = ordered_inventory

            f.log(f"📦 Dependency ordering applied ({len(ordered_inventory)} files)")

            # ---- INVENTORY VALIDATION / CONSISTENCY ----
            try:
                if self.inventory_validator_agent:
                    ordered_inventory = self.inventory_validator_agent.run(f, ordered_inventory)
                    architecture["file_inventory"] = ordered_inventory
                    f.log("✅ InventoryValidatorAgent applied")
            except Exception as e:
                f.log(f"⚠️ InventoryValidatorAgent skipped: {e}")

            try:
                if self.inventory_consistency_agent:
                    domain_model = self.inventory_consistency_agent.run(f, domain_model)
                    f.log("✅ InventoryConsistencyAgent applied")
            except Exception as e:
                f.log(f"⚠️ InventoryConsistencyAgent skipped: {e}")

            f.state.domain_model = domain_model
            f.state.architecture = architecture

            StateManager.save_specs(
                f.spec_file,
                f.state.domain_model,
                f.state.architecture,
                []
            )

        inventory = f.state.architecture["file_inventory"]

        # ---- CODE GENERATION AGENTS ----
        f.log("⚙️ Starting parallel code generation")
        self.codegen_agent.run(f, inventory)

        f.log("🚀 Code generation finished")

        # ---- LLM JAVA REPAIR PASS (optional) ----
        try:
            if self.java_llm_repair_agent:
                self.java_llm_repair_agent.run(f)
                f.log("🧠 Java LLM repair pass completed")
        except Exception as e:
            f.log(f"⚠️ Java LLM repair skipped: {e}")

        # ---- CODE DEPENDENCY ANALYSIS (post-generation) ----
        try:
            nodes, edges = self.import_dependency_analyzer.build_graph(f, inventory)
            f.log(f"🔎 Import dependency scan completed ({len(edges)} relations detected)")
        except Exception as e:
            f.log(f"⚠️ Import dependency scan skipped: {e}")

        # ---- COMPILE AND FIX LOOP (self-healing) ----
        MAX_FIX_ATTEMPTS = 5
        success = False
        compile_output = ""

        def _regenerate_paths(paths):
            if not paths:
                return
            inv_by_path = {it["path"]: it for it in inventory if "path" in it}
            for p in paths:
                item = inv_by_path.get(p)
                if not item:
                    continue
                try:
                    f._generate_single_file(item, 0, 0)
                    f.log(f"♻️ Regenerated {p}")
                except Exception as e:
                    f.log(f"⚠️ Regeneration failed for {p}: {e}")

        for attempt in range(MAX_FIX_ATTEMPTS):

            success, compile_output = self.compile_agent.run(f)

            if success:
                break

            f.log(f"🧠 Compile fix attempt {attempt+1}/{MAX_FIX_ATTEMPTS}")

            fixed = False

            # 1) Try semantic compile fixer first (imports, missing types, signature mismatches, etc.)
            if self.semantic_compile_fix_agent:
                try:
                    fixed = bool(self.semantic_compile_fix_agent.run(f, compile_output))
                except Exception as e:
                    f.log(f"⚠️ Semantic compile fix skipped: {e}")

            # 2) Fallback to LLM compile fixer
            if not fixed:
                try:
                    result = self.compile_fix_agent.run(f, compile_output)
                    if isinstance(result, dict):
                        fixed = bool(result.get("fixed", True))
                        _regenerate_paths(result.get("regenerate", []))
                    else:
                        fixed = bool(result)
                except Exception as e:
                    f.log(f"⚠️ Compile fix failed: {e}")
                    fixed = False

            if not fixed:
                continue

        if success:
            f.log("✨ PROJECT GENERATED AND VERIFIED")

            # ---- AUTONOMOUS REFACTOR PHASE ----
            try:
                self.refactor_agent.run(f)
                f.log("🧠 Refactor agent completed")
            except Exception as e:
                f.log(f"⚠️ Refactor phase skipped: {e}")

            # ---- RUNTIME FEEDBACK PHASE ----
            if self.runtime_feedback_agent:
                try:
                    runtime_report = self.runtime_feedback_agent.run(f)

                    evolve = self.evolution_agent.run(f, runtime_report)

                    if evolve:
                        f.log("🔁 Evolution cycle triggered")

                    f.log("📊 Runtime feedback analysis completed")

                except Exception as e:
                    f.log(f"⚠️ Runtime feedback skipped: {e}")
            else:
                f.log("⚠️ Runtime feedback agent not available; skipping")

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
                "MODE_ID_RECORD",
                "domain/ExampleId.java",
                (
                    "GENERATION MODE: MODE_ID_RECORD\n"
                    "STRICT RULES (NON-NEGOTIABLE):\n"
                    "- Use Java record\n"
                    "- Field name MUST be 'value'\n"
                    "- Field type MUST be UUID\n"
                    "- Implements ValueObject\n"
                    "- Include canonical constructor validation\n"
                    "- Throw IllegalArgumentException or Objects.requireNonNull if value is null\n"
                    "- Include static factory method newId() returning new <Id>(UUID.randomUUID())\n"
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
           "   <build>\n"
            "    <plugins>\n"
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

            self.domain_memory.learn(signals)

        except Exception as e:
            self.log(f"⚠️ Domain learning skipped: {e}")



    def _generate_single_file(self, item, index, total):
        rel_path = item["path"]
        file_name = Path(rel_path).name

        output_path = self.resolve_output_path(rel_path)

        if output_path.exists():
            self.log(f"⏭️ Skipping existing file {file_name}")
            return

        self.log(f"[{index}/{total}] Fabricating {file_name}")

        _, golden_rel, strict = self.resolve_generation_mode(item)

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

        code = self.executor.run_task(
            "write_code",
            path=rel_path,
            desc=prompt,
            base_package=self.base_package,
            context_data=json.dumps({
                "name": item["entity"],
                "kind": item["description"],
                "fields": item.get("fields", []),
                "values": item.get("values", []),
                "path": rel_path,
                "base_package": self.base_package,
                "expected_package": expected_pkg,
            }),
        )

        from ai.validators.code_verifier import verify_java_code
        from ai.validators.code_auto_fix import auto_fix_java_code

        verification = verify_java_code(code)

        if not verification["valid"]:
            self.log(f"⚠️ Verification issues in {file_name}: {verification['issues']}")
            code = auto_fix_java_code(code, verification["issues"])
            self.log("🔧 Auto-fix applied")

        self.save_to_disk(rel_path, code)

    # ------------------------------------------------


# ------------------ Entrypoint ------------------
if __name__ == "__main__":
    factory = SoftwareFactory(" ".join(sys.argv[1:]))
    orchestrator = FactoryOrchestrator(factory)
    orchestrator.run() 