from pathlib import Path


class ArchitectureLogger:

    def log_tree(self, root: Path, output_file: Path):
        lines = []

        def walk(current: Path, prefix: str = ""):
            children = sorted(
                current.iterdir(),
                key=lambda p: (p.is_file(), p.name.lower())
            )

            for i, child in enumerate(children):
                is_last = i == len(children) - 1
                branch = "└── " if is_last else "├── "
                lines.append(f"{prefix}{branch}{child.name}")

                if child.is_dir():
                    extension = "    " if is_last else "│   "
                    walk(child, prefix + extension)

        lines.append(root.name)
        walk(root)

        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text("\n".join(lines), encoding="utf-8")