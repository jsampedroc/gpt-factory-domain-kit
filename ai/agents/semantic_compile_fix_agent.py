# ------------------ Semantic Compile Fix Agent ------------------
class SemanticCompileFixAgent:
    """
    Handles semantic compile errors such as missing domain types.
    Example: 'cannot find symbol Address'.
    The agent can synthesize minimal ValueObject stubs so the
    compilation pipeline can proceed.
    """

    MISSING_SYMBOL_RE = re.compile(r"cannot find symbol\s+\n?\s*symbol:\s*class\s+([A-Za-z0-9_]+)", re.MULTILINE)

    def run(self, factory, compile_output):

        matches = self.MISSING_SYMBOL_RE.findall(compile_output)

        if not matches:
            return False

        created = False

        for symbol in matches:

            # ignore common java types
            if symbol in STANDARD_JAVA_TYPES:
                continue

            # check if type already exists
            expected_rel = f"domain/valueobject/{symbol}.java"
            target = factory.resolve_output_path(expected_rel)

            if target.exists():
                continue

            factory.log(f"🧠 Synthesizing missing ValueObject: {symbol}")

            code = (
                f"package {factory.base_package}.domain.valueobject;\n\n"
                "import java.util.Objects;\n"
                f"import {factory.base_package}.domain.shared.ValueObject;\n\n"
                f"public final class {symbol} implements ValueObject {{\n\n"
                "    private final String value;\n\n"
                f"    public {symbol}(String value) {{\n"
                "        this.value = Objects.requireNonNull(value);\n"
                "    }\n\n"
                "    public String getValue() {\n"
                "        return value;\n"
                "    }\n"
                "}\n"
            )

            factory.save_to_disk(expected_rel, code)
            created = True

        return created