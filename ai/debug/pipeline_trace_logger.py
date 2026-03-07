

import json
from pathlib import Path
from datetime import datetime


class PipelineTraceLogger:
    """
    Lightweight pipeline tracing utility for the AI software factory.

    Writes structured checkpoints during the pipeline execution so we can
    diagnose where generation errors start (domain model, inventory,
    code generation, imports, etc).
    """

    def __init__(self, output_root: Path):
        self.output_root = Path(output_root)
        self.trace_file = self.output_root / "pipeline_trace.log"

        # ensure directory exists
        self.trace_file.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------
    def log_step(self, step: str, payload=None):
        """
        Write a pipeline checkpoint.
        """
        try:
            with open(self.trace_file, "a", encoding="utf-8") as f:

                f.write("\n")
                f.write("=" * 60 + "\n")
                f.write(f"STEP: {step}\n")
                f.write(f"TIME: {datetime.now().isoformat()}\n")
                f.write("=" * 60 + "\n")

                if payload is not None:
                    try:
                        f.write(json.dumps(payload, indent=2, default=str))
                    except Exception:
                        f.write(str(payload))

                f.write("\n")

        except Exception:
            # tracing must never break the pipeline
            pass

    # ------------------------------------------------
    def log_message(self, message: str):
        """
        Write a simple message line.
        """
        try:
            with open(self.trace_file, "a", encoding="utf-8") as f:
                ts = datetime.now().strftime("%H:%M:%S")
                f.write(f"[{ts}] {message}\n")
        except Exception:
            pass

    # ------------------------------------------------
    def log_generated_files(self, root_path: Path):
        """
        Record all generated Java files to help debug path issues.
        """
        try:
            root_path = Path(root_path)
            files = []

            if root_path.exists():
                for p in root_path.rglob("*.java"):
                    try:
                        files.append(str(p.relative_to(root_path)))
                    except Exception:
                        files.append(str(p))

            self.log_step("GENERATED_FILES", files)

        except Exception:
            pass

    # ------------------------------------------------
    def log_inventory(self, inventory):
        """
        Specialized helper for inventory logging.
        """
        try:
            summary = {
                "files": len(inventory),
                "sample": inventory[:20] if isinstance(inventory, list) else inventory
            }

            self.log_step("INVENTORY", summary)
        except Exception:
            pass