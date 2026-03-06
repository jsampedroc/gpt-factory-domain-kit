# ai/codegen/template_java_generator.py

class TemplateJavaGenerator:

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

        lines.append("\n}\n")

        return "".join(lines)

    def generate_repository(self, package_name, entity):

        return f"""
package {package_name};

import org.springframework.data.jpa.repository.JpaRepository;
import java.util.UUID;

public interface {entity}Repository extends JpaRepository<{entity}, UUID> {{

}}
"""

    def generate_service(self, package_name, class_name, entity, base_package):

        return f"""
package {package_name};

import {base_package}.domain.model.{entity};
import {base_package}.domain.repository.{entity}Repository;

public class {class_name} {{

    private final {entity}Repository repository;

    public {class_name}({entity}Repository repository) {{
        this.repository = repository;
    }}

}}
"""

    def generate_controller(self, package_name, class_name, entity, base_package):

        return f"""
package {package_name};

import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/{entity.lower()}s")
public class {class_name} {{

}}
"""