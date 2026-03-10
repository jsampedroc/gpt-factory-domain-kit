from pathlib import Path


class DeterministicSkeletonBuilder:
    """
    Generates deterministic Java class skeletons BEFORE AI writes code.
    This prevents broken imports and missing types.
    """

    def __init__(self, factory):
        self.factory = factory

    def build(self, inventory):
        for item in inventory:

            path = item["path"]
            class_name = Path(path).stem
            entity = item.get("entity")
            desc = item["description"]

            output_path = self.factory.resolve_output_path(path)

            if output_path.exists():
                continue

            pkg = self.factory._expected_package_for(path)

            code = self._generate_skeleton(pkg, class_name, desc)

            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(code)

    def _generate_skeleton(self, pkg, class_name, desc):

        if desc == "Entity":
            return f"""package {pkg};

public class {class_name} {{

    // fields will be injected by code generation

}}
"""

        if desc == "ID Record":
            return f"""package {pkg};

public record {class_name}(java.util.UUID value) {{

}}
"""

        if desc == "Repository Interface":
            return f"""package {pkg};

public interface {class_name}Repository {{

}}
"""

        if desc == "Service":
            return f"""package {pkg};

public class {class_name}Service {{

}}
"""

        if desc == "Controller":
            return f"""package {pkg};

public class {class_name}Controller {{

}}
"""

        if desc == "JPA_ENTITY":
            return f"""package {pkg};

import jakarta.persistence.Entity;
import jakarta.persistence.Table;
import jakarta.persistence.Id;
import jakarta.persistence.Column;
import java.util.UUID;

@Entity
@Table(name = "{class_name.replace('JpaEntity','').lower()}s")
public class {class_name} {{

    @Id
    @Column(name = "id", nullable = false)
    private UUID id;

}}
"""

        return f"""package {pkg};

public class {class_name} {{

}}
"""