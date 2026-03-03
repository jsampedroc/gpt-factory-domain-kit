# main.py — AI SOFTWARE FACTORY (STABLE, HARDENED, PROFESSIONAL)
import sys
import json
import yaml
import re
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from ai.pipeline.state_manager import StateManager
from ai.pipeline.task_executor import TaskExecutor
from ai.utils.logging_helper import Tee
from ai.validators.layer_contracts import LayerContracts


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
        desc = item["description"]

        if desc == "ENUM":
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
                    "- Follow the golden sample EXACTLY (structure/style)\n"
                )
            )

        if desc == "Entity":
            return (
                "MODE_DOMAIN_ENTITY",
                "domain/Example.java",
                (
                    "GENERATION MODE: MODE_DOMAIN_ENTITY\n"
                    "STRICT RULES (NON-NEGOTIABLE):\n"
                    "- Plain Java ONLY\n"
                    "- NO Lombok\n"
                    "- NO jakarta.*, javax.*\n"
                    "- NO annotations of any kind\n"
                    "- NO frameworks\n"
                    "- Use explicit constructors\n"
                    "- Use Objects.requireNonNull ONLY if needed for fields declared in THIS class\n"
                    "- DO NOT add unused imports\n"
                    "- Follow golden sample EXACTLY\n"
                )
            )

        if desc == "ID Record":
            return (
                "MODE_ID_RECORD",
                "domain/ExampleId.java",
                (
                    "GENERATION MODE: MODE_ID_RECORD\n"
                    "STRICT RULES (NON-NEGOTIABLE):\n"
                    "- Java class or record (no Lombok)\n"
                    "- Implements ValueObject\n"
                    "- NO annotations\n"
                    "- NO frameworks\n"
                    "- Follow golden sample EXACTLY\n"
                )
            )

        if desc == "Repository Interface":
            return ("MODE_DOMAIN_REPOSITORY_PORT", "domain/ExampleRepository.java", "")

        if desc == "Service":
            return ("MODE_APPLICATION_SERVICE", "application/ExampleService.java", "")

        if desc == "Mapper":
            return ("MODE_MAPPER", "application/ExampleMapper.java", "")

        if desc == "DTO_REQUEST":
            return (
                "MODE_DTO_REQUEST",
                "application/ExampleRequest.java",
                (
                    "GENERATION MODE: MODE_DTO_REQUEST\n"
                    "STRICT RULES (NON-NEGOTIABLE):\n"
                    "- Plain Java DTO\n"
                    "- NO annotations\n"
                    "- NO jakarta.*, javax.*\n"
                    "- NO Lombok\n"
                    "- final fields\n"
                    "- constructor with all fields\n"
                    "- getters only\n"
                    "- Follow golden sample EXACTLY\n"
                )
            )

        if desc == "DTO_RESPONSE":
            return (
                "MODE_DTO_RESPONSE",
                "application/ExampleResponse.java",
                (
                    "GENERATION MODE: MODE_DTO_RESPONSE\n"
                    "STRICT RULES (NON-NEGOTIABLE):\n"
                    "- Plain Java DTO\n"
                    "- NO annotations\n"
                    "- NO jakarta.*, javax.*\n"
                    "- NO Lombok\n"
                    "- final fields\n"
                    "- constructor with all fields\n"
                    "- getters only\n"
                    "- Follow golden sample EXACTLY\n"
                )
            )

        # ✅ OPTION B (HEXAGONAL CORRECT): JPA ENTITY + SPRING DATA + ADAPTER
        if desc == "JPA_ENTITY":
            return (
                "MODE_JPA_ENTITY",
                "infrastructure/ExampleJpaEntity.java",
                (
                    "GENERATION MODE: MODE_JPA_ENTITY\n"
                    "STRICT RULES (NON-NEGOTIABLE):\n"
                    "- infrastructure.persistence.entity\n"
                    "- Use ONLY jakarta.persistence annotations (@Entity, @Table, @Id, @Column)\n"
                    "- NO Lombok\n"
                    "- NO Hibernate-specific annotations (org.hibernate.*)\n"
                    "- ID type MUST be java.util.UUID\n"
                    "- Provide: protected no-arg ctor + explicit public ctor\n"
                    "- Provide explicit getters\n"
                    "- NO mapping methods to/from domain inside this class\n"
                    "- Follow golden sample EXACTLY\n"
                )
            )

        if desc == "SPRING_DATA_REPOSITORY":
            return (
                "MODE_SPRING_DATA_REPOSITORY",
                "infrastructure/SpringDataExampleRepository.java",
                (
                    "GENERATION MODE: MODE_SPRING_DATA_REPOSITORY\n"
                    "STRICT RULES (NON-NEGOTIABLE):\n"
                    "- Extends JpaRepository<ExampleJpaEntity, UUID>\n"
                    "- NO domain model references in generics\n"
                    "- NO Lombok\n"
                    "- Follow golden sample EXACTLY\n"
                )
            )

        if desc == "JPA_ADAPTER":
            return (
                "MODE_JPA_ADAPTER",
                "infrastructure/JpaExampleRepositoryAdapter.java",
                (
                    "GENERATION MODE: MODE_JPA_ADAPTER\n"
                    "STRICT RULES (NON-NEGOTIABLE):\n"
                    "- Implements domain repository interface\n"
                    "- Depends on SpringData repo + JpaEntity\n"
                    "- Explicit constructor injection\n"
                    "- Mapping inside adapter (NO separate mapper class)\n"
                    "- Follow golden sample EXACTLY\n"
                )
            )

        if desc == "Controller":
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

        # Domain enums
        for enum in model.get("enums", []):
            inventory.append({
                "path": f"domain/shared/{enum['name']}.java",
                "entity": enum["name"],
                "description": "ENUM",
                "values": enum.get("values", []),
            })

        layers = [
            ("domain/model", "{name}.java", "Entity"),
            ("domain/valueobject", "{name}Id.java", "ID Record"),
            ("domain/repository", "{name}Repository.java", "Repository Interface"),

            ("application/service", "{name}Service.java", "Service"),
            ("application/dto", "{name}Request.java", "DTO_REQUEST"),
            ("application/dto", "{name}Response.java", "DTO_RESPONSE"),
            ("application/mapper", "{name}Mapper.java", "Mapper"),

            # Infrastructure - persistence (Option B)
            ("infrastructure/persistence/entity", "{name}JpaEntity.java", "JPA_ENTITY"),
            ("infrastructure/persistence/spring", "SpringData{name}Repository.java", "SPRING_DATA_REPOSITORY"),
            ("infrastructure/persistence/adapter", "Jpa{name}RepositoryAdapter.java", "JPA_ADAPTER"),

            ("infrastructure/rest", "{name}Controller.java", "Controller"),
        ]

        for ent in model.get("entities", []):
            for folder, tpl, desc in layers:
                inventory.append({
                    "path": f"{folder}/{tpl.format(name=ent['name'])}",
                    "entity": ent["name"],
                    "description": desc,
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
    def run(self):
        tee = Tee(self.out_dir / "execution.log")
        sys.stdout = tee

        try:
            self.log(f"🚀 ENGINE ACTIVE: {self.project_name}")

            # --- BOOTSTRAP (NO LLM) ---
            self._bootstrap_pom()
            self._bootstrap_domain_kernel()

            # --- DOMAIN MODEL ---
            if not StateManager.load_specs(self.spec_file, self.state):
                # ✅ CRITICAL: pass base_package (prevents com.example + broken packages)
                raw = self.executor.run_task(
                    "model_domain",
                    idea=self.idea,
                    base_package=self.base_package,
                )
                self.state.domain_model = json.loads(raw)
                self.state.architecture = {
                    "file_inventory": self.generate_inventory(self.state.domain_model)
                }
                StateManager.save_specs(self.spec_file, self.state.domain_model, self.state.architecture, [])

            inventory = self.state.architecture["file_inventory"]

            # --- CODE GENERATION ---
            for i, item in enumerate(inventory, 1):
                rel_path = item["path"]
                file_name = Path(rel_path).name
                self.log(f"[{i}/{len(inventory)}] Fabricating {file_name}")

                _, golden_rel, strict = self.resolve_generation_mode(item)

                # Enforce package from engine (LLM must comply)
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
                        # Strip package from golden sample to avoid misleading the model
                        golden_body = self._strip_package_line(p.read_text(encoding="utf-8"))
                        golden = (
                            "\n=== GOLDEN SAMPLE (FOLLOW EXACTLY, CHANGE NAMES ONLY) ===\n"
                            + golden_body
                            + "\n=== END GOLDEN SAMPLE ===\n"
                        )

                prompt = mandatory_header + strict + "\n" + golden

                # ✅ CRITICAL: always pass base_package to write_code
                code = self.executor.run_task(
                    "write_code",
                    path=rel_path,
                    desc=prompt,
                    base_package=self.base_package,
                    context_data=json.dumps({
                        "name": item["entity"],
                        "kind": item["description"],
                        "values": item.get("values", []),
                        "path": rel_path,
                        "base_package": self.base_package,
                        "expected_package": expected_pkg,
                    }),
                )

                self.save_to_disk(rel_path, code)

            self.log("✨ PROJECT GENERATED SUCCESSFULLY")

        except Exception as e:
            self.log(f"❌ FATAL: {e}")
            import traceback
            traceback.print_exc()
        finally:
            sys.stdout = sys.__stdout__
            tee.close()


# ------------------ Entrypoint ------------------
if __name__ == "__main__":
    SoftwareFactory(" ".join(sys.argv[1:])).run()