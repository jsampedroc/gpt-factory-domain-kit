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

            path = item.get("path")
            if not path:
                # skip malformed items
                continue

            class_name = Path(path).stem
            entity = item.get("entity")

            # Normalize description/type coming from different builders
            raw_desc = item.get("description") or item.get("type") or ""
            desc = str(raw_desc).upper()

            output_path = self.factory.resolve_output_path(path)

            if output_path.exists():
                continue

            pkg = self.factory._expected_package_for(path)

            code = self._generate_skeleton(pkg, class_name, desc)

            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(code)

    def _generate_skeleton(self, pkg, class_name, desc):

        if desc == "ENTITY":
            return f"""package {pkg};

public class {class_name} {{

    // fields will be injected by code generation

}}
"""

        if desc == "VALUEOBJECT":
            return f"""package {pkg};

public class {class_name} {{

    // value object fields will be injected by code generation

}}
"""

        if desc == "ID RECORD":
            return f"""package {pkg};

public record {class_name}(java.util.UUID value) {{

}}
"""

        if desc == "REPOSITORY INTERFACE":
            return f"""package {pkg};

public interface {class_name} {{

}}
"""

        if desc in {"SERVICE", "DOMAIN SERVICE"}:
            return f"""package {pkg};

public class {class_name}Service {{

}}
"""

        if desc == "CONTROLLER":
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

    public {class_name}() {{}}

    public UUID getId() {{
        return id;
    }}

    public void setId(UUID id) {{
        this.id = id;
    }}

}}
"""

        return f"""package {pkg};

public class {class_name} {{

}}
"""