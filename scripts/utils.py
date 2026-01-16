import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PKG_DIR = BASE_DIR / "src" / "slide_voice_app"


def compile_resources():
    """Runs the pyside6-rcc compiler via uv."""
    try:
        _ = subprocess.run(
            [
                "uv",
                "run",
                "pyside6-rcc",
                str(BASE_DIR / "resources.qrc"),
                "-o",
                str(PKG_DIR / "rc_resources.py"),
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error compiling resources: {e}")
        sys.exit(1)
