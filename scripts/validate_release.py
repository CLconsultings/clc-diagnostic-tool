import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

from diagnostic.version import ENGINE_VERSION, INSTRUMENT_VERSION, RELEASE_POLICY_VERSION


ROOT = Path(__file__).resolve().parents[1]
APPROVED_LICENSE_SHA256 = "69e3dcd11a42936c6d92ce2cca97dad3af223dbbc67dab047bfb7b274529a759"
INSTRUMENT_PATHS = {"diagnostic/questions.py"}
ENGINE_PATHS = {
    "diagnostic/engine.py",
    "diagnostic/model.py",
    "streamlit_app.py",
}


def _semver(value: str) -> tuple[int, int, int]:
    if not re.fullmatch(r"\d+\.\d+\.\d+", value):
        raise ValueError(f"Invalid semantic version: {value!r}")
    return tuple(int(part) for part in value.split("."))


def _base_version(base_sha: str, constant: str) -> str | None:
    result = subprocess.run(
        ["git", "show", f"{base_sha}:diagnostic/version.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    match = re.search(
        rf'^\s*{re.escape(constant)}\s*=\s*["\']([^"\']+)["\']\s*$',
        result.stdout,
        re.MULTILINE,
    )
    return match.group(1) if match else None


def _pull_request_changes(base_sha: str) -> tuple[set[str], str]:
    changed = subprocess.run(
        ["git", "diff", "--no-renames", "--name-only", f"{base_sha}...HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    changelog_diff = subprocess.run(
        ["git", "diff", "--unified=0", f"{base_sha}...HEAD", "--", "CHANGELOG.md"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    added_changelog = "\n".join(
        line[1:]
        for line in changelog_diff.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    )
    return set(changed.splitlines()), added_changelog


def _validate_version_bump(
    errors: list[str],
    changed_paths: set[str],
    added_changelog: str,
    base_sha: str,
    governed_paths: set[str],
    constant: str,
    current_version: str,
) -> None:
    if not (changed_paths & governed_paths):
        return

    try:
        current = _semver(current_version)
    except ValueError as exc:
        errors.append(str(exc))
        return

    previous_version = _base_version(base_sha, constant)
    if previous_version is not None:
        try:
            if current <= _semver(previous_version):
                errors.append(
                    f"{constant} must increase when governed behavior changes "
                    f"(base {previous_version}, proposed {current_version})."
                )
        except ValueError as exc:
            errors.append(f"Base {exc}")

    if not re.search(rf"(?<!\d){re.escape(current_version)}(?!\d)", added_changelog):
        errors.append(
            f"CHANGELOG.md additions must record {constant} {current_version} "
            "when its governed behavior changes."
        )


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
        ".github/workflows/governance-integrity.yml",
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
        "required_checks": [
            "Governed release / release-gate",
            "Governance integrity / immutable-controls",
        ],
        "version_controls": {
            "instrument": sorted(INSTRUMENT_PATHS),
            "engine": sorted(ENGINE_PATHS),
        },
    }
    for key, expected_value in expected.items():
        if manifest.get(key) != expected_value:
            errors.append(f"release_manifest.json {key!r} must equal {expected_value!r}")

    license_digest = hashlib.sha256((ROOT / "LICENSE").read_bytes()).hexdigest()
    if license_digest != APPROVED_LICENSE_SHA256:
        errors.append("LICENSE must exactly match the approved CLConsulting proprietary notice.")

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

    integrity_workflow = (ROOT / ".github/workflows/governance-integrity.yml").read_text(encoding="utf-8")
    for protected_control in (
        "pull_request_target",
        ".github/CODEOWNERS",
        ".github/workflows/",
        "file.previous_filename",
        "LICENSE",
        "RELEASE_GOVERNANCE.md",
        "scripts/validate_release.py",
    ):
        if protected_control not in integrity_workflow:
            errors.append(f"Governance integrity control is missing: {protected_control}")

    if os.environ.get("GITHUB_EVENT_NAME") == "pull_request":
        base_sha = os.environ.get("GOVERNANCE_BASE_SHA", "").strip()
        if not re.fullmatch(r"[0-9a-fA-F]{40}", base_sha):
            errors.append("GOVERNANCE_BASE_SHA must identify the exact pull-request base commit.")
        else:
            try:
                changed_paths, added_changelog = _pull_request_changes(base_sha)
                _validate_version_bump(
                    errors,
                    changed_paths,
                    added_changelog,
                    base_sha,
                    INSTRUMENT_PATHS,
                    "INSTRUMENT_VERSION",
                    INSTRUMENT_VERSION,
                )
                _validate_version_bump(
                    errors,
                    changed_paths,
                    added_changelog,
                    base_sha,
                    ENGINE_PATHS,
                    "ENGINE_VERSION",
                    ENGINE_VERSION,
                )
            except subprocess.CalledProcessError as exc:
                errors.append(f"Unable to compare the pull request with its base: {exc}")

    if errors:
        raise SystemExit("Release governance validation failed:\n- " + "\n- ".join(errors))

    print(
        "Release governance validated: "
        f"policy {RELEASE_POLICY_VERSION}, instrument {INSTRUMENT_VERSION}, engine {ENGINE_VERSION}."
    )


if __name__ == "__main__":
    main()
