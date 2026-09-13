"""Run the immutable release regressions without repository pytest configuration."""

import os
import sys
from pathlib import Path

os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
os.environ.pop("PYTEST_ADDOPTS", None)

import pytest


ROOT = Path(__file__).resolve().parents[1]
TRUSTED_TESTS = (
    ROOT / "tests/test_engine.py",
    ROOT / "tests/test_release_validator.py",
)


def main() -> None:
    sys.path.insert(0, str(ROOT))
    arguments = [
        "-q",
        "--noconftest",
        "-c",
        os.devnull,
        f"--rootdir={ROOT}",
        *(str(path) for path in TRUSTED_TESTS),
    ]
    raise SystemExit(pytest.main(arguments))


if __name__ == "__main__":
    main()
