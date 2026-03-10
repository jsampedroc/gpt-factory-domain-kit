class TemplateJavaGenerator:

    def generate_jpa_entity(self, package_name, class_name, fields):

        lines = []

        lines.append(f"package {package_name};\n\n")

        lines.append("import jakarta.persistence.*;\n")
        lines.append("import java.util.UUID;\n")

        # Domain imports are resolved later by the central ImportResolver
        # to avoid duplicate or incorrect imports.

        lines.append("\n")

        lines.append("@Entity\n")
        
        lines.append(f"public class {class_name} {{\n\n")

        lines.append("    @Id\n")
        lines.append("    @GeneratedValue\n")
        lines.append("    private UUID id;\n\n")

        for f in fields:
            name = f.get("name")
            type_ = f.get("type")

            if name == "id":
                continue

            lines.append(f"    private {type_} {name};\n")

        # constructor
        lines.append("\n    public " + class_name + "() {}\n")

        # getters
        for f in fields:
            name = f.get("name")
            type_ = f.get("type")

            if name == "id":
                continue

            method = name[0].upper() + name[1:]
            lines.append(f"\n    public {type_} get{method}() {{ return this.{name}; }}\n")

        lines.append("\n}\n")

        return "".join(lines)

    def generate_repository(self, package_name, entity, base_package=None, module=None):

        if module:
            model_import = f"{base_package}.{module}.domain.model.{entity}"
            id_import = f"{base_package}.{module}.domain.valueobject.{entity}Id"
        else:
            model_import = f"{base_package}.domain.model.{entity}"
            id_import = f"{base_package}.domain.valueobject.{entity}Id"

        return f"""
package {package_name};

import {model_import};
import {id_import};
import java.util.Optional;

public interface {entity}Repository {{

    {entity} save({entity} entity);

    Optional<{entity}> findById({entity}Id id);

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

    def generate_controller(self, package_name, class_name, entity, base_package, module=None):

        if module:
            service_import = f"{base_package}.{module}.application.service.{entity}Service"
        else:
            service_import = f"{base_package}.application.service.{entity}Service"

        return f"""
package {package_name};

import {service_import};
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/{entity.lower()}s")
public class {class_name} {{

    private final {entity}Service service;

    public {class_name}({entity}Service service) {{
        this.service = service;
    }}

}}
"""