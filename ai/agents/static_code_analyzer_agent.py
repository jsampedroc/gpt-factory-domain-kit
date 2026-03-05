import re
from pathlib import Path


class StaticCodeAnalyzerAgent:
    """
    Performs lightweight static analysis before compilation.
    Detects common code generation issues and auto-fixes simple cases.
    """

    def run(self, factory):

        base = factory.output_root / "backend/src/main/java"

        if not base.exists():
            return

        factory.log("🔍 StaticCodeAnalyzer scanning generated code")

        for file in base.rglob("*.java"):

            try:
                code = file.read_text()

                code = self._fix_dayofweek_import(code)
                code = self._fix_repository_save_signature(code)

                file.write_text(code)

            except Exception as e:
                factory.log(f"⚠️ Analyzer skipped {file.name}: {e}")

    def _fix_dayofweek_import(self, code):

        if "DayOfWeek" in code and "java.time.DayOfWeek" not in code:
            if "domain.shared.DayOfWeek" in code:
                code = code.replace(
                    "import com.preschoolmanagement.domain.shared.DayOfWeek;",
                    "import java.time.DayOfWeek;"
                )

        return code

    def _fix_repository_save_signature(self, code):

        pattern = r"void save\((.*?)\)"

        if re.search(pattern, code):
            code = re.sub(pattern, r"\1 save(\1)", code)

        return code