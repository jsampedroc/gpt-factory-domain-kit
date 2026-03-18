class TemplateJavaGenerator:

    def generate_jpa_entity(self, package_name, class_name, fields):

        lines = []

        lines.append(f"package {package_name};\n\n")

        lines.append("import jakarta.persistence.*;\n")
        lines.append("import java.util.UUID;\n")

        # detect collections
        needs_list = any((f.get("type") or "").startswith("List") for f in fields)

        if needs_list:
            lines.append("import java.util.List;\n")

        # Domain imports are resolved later by the central ImportResolver
        # to avoid duplicate or incorrect imports.

        lines.append("\n")

        lines.append("@Entity\n")
        
        lines.append(f"public class {class_name} {{\n\n")

        lines.append("    @Id\n")
        lines.append("    @GeneratedValue\n")
        lines.append("    private UUID id;\n\n")

        lines.append("    public UUID getId() { return this.id; }\n")
        lines.append("    public void setId(UUID id) { this.id = id; }\n\n")

        for f in fields:
            name = f.get("name")
            type_ = f.get("type")

            if name == "id":
                continue

            lines.append(f"    private {type_} {name};\n")

        # constructor
        lines.append("\n    public " + class_name + "() {}\n")

        # getters and setters
        for f in fields:
            name = f.get("name")
            type_ = f.get("type")

            if name == "id":
                continue

            method = name[0].upper() + name[1:]

            lines.append(f"\n    public {type_} get{method}() {{ return this.{name}; }}\n")
            lines.append(f"    public void set{method}({type_} {name}) {{ this.{name} = {name}; }}\n")

        lines.append("\n}\n")

        return "".join(lines)

    def generate_repository(self, package_name, entity, base_package=None, module=None):

        if module:
            model_import = f"{base_package}.{module}.domain.model.{entity}"
        else:
            model_import = f"{base_package}.domain.model.{entity}"

        return f"""
package {package_name};

import {model_import};
import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface {entity}Repository {{

    {entity} save({entity} entity);

    Optional<{entity}> findById(UUID id);

    List<{entity}> findAll();

}}

"""

    def generate_spring_data_repository(self, package_name, entity, base_package, module=None):

        if module:
            jpa_entity_import = f"{base_package}.{module}.infrastructure.persistence.entity.{entity}JpaEntity"
        else:
            jpa_entity_import = f"{base_package}.infrastructure.persistence.entity.{entity}JpaEntity"

        return f"""
package {package_name};

import org.springframework.data.jpa.repository.JpaRepository;
import {jpa_entity_import};
import java.util.UUID;

public interface SpringData{entity}Repository extends JpaRepository<{entity}JpaEntity, UUID> {{
}}
"""

    def generate_service(self, package_name, class_name, entity, base_package, module=None):

        if module:
            model_import = f"{base_package}.{module}.domain.model.{entity}"
            repo_import = f"{base_package}.{module}.domain.repository.{entity}Repository"
        else:
            model_import = f"{base_package}.domain.model.{entity}"
            repo_import = f"{base_package}.domain.repository.{entity}Repository"

        return f"""
package {package_name};

import {model_import};
import {repo_import};

public class {class_name} {{

    private final {entity}Repository repository;

    public {class_name}({entity}Repository repository) {{
        this.repository = repository;
    }}

}}
"""

    def generate_jpa_adapter(self, package_name, class_name, entity, fields, base_package, module=None):
        """
        Deterministic JPA repository adapter.
        Never uses LLM — constructor arity is always correct.
        fields: non-id entity fields from inventory (id is always prepended by AST generator)
        """

        if module:
            domain_model_import = f"{base_package}.{module}.domain.model.{entity}"
            repo_import = f"{base_package}.{module}.domain.repository.{entity}Repository"
            id_import = f"{base_package}.{module}.domain.valueobject.{entity}Id"
            jpa_entity_import = f"{base_package}.{module}.infrastructure.persistence.entity.{entity}JpaEntity"
            spring_repo_import = f"{base_package}.{module}.infrastructure.persistence.spring.SpringData{entity}Repository"
        else:
            domain_model_import = f"{base_package}.domain.model.{entity}"
            repo_import = f"{base_package}.domain.repository.{entity}Repository"
            id_import = f"{base_package}.domain.valueobject.{entity}Id"
            jpa_entity_import = f"{base_package}.infrastructure.persistence.entity.{entity}JpaEntity"
            spring_repo_import = f"{base_package}.infrastructure.persistence.spring.SpringData{entity}Repository"

        # Build per-field mapping lines
        # Non-id fields: use their original type (enums, VOs, primitives stay as-is)
        non_id_fields = [f for f in fields if f.get("name") != "id"]

        to_jpa_setters = "\n".join(
            f"        jpa.set{f['name'][0].upper() + f['name'][1:]}(domain.get{f['name'][0].upper() + f['name'][1:]}());"
            for f in non_id_fields
        )

        to_domain_args = ",\n            ".join(
            [f"new {entity}Id(jpa.getId())"] +
            [f"jpa.get{f['name'][0].upper() + f['name'][1:]}()" for f in non_id_fields]
        )

        return f"""package {package_name};

import {domain_model_import};
import {repo_import};
import {id_import};
import {jpa_entity_import};
import {spring_repo_import};
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;

@Repository
public class {class_name} implements {entity}Repository {{

    private final SpringData{entity}Repository springRepository;

    public {class_name}(SpringData{entity}Repository springRepository) {{
        this.springRepository = springRepository;
    }}

    @Override
    public {entity} save({entity} entity) {{
        {entity}JpaEntity jpa = toJpaEntity(entity);
        return toDomain(springRepository.save(jpa));
    }}

    @Override
    public Optional<{entity}> findById(UUID id) {{
        return springRepository.findById(id).map(this::toDomain);
    }}

    @Override
    public List<{entity}> findAll() {{
        return springRepository.findAll().stream().map(this::toDomain).collect(Collectors.toList());
    }}

    private {entity}JpaEntity toJpaEntity({entity} domain) {{
        {entity}JpaEntity jpa = new {entity}JpaEntity();
        jpa.setId(domain.getId().value());
{to_jpa_setters}
        return jpa;
    }}

    private {entity} toDomain({entity}JpaEntity jpa) {{
        return new {entity}(
            {to_domain_args}
        );
    }}
}}
"""

    def _generate_execute_body(self, entity, use_case_name, uc_type, uc_inputs,
                               uc_returns, entity_fields):
        """
        Deterministic execute() body. Uses only known repository methods and correct
        Java record accessor syntax (fieldName(), not getFieldName()).
        """
        dto_var = "command" if uc_type == "command" else "query"
        entity_var = entity[0].lower() + entity[1:]
        is_list = str(uc_returns).startswith("List")
        is_query = uc_type == "query"
        uc_lower = use_case_name.lower()
        is_deactivate = any(w in uc_lower for w in ("deactivat", "cancel", "remov", "delet"))
        is_update = any(w in uc_lower for w in ("update", "edit", "modif", "change"))

        # Find the id input field from the use case inputs
        id_input = next(
            (i for i in (uc_inputs or []) if i.get("name", "").lower().endswith("id")),
            None
        )
        id_field = id_input["name"] if id_input else None

        if is_list:
            return "        return repository.findAll();"

        if is_query:
            if id_field:
                return (
                    f"        return repository.findById({dto_var}.{id_field}());"
                )
            return "        return repository.findAll().stream().findFirst();"

        if is_deactivate or is_update:
            if id_field:
                return (
                    f"        return repository.findById({dto_var}.{id_field}())\n"
                    f"            .orElseThrow(() -> new IllegalArgumentException("
                    f"\"Not found\"));"
                )
            return "        throw new UnsupportedOperationException(\"Not implemented\");"

        # CREATE command — build entity constructor
        # Non-id entity fields (excluding base 'id')
        non_id_fields = [f for f in (entity_fields or []) if f.get("name") != "id"]
        input_names = {i.get("name") for i in (uc_inputs or [])}

        args = [f"new {entity}Id(UUID.randomUUID())"]
        for f in non_id_fields:
            fname = f.get("name")
            ftype = f.get("type", "")
            if fname in input_names:
                args.append(f"{dto_var}.{fname}()")
            elif ftype == "UUID" or fname.lower().endswith("id"):
                args.append("UUID.randomUUID()")
            else:
                args.append("null")

        args_str = ",\n            ".join(args)
        return (
            f"        {entity} {entity_var} = new {entity}(\n"
            f"            {args_str}\n"
            f"        );\n"
            f"        return repository.save({entity_var});"
        )

    def generate_usecase(self, package_name, use_case_name, entity, uc_type,
                         uc_inputs, uc_returns, uc_description, base_package,
                         module=None, entity_fields=None):
        """
        Deterministic use case class. One method: execute(Command/Query) -> return_type.
        Body is generated deterministically (no LLM).
        """
        if module:
            repo_import = f"{base_package}.{module}.domain.repository.{entity}Repository"
            model_import = f"{base_package}.{module}.domain.model.{entity}"
        else:
            repo_import = f"{base_package}.domain.repository.{entity}Repository"
            model_import = f"{base_package}.domain.model.{entity}"

        dto_suffix = "Command" if uc_type == "command" else "Query"
        dto_class = f"{use_case_name}{dto_suffix}"

        # Determine return type
        returns = uc_returns or entity
        needs_optional = uc_type == "query" and not returns.startswith("List")
        if needs_optional:
            return_type = f"Optional<{returns}>"
        elif returns.startswith("List"):
            return_type = f"List<{entity}>"
        else:
            return_type = returns

        # Id type import
        if module:
            id_import = f"{base_package}.{module}.domain.valueobject.{entity}Id"
        else:
            id_import = f"{base_package}.domain.valueobject.{entity}Id"

        # Deterministic execute() body
        body = self._generate_execute_body(
            entity, use_case_name, uc_type, uc_inputs, uc_returns, entity_fields or []
        )

        return f"""package {package_name};

import {model_import};
import {repo_import};
import {id_import};
import java.util.UUID;
import java.util.Optional;
import java.util.List;
import org.springframework.stereotype.Service;

/**
 * {uc_description or use_case_name}
 */
@Service
public class {use_case_name}UseCase {{

    private final {entity}Repository repository;

    public {use_case_name}UseCase({entity}Repository repository) {{
        this.repository = repository;
    }}

    public {return_type} execute({dto_class} {dto_suffix.lower()}) {{
{body}
    }}
}}
"""

    def generate_usecase_command(self, package_name, use_case_name, inputs):
        """Generates a Command record (input DTO for a command use case)."""
        inputs = self._dedup_inputs(inputs)
        imports = self._imports_for_inputs(inputs)
        imports_str = ("".join(f"import {i};\n" for i in sorted(imports)) + "\n") if imports else ""
        fields_str = ",\n    ".join(
            f"{inp.get('type', 'String')} {inp.get('name', 'value')}"
            for inp in (inputs or [])
        ) if inputs else ""

        if fields_str:
            return f"""package {package_name};

{imports_str}public record {use_case_name}Command(
    {fields_str}
) {{}}
"""
        return f"""package {package_name};

public record {use_case_name}Command() {{}}
"""

    def generate_usecase_query(self, package_name, use_case_name, inputs):
        """Generates a Query record (input DTO for a query use case)."""
        inputs = self._dedup_inputs(inputs)
        imports = self._imports_for_inputs(inputs)
        imports_str = ("".join(f"import {i};\n" for i in sorted(imports)) + "\n") if imports else ""
        fields_str = ",\n    ".join(
            f"{inp.get('type', 'String')} {inp.get('name', 'value')}"
            for inp in (inputs or [])
        ) if inputs else ""

        if fields_str:
            return f"""package {package_name};

{imports_str}public record {use_case_name}Query(
    {fields_str}
) {{}}
"""
        return f"""package {package_name};

public record {use_case_name}Query() {{}}
"""

    @staticmethod
    def _dedup_inputs(inputs):
        """Remove duplicate fields by name, keeping first occurrence."""
        seen = set()
        result = []
        for inp in (inputs or []):
            name = inp.get("name")
            if name and name not in seen:
                seen.add(name)
                result.append(inp)
        return result

    @staticmethod
    def _imports_for_inputs(inputs):
        """Returns the set of Java standard imports needed for the given input fields."""
        TYPE_IMPORTS = {
            "UUID": "java.util.UUID",
            "LocalDate": "java.time.LocalDate",
            "LocalDateTime": "java.time.LocalDateTime",
            "Instant": "java.time.Instant",
            "BigDecimal": "java.math.BigDecimal",
            "List": "java.util.List",
            "Optional": "java.util.Optional",
        }
        needed = set()
        for inp in (inputs or []):
            t = inp.get("type", "")
            for key, imp in TYPE_IMPORTS.items():
                if key in t:
                    needed.add(imp)
        return needed

    def generate_mapper(self, package_name, class_name, entity, base_package, module=None):
        if module:
            domain_import = f"{base_package}.{module}.domain.model.{entity}"
            req_import = f"{base_package}.{module}.application.dto.{entity}Request"
            res_import = f"{base_package}.{module}.application.dto.{entity}Response"
        else:
            domain_import = f"{base_package}.domain.model.{entity}"
            req_import = f"{base_package}.application.dto.{entity}Request"
            res_import = f"{base_package}.application.dto.{entity}Response"

        return f"""package {package_name};

import {domain_import};
import {req_import};
import {res_import};
import org.mapstruct.Mapper;

@Mapper(componentModel = "spring")
public interface {class_name} {{

    {entity}Response toResponse({entity} entity);

}}
"""

    def generate_controller(self, package_name, class_name, entity, base_package, module=None):
        return f"""package {package_name};

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import java.util.UUID;

@RestController
@RequestMapping("/{entity.lower()}s")
public class {class_name} {{

    // TODO: inject use cases via constructor injection

}}
"""