import json
from pathlib import Path

from diagnostic.version import ENGINE_VERSION, INSTRUMENT_VERSION, RELEASE_POLICY_VERSION


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    errors = []
    required_paths = [
        "LICENSE",
        "RELEASE_GOVERNANCE.md",
        "SECURITY.md",
        "CHANGELOG.md",
        "release_manifest.json",
        ".github/CODEOWNERS",
        ".github/dependabot.yml",
        ".github/pull_request_template.md",
        ".github/workflows/python-app.yml",
    ]
    for relative_path in required_paths:
        if not (ROOT / relative_path).is_file():
            errors.append(f"Required release-control file is missing: {relative_path}")

    manifest = json.loads((ROOT / "release_manifest.json").read_text(encoding="utf-8"))
    expected = {
        "owner": "CLConsulting",
        "license": "Proprietary",
        "decision_authority": "automated-gates",
        "policy_version": RELEASE_POLICY_VERSION,
        "instrument_version": INSTRUMENT_VERSION,
        "engine_version": ENGINE_VERSION,
        "required_check": "Governed release / release-gate",
    }
    for key, expected_value in expected.items():
        if manifest.get(key) != expected_value:
            errors.append(f"release_manifest.json {key!r} must equal {expected_value!r}")

    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    if "CLCONSULTING PROPRIETARY LICENSE" not in license_text or "Apache License" in license_text:
        errors.append("LICENSE must contain only the CLConsulting proprietary notice.")

    owners = (ROOT / ".github/CODEOWNERS").read_text(encoding="utf-8").strip()
    if owners != "* @CLconsultings":
        errors.append("CODEOWNERS must assign repository ownership to @CLconsultings.")

    runtime_requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8").lower()
    for development_dependency in ("pytest", "flake8", "pip-audit"):
        if development_dependency in runtime_requirements:
            errors.append(f"Development dependency found in runtime requirements: {development_dependency}")

    workflow = (ROOT / ".github/workflows/python-app.yml").read_text(encoding="utf-8")
    for required_command in (
        "python -m scripts.validate_release",
        "python -m pytest -q",
        "python -m pip_audit -r requirements.txt",
    ):
        if required_command not in workflow:
            errors.append(f"Required workflow command is missing: {required_command}")

    if errors:
        raise SystemExit("Release governance validation failed:\n- " + "\n- ".join(errors))

    print(
        "Release governance validated: "
        f"policy {RELEASE_POLICY_VERSION}, instrument {INSTRUMENT_VERSION}, engine {ENGINE_VERSION}."
    )


if __name__ == "__main__":
    main()
