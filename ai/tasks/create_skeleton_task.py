# ai/tasks/create_skeleton_task.py

def build_create_skeleton_task(path, name, base_package, **kwargs):
    return {
        "agent": "backend_builder",
        "description": f"""
        Generate ONLY the skeleton (empty signature) for the file '{path}'.
        
        SYNTAX RULES (Java 17):
        1. PACKAGE: Must match the directory structure under '{base_package}'.
        2. IMPORTS: Include only Shared Kernel imports: '{base_package}.domain.shared.*'.
        3. TYPE DEFINITION:
           - If ID: 'public record {name}(java.util.UUID value) implements ValueObject {{}}'
           - If Repository: 'public interface {name} extends EntityRepository<Entity, ValueObject> {{}}'
           - If Entity: 'public class {name} extends Entity<ValueObject> {{}}'
           - If Service: 'public class {name} {{}}'
        
        DO NOT write logic, methods, or fields. Only the header and empty braces.
        """,
        "expected_output": "Minimal Java code (file signature)."
    }