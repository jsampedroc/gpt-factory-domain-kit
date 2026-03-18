import os
import subprocess

OUTPUTS_DIR = "outputs"
RUNNER_PATH = os.path.abspath("ai-runner/runner.py")


def run_project(project_path):
    print(f"🚀 Running: {project_path}")

    subprocess.run(
        ["uv", "run", RUNNER_PATH],
        cwd=project_path
    )


def run_all():
    for project in os.listdir(OUTPUTS_DIR):
        path = os.path.join(OUTPUTS_DIR, project)

        if os.path.isdir(path):
            run_project(path)


if __name__ == "__main__":
    run_all()