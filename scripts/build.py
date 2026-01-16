import subprocess
import sys

from utils import BASE_DIR, PKG_DIR, compile_resources  # pyright: ignore [reportImplicitRelativeImport]


def run_build():
    """Builds the application using Nuitka."""
    compile_resources()

    try:
        _ = subprocess.run(
            [
                "uv",
                "run",
                "python",
                "-m",
                "nuitka",
                "--enable-plugin=pyside6",
                "--include-qt-plugins=qml",
                "--output-filename=slide-voice-app",
                "--standalone",
                f"--output-dir={BASE_DIR / 'dist'}",
                PKG_DIR,
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"Nuitka build failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_build()
