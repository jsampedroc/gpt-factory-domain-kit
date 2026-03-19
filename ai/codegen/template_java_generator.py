class TemplateJavaGenerator:

    # JDK types that Hibernate can map natively — everything else must be converted
    _JDK_TYPES = {
        "String", "UUID", "Integer", "Long", "Double", "Float", "Boolean",
        "int", "long", "double", "float", "boolean",
        "LocalDate", "LocalDateTime", "Instant", "BigDecimal",
        "Short", "Byte", "Character",
    }

    # Domain value-object / custom types → JPA-safe JDK equivalent
    _VO_TYPE_MAP = {
        "Money": "BigDecimal",
        "Price": "BigDecimal",
        "Amount": "BigDecimal",
    }

    @classmethod
    def _jpa_type(cls, java_type: str) -> str:
        """
        Convert a domain type to a JPA-safe JDK type.
        - Known VO wrappers (Money, Price…) → BigDecimal
        - *Status / *Type / *Kind / *State value objects → String
        - *Id value objects → UUID
        - List<X> / Set<X> → kept as-is (caller handles separately)
        - Everything else that is a JDK primitive/type → unchanged
        """
        if not java_type:
            return "String"
        outer = java_type.split("<")[0]
        if outer in cls._JDK_TYPES:
            return java_type  # already safe
        if outer in cls._VO_TYPE_MAP:
            return cls._VO_TYPE_MAP[outer]
        if outer.endswith("Id"):
            return "UUID"
        if any(outer.endswith(sfx) for sfx in ("Status", "Type", "Kind", "State", "Category", "Role")):
            return "String"
        if java_type.startswith("List<") or java_type.startswith("Set<"):
            return java_type  # handled elsewhere
        # Unknown custom type → String (safe fallback)
        return "String"

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

        # Derive @Table name: strip JpaEntity suffix, convert CamelCase → snake_case
        entity_base = class_name.replace("JpaEntity", "")
        import re as _re
        table_name = _re.sub(r"([A-Z])", r"_\1", entity_base).lstrip("_").lower()

        lines.append("@Entity\n")
        lines.append(f"@Table(name = \"{table_name}\")\n")
        lines.append(f"public class {class_name} {{\n\n")

        lines.append("    @Id\n")
        lines.append("    @GeneratedValue\n")
        lines.append("    private UUID id;\n\n")

        lines.append("    public UUID getId() { return this.id; }\n")
        lines.append("    public void setId(UUID id) { this.id = id; }\n\n")

        needs_bigdecimal = any(self._jpa_type(f.get("type", "")) == "BigDecimal" for f in fields if f.get("name") != "id")
        needs_localdate = any(f.get("type", "").startswith("LocalDate") for f in fields if f.get("name") != "id")
        needs_localdatetime = any(f.get("type", "") == "LocalDateTime" for f in fields if f.get("name") != "id")

        if needs_bigdecimal:
            lines.append("import java.math.BigDecimal;\n")
        if needs_localdate or needs_localdatetime:
            pass  # LocalDate/LocalDateTime imports added by import resolver

        for f in fields:
            name = f.get("name")
            type_ = self._jpa_type(f.get("type") or "String")

            if name == "id":
                continue

            lines.append(f"    private {type_} {name};\n")

        # constructor
        lines.append("\n    public " + class_name + "() {}\n")

        # getters and setters
        for f in fields:
            name = f.get("name")
            type_ = self._jpa_type(f.get("type") or "String")

            if name == "id":
                continue

            method = name[0].upper() + name[1:]

            lines.append(f"\n    public {type_} get{method}() {{ return this.{name}; }}\n")
            lines.append(f"    public void set{method}({type_} {name}) {{ this.{name} = {name}; }}\n")

        lines.append("\n}\n")

        return "".join(lines)

    def generate_page_result(self, package_name: str) -> str:
        """Domain-layer PageResult<T> — no Spring dependency."""
        return f"""package {package_name};

import java.util.List;

public record PageResult<T>(
        List<T> content,
        int page,
        int size,
        long total) {{

    public int totalPages() {{
        return size == 0 ? 0 : (int) Math.ceil((double) total / size);
    }}

    public boolean isLast() {{
        return page >= totalPages() - 1;
    }}
}}
"""

    def generate_page_response(self, package_name: str) -> str:
        """HTTP-layer PageResponse<T> record returned by controllers."""
        return f"""package {package_name};

import java.util.List;

public record PageResponse<T>(
        List<T> content,
        int page,
        int size,
        long total,
        int totalPages,
        boolean last) {{}}
"""

    def generate_global_exception_handler(self, package_name: str) -> str:
        """@ControllerAdvice that returns structured JSON errors."""
        return f"""package {package_name};

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@RestControllerAdvice
public class GlobalExceptionHandler {{

    @ExceptionHandler(IllegalArgumentException.class)
    public ResponseEntity<Map<String, Object>> handleBadRequest(IllegalArgumentException ex) {{
        return error(HttpStatus.BAD_REQUEST, ex.getMessage());
    }}

    @ExceptionHandler(IllegalStateException.class)
    public ResponseEntity<Map<String, Object>> handleConflict(IllegalStateException ex) {{
        return error(HttpStatus.CONFLICT, ex.getMessage());
    }}

    @ExceptionHandler(jakarta.persistence.EntityNotFoundException.class)
    public ResponseEntity<Map<String, Object>> handleNotFound(jakarta.persistence.EntityNotFoundException ex) {{
        return error(HttpStatus.NOT_FOUND, ex.getMessage());
    }}

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<Map<String, Object>> handleValidation(MethodArgumentNotValidException ex) {{
        List<String> errors = ex.getBindingResult().getFieldErrors().stream()
                .map(fe -> fe.getField() + ": " + fe.getDefaultMessage())
                .toList();
        Map<String, Object> body = buildBody(HttpStatus.BAD_REQUEST, "Validation failed");
        body.put("errors", errors);
        return ResponseEntity.badRequest().body(body);
    }}

    @ExceptionHandler(Exception.class)
    public ResponseEntity<Map<String, Object>> handleGeneric(Exception ex) {{
        return error(HttpStatus.INTERNAL_SERVER_ERROR, "Internal server error");
    }}

    private ResponseEntity<Map<String, Object>> error(HttpStatus status, String message) {{
        return ResponseEntity.status(status).body(buildBody(status, message));
    }}

    private Map<String, Object> buildBody(HttpStatus status, String message) {{
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("timestamp", Instant.now().toString());
        body.put("status", status.value());
        body.put("error", status.getReasonPhrase());
        body.put("message", message);
        return body;
    }}
}}
"""

    def generate_repository(self, package_name, entity, base_package=None, module=None):

        if module:
            model_import = f"{base_package}.{module}.domain.model.{entity}"
            page_import = f"{base_package}.shared.PageResult"
        else:
            model_import = f"{base_package}.domain.model.{entity}"
            page_import = f"{base_package}.shared.PageResult"

        return f"""
package {package_name};

import {model_import};
import {page_import};
import java.util.Optional;
import java.util.UUID;

public interface {entity}Repository {{

    {entity} save({entity} entity);

    Optional<{entity}> findById(UUID id);

    PageResult<{entity}> findAll(int page, int size, String search);

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
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import {jpa_entity_import};
import java.util.UUID;

public interface SpringData{entity}Repository
        extends JpaRepository<{entity}JpaEntity, UUID>,
                JpaSpecificationExecutor<{entity}JpaEntity> {{
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

        # Build per-field mapping lines with VO → JDK type conversion
        non_id_fields = [f for f in fields if f.get("name") != "id"]

        def _setter_expr(f):
            """domain.getX() → jpa.setX(expr) with VO unwrapping if needed."""
            fname = f["name"]
            method = fname[0].upper() + fname[1:]
            orig_type = f.get("type", "String")
            jpa_t = self._jpa_type(orig_type)
            outer = orig_type.split("<")[0]
            domain_getter = f"domain.get{method}()"
            if jpa_t == orig_type:
                # No conversion needed
                expr = domain_getter
            elif jpa_t == "BigDecimal":
                if outer == "Money":
                    expr = f"{domain_getter} != null ? java.math.BigDecimal.valueOf({domain_getter}.getAmount()) : null"
                else:
                    expr = f"{domain_getter} != null ? java.math.BigDecimal.valueOf({domain_getter}) : null"
            elif jpa_t == "String":
                if outer.endswith("Id"):
                    expr = f"{domain_getter} != null ? {domain_getter}.getValue() : null"
                else:
                    # *Status/*Type/*Kind VO: call .getValue()
                    expr = f"{domain_getter} != null ? {domain_getter}.getValue() : null"
            elif jpa_t == "UUID":
                expr = f"{domain_getter} != null ? {domain_getter}.value() : null"
            else:
                expr = domain_getter
            return f"        jpa.set{method}({expr});"

        def _domain_arg(f):
            """jpa.getX() → arg in domain constructor with JDK → VO wrapping if needed."""
            fname = f["name"]
            method = fname[0].upper() + fname[1:]
            orig_type = f.get("type", "String")
            jpa_t = self._jpa_type(orig_type)
            outer = orig_type.split("<")[0]
            jpa_getter = f"jpa.get{method}()"
            if jpa_t == orig_type:
                return jpa_getter
            elif jpa_t == "BigDecimal":
                if outer == "Money":
                    return f"{jpa_getter} != null ? new {orig_type}({jpa_getter}.doubleValue(), \"USD\") : null"
                else:
                    return jpa_getter
            elif jpa_t == "String":
                # Wrap back into VO
                return f"new {orig_type}({jpa_getter})"
            elif jpa_t == "UUID":
                return f"new {orig_type}({jpa_getter})"
            return jpa_getter

        to_jpa_setters = "\n".join(_setter_expr(f) for f in non_id_fields)

        to_domain_args = ",\n            ".join(
            [f"new {entity}Id(jpa.getId())"] +
            [_domain_arg(f) for f in non_id_fields]
        )

        needs_bigdecimal = any(self._jpa_type(f.get("type", "")) == "BigDecimal" for f in non_id_fields)
        bigdecimal_import = "import java.math.BigDecimal;\n" if needs_bigdecimal else ""

        # Detect String fields usable in search predicate
        str_fields = [
            f["name"] for f in non_id_fields
            if self._jpa_type(f.get("type", "String")) == "String"
            and not f["name"].lower().endswith("id")
        ][:4]  # cap to 4 most relevant

        if str_fields:
            predicate_lines = " ".join(
                f'cb.like(cb.lower(root.get("{fn}")), like),'
                for fn in str_fields
            ).rstrip(",")
            search_body = (
                f"        if (search != null && !search.isBlank()) {{\n"
                f"            String like = \"%\" + search.toLowerCase() + \"%\";\n"
                f"            spec = spec.and((root, q, cb) -> cb.or(\n"
                f"                {predicate_lines}\n"
                f"            ));\n"
                f"        }}"
            )
        else:
            search_body = "        // no searchable string fields"

        if module:
            page_import = f"{base_package}.shared.PageResult"
        else:
            page_import = f"{base_package}.shared.PageResult"

        return f"""package {package_name};

import {domain_model_import};
import {repo_import};
import {id_import};
import {jpa_entity_import};
import {spring_repo_import};
import {page_import};
import org.springframework.data.domain.PageRequest;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;
{bigdecimal_import}

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
    public PageResult<{entity}> findAll(int page, int size, String search) {{
        Specification<{entity}JpaEntity> spec = Specification.where(null);
{search_body}
        var p = springRepository.findAll(spec, PageRequest.of(page, size));
        List<{entity}> content = p.getContent().stream().map(this::toDomain).collect(Collectors.toList());
        return new PageResult<>(content, page, size, p.getTotalElements());
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
            return f"        return repository.findAll({dto_var}.page(), {dto_var}.size(), {dto_var}.search());"

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
        is_list_all = use_case_name.startswith("ListAll")
        needs_optional = uc_type == "query" and not returns.startswith("List") and not is_list_all
        if is_list_all:
            return_type = f"PageResult<{entity}>"
        elif needs_optional:
            return_type = f"Optional<{returns}>"
        elif returns.startswith("List"):
            return_type = f"List<{entity}>"
        else:
            return_type = returns

        # Id type import
        if module:
            id_import = f"{base_package}.{module}.domain.valueobject.{entity}Id"
            page_result_import = f"{base_package}.shared.PageResult"
        else:
            id_import = f"{base_package}.domain.valueobject.{entity}Id"
            page_result_import = f"{base_package}.shared.PageResult"

        # Deterministic execute() body
        body = self._generate_execute_body(
            entity, use_case_name, uc_type, uc_inputs, uc_returns, entity_fields or []
        )

        return f"""package {package_name};

import {model_import};
import {repo_import};
import {id_import};
import {page_result_import};
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
        """Generates a Query record. ListAll* queries automatically get page/size/search fields."""
        is_list_all = use_case_name.startswith("ListAll")
        inputs = self._dedup_inputs(inputs)

        if is_list_all:
            # Always inject pagination params for list queries
            pagination = [
                {"name": "page", "type": "int"},
                {"name": "size", "type": "int"},
                {"name": "search", "type": "String"},
            ]
            # Merge: keep any extra inputs from spec, deduplicate
            extra = [i for i in inputs if i.get("name") not in ("page", "size", "search")]
            inputs = pagination + extra

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

    def generate_response_dto(self, package_name, entity, fields, base_package=None, module=None):
        """
        Generates a flat *Response record using only JDK-safe types.
        VO types (Money, *Status, *Id…) are unwrapped to String / Double / UUID.
        Always has UUID id as first field.
        """
        import re as _re

        def _response_type(java_type: str) -> str:
            outer = java_type.split("<")[0]
            if outer in self._JDK_TYPES:
                # LocalDate / LocalDateTime → String for clean JSON
                if outer in ("LocalDate", "LocalDateTime", "Instant"):
                    return "String"
                return java_type
            if outer in self._VO_TYPE_MAP or outer in ("Money", "Price", "Amount"):
                return "Double"
            if outer.endswith("Id"):
                return "UUID"
            if any(outer.endswith(s) for s in ("Status", "Type", "Kind", "State", "Category", "Role")):
                return "String"
            return "String"

        non_id_fields = [f for f in fields if f.get("name") != "id"]
        fields_str = "        UUID id"
        for f in non_id_fields:
            fname = f.get("name", "value")
            rtype = _response_type(f.get("type", "String"))
            fields_str += f",\n        {rtype} {fname}"

        needs_uuid = True  # id is always UUID
        needs_bigdecimal = any(
            _response_type(f.get("type", "")) == "BigDecimal" for f in non_id_fields
        )

        imports = ["import java.util.UUID;"]
        if needs_bigdecimal:
            imports.append("import java.math.BigDecimal;")

        imports_str = "\n".join(imports)

        return f"""package {package_name};

{imports_str}

public record {entity}Response(
{fields_str}
) {{}}
"""

    def generate_controller(self, package_name, class_name, entity, base_package, module=None, fields=None):
        """
        Full REST controller with 5 endpoints wired to the 5 standard use cases.
        toResponse() unwraps VO types to JDK types matching *Response record.
        """
        import re as _re

        fields = fields or []
        non_id_fields = [f for f in fields if f.get("name") != "id"]

        # Pluralise entity name for URL path (simple snake_case + 's')
        snake = _re.sub(r"([A-Z])", r"_\1", entity).lstrip("_").lower()
        url_path = snake + "s"

        # Use-case class names follow standard naming convention
        list_uc   = f"ListAll{entity}sUseCase"
        list_q    = f"ListAll{entity}sQuery"
        get_uc    = f"Get{entity}ByIdUseCase"
        get_q     = f"Get{entity}ByIdQuery"
        reg_uc    = f"Register{entity}UseCase"
        reg_cmd   = f"Register{entity}Command"
        upd_uc    = f"Update{entity}UseCase"
        upd_cmd   = f"Update{entity}Command"
        deact_uc  = f"Deactivate{entity}UseCase"
        deact_cmd = f"Deactivate{entity}Command"

        mod_prefix = f"{base_package}.{module}" if module else base_package

        uc_pkg = f"{mod_prefix}.application.usecase"
        dto_pkg = f"{mod_prefix}.application.dto"
        model_import = f"{mod_prefix}.domain.model.{entity}"
        page_result_import = f"{base_package}.shared.PageResult"
        page_response_import = f"{base_package}.shared.PageResponse"

        # Build toResponse() field mapping
        def _response_type(java_type: str) -> str:
            outer = java_type.split("<")[0]
            if outer in self._JDK_TYPES:
                if outer in ("LocalDate", "LocalDateTime", "Instant"):
                    return "String"
                return java_type
            if outer in self._VO_TYPE_MAP or outer in ("Money", "Price", "Amount"):
                return "Double"
            if outer.endswith("Id"):
                return "UUID"
            if any(outer.endswith(s) for s in ("Status", "Type", "Kind", "State", "Category", "Role")):
                return "String"
            return "String"

        def _getter_expr(f):
            fname = f["name"]
            method = fname[0].upper() + fname[1:]
            orig = f.get("type", "String")
            rtype = _response_type(orig)
            outer = orig.split("<")[0]
            g = f"e.get{method}()"
            if rtype == orig:
                # JDK type that stays as-is: LocalDate/LocalDateTime → toString()
                if outer in ("LocalDate", "LocalDateTime", "Instant"):
                    return f"{g} != null ? {g}.toString() : null"
                return g
            if rtype == "Double":
                if outer == "Money":
                    return f"{g} != null ? {g}.getAmount() : null"
                return f"{g} != null ? {g}.doubleValue() : null"
            if rtype == "String":
                # Temporal JDK types → toString()
                if outer in ("LocalDate", "LocalDateTime", "Instant"):
                    return f"{g} != null ? {g}.toString() : null"
                # VO wrapper → getValue()
                return f"{g} != null ? {g}.getValue() : null"
            if rtype == "UUID":
                return f"{g} != null ? {g}.value() : null"
            return g

        response_args = ["                e.getId().value()"]
        for f in non_id_fields:
            response_args.append(f"                {_getter_expr(f)}")
        response_args_str = ",\n".join(response_args)

        entity_var = entity[0].lower() + entity[1:]

        return f"""package {package_name};

import {model_import};
import {dto_pkg}.{entity}Response;
import {page_result_import};
import {page_response_import};
import {uc_pkg}.{list_uc};
import {uc_pkg}.{list_q};
import {uc_pkg}.{get_uc};
import {uc_pkg}.{get_q};
import {uc_pkg}.{reg_uc};
import {uc_pkg}.{reg_cmd};
import {uc_pkg}.{upd_uc};
import {uc_pkg}.{upd_cmd};
import {uc_pkg}.{deact_uc};
import {uc_pkg}.{deact_cmd};
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/{url_path}")
@CrossOrigin(origins = "*")
public class {class_name} {{

    private final {list_uc} listAll;
    private final {get_uc} getById;
    private final {reg_uc} register;
    private final {upd_uc} update;
    private final {deact_uc} deactivate;

    public {class_name}(
            {list_uc} listAll,
            {get_uc} getById,
            {reg_uc} register,
            {upd_uc} update,
            {deact_uc} deactivate) {{
        this.listAll    = listAll;
        this.getById    = getById;
        this.register   = register;
        this.update     = update;
        this.deactivate = deactivate;
    }}

    @GetMapping
    public PageResponse<{entity}Response> getAll(
            @RequestParam(defaultValue = "0")  int page,
            @RequestParam(defaultValue = "20") int size,
            @RequestParam(defaultValue = "")   String search) {{
        PageResult<{entity}> result = listAll.execute(new {list_q}(page, size, search));
        List<{entity}Response> content = result.content().stream()
                .map(this::toResponse).collect(Collectors.toList());
        return new PageResponse<>(content, result.page(), result.size(),
                result.total(), result.totalPages(), result.isLast());
    }}

    @GetMapping("/{{id}}")
    public ResponseEntity<{entity}Response> getOne(@PathVariable("id") UUID id) {{
        return getById.execute(new {get_q}(id))
                .map(this::toResponse)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }}

    @PostMapping
    public ResponseEntity<{entity}Response> create(@RequestBody {reg_cmd} cmd) {{
        return ResponseEntity.ok(toResponse(register.execute(cmd)));
    }}

    @PutMapping("/{{id}}")
    public ResponseEntity<{entity}Response> updateOne(@PathVariable("id") UUID id,
                                                       @RequestBody {upd_cmd} cmd) {{
        return ResponseEntity.ok(toResponse(update.execute(cmd)));
    }}

    @DeleteMapping("/{{id}}")
    public ResponseEntity<Void> deleteOne(@PathVariable("id") UUID id) {{
        deactivate.execute(new {deact_cmd}(id));
        return ResponseEntity.noContent().build();
    }}

    private {entity}Response toResponse({entity} e) {{
        return new {entity}Response(
{response_args_str}
        );
    }}
}}
"""