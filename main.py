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
        total = len(inventory)

        with ThreadPoolExecutor(max_workers=6) as pool:
            futures = []

            for i, item in enumerate(inventory, 1):
                futures.append(
                    pool.submit(
                        factory._generate_single_file,
                        item,
                        i,
                        total
                    )
                )

            for future in as_completed(futures):
                future.result()


class CompileAgent:
    def run(self, factory):
        success, output = factory._compile_project()
        return success, output


class CompileFixAgent:
    def run(self, factory, compile_output):
        fixed = factory.executor.run_task(
            "fix_compile_error",
            error_log=compile_output,
            base_package=factory.base_package
        )
        return fixed



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

                for node in nodes:
                    if node.endswith(rel):
                        edges[path].add(node)

        return nodes, edges

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
        self.compile_agent = CompileAgent()
        self.compile_fix_agent = CompileFixAgent()
        self.task_graph_builder = TaskGraphBuilder()
        self.import_dependency_analyzer = ImportDependencyAnalyzer()

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

            f.log(f"🏗 Architecture style selected: {architecture_style['architecture_style']}")

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

        # ---- IMPORT DEPENDENCY ANALYSIS (post-generation) ----
        try:
            nodes, edges = self.import_dependency_analyzer.build_graph(f, inventory)
            f.log(f"🔎 Import dependency scan completed ({len(edges)} relations detected)")
        except Exception as e:
            f.log(f"⚠️ Import dependency scan skipped: {e}")

        success, compile_output = self.compile_agent.run(f)

        if not success:
            f.log("🧠 Attempting automatic compile fix...")
            fixed = self.compile_fix_agent.run(f, compile_output)

            if fixed:
                f.log("🔧 Compile fix attempt applied")
                success, _ = self.compile_agent.run(f)

        if success:
            f.log("✨ PROJECT GENERATED AND VERIFIED")
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
            "  <build>\n"
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