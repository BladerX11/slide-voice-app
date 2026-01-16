import subprocess
import sys

from utils import compile_resources  # pyright: ignore [reportImplicitRelativeImport]


def run_dev():
    """Runs the application."""
    try:
        compile_resources()
        _ = subprocess.run(["uv", "run", "-m", "slide_voice_app"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Running application failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_dev()
