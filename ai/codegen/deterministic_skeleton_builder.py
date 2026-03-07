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
            entity = item["entity"]
            desc = item["description"]

            output_path = self.factory.resolve_output_path(path)

            if output_path.exists():
                continue

            pkg = self.factory._expected_package_for(path)

            code = self._generate_skeleton(pkg, entity, desc)

            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(code)

    def _generate_skeleton(self, pkg, entity, desc):

        if desc == "Entity":
            return f"""package {pkg};

public class {entity} {{

}}
"""

        if desc == "ID Record":
            return f"""package {pkg};

public record {entity}Id(java.util.UUID value) {{

}}
"""

        if desc == "Repository Interface":
            return f"""package {pkg};

public interface {entity}Repository {{

}}
"""

        if desc == "Service":
            return f"""package {pkg};

public class {entity}Service {{

}}
"""

        if desc == "Controller":
            return f"""package {pkg};

public class {entity}Controller {{

}}
"""

        if desc == "JPA_ENTITY":
            return f"""package {pkg};

import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import java.util.UUID;

@Entity
public class {entity}JpaEntity {{

    @Id
    private UUID id;

}}
"""

        return f"""package {pkg};

public class {entity} {{

}}
"""