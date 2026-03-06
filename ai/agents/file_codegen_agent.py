from pathlib import Path
import json
import hashlib

from ai.codegen.import_resolver import resolve_imports
from ai.validators.code_verifier import verify_java_code
from ai.validators.code_auto_fix import auto_fix_java_code


class FileCodeGenerationAgent:

    def __init__(self, factory):
        self.factory = factory

    def generate(self, item, index, total):

        f = self.factory

        rel_path = item["path"]
        file_name = Path(rel_path).name

        output_path = f.resolve_output_path(rel_path)

        domain_graph = getattr(f.state, "domain_graph", {})
        semantic_graph = getattr(f.state, "semantic_code_graph", {})
        task_graph = getattr(f.state, "task_graph", [])

        deps = []
        for t in task_graph:
            if isinstance(t, dict) and t.get("path") == rel_path:
                deps = t.get("depends_on", []) or []
                break

        parts = rel_path.split("/")
        layer = parts[0] if len(parts) > 0 else None
        module = parts[1] if len(parts) > 1 else None

        context_payload = json.dumps({
            "name": item["entity"],
            "kind": item["description"],
            "fields": item.get("fields", []),
            "values": item.get("values", []),
            "path": rel_path,
            "layer": layer,
            "module": module,
            "base_package": f.base_package,
            "expected_package": f._expected_package_for(rel_path),
            "domain_relations": domain_graph.get(item["entity"], []),
            "semantic_relations": semantic_graph.get(item["entity"], []),
            "task_dependencies": deps,
        }, sort_keys=True)

        model = getattr(f.executor, "model_name", "unknown")

        signature_raw = rel_path + context_payload + model
        signature = hashlib.sha256(signature_raw.encode()).hexdigest()

        prev_sig = f.state.signatures.get(rel_path)

        if prev_sig and prev_sig == signature and output_path.exists():
            f.log(f"⏭️ Incremental skip {file_name}")
            return

        f.log(f"[{index}/{total}] Fabricating {file_name}")

        expected_pkg = f._expected_package_for(rel_path)

        code = f.executor.run_task(
            "write_code",
            path=rel_path,
            base_package=f.base_package,
            context_data=context_payload,
        )

        verification = verify_java_code(code)

        if not verification["valid"]:
            f.log(f"⚠️ Verification issues in {file_name}")
            code = auto_fix_java_code(code, verification["issues"])

        try:
            code = resolve_imports(code)
        except Exception:
            pass

        f.save_to_disk(rel_path, code)

        f.state.signatures[rel_path] = signature