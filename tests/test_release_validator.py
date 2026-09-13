from scripts import validate_release


def test_engine_change_requires_higher_version(monkeypatch):
    monkeypatch.setattr(validate_release, "_base_version", lambda *_: "2.1.0")
    errors = []

    validate_release._validate_version_bump(
        errors,
        {"diagnostic/engine.py"},
        "## 2.1.0",
        "a" * 40,
        validate_release.ENGINE_PATHS,
        "ENGINE_VERSION",
        "2.1.0",
    )

    assert errors == [
        "ENGINE_VERSION must increase when governed behavior changes "
        "(base 2.1.0, proposed 2.1.0)."
    ]


def test_engine_change_requires_new_version_in_changelog(monkeypatch):
    monkeypatch.setattr(validate_release, "_base_version", lambda *_: "2.1.0")
    errors = []

    validate_release._validate_version_bump(
        errors,
        {"diagnostic/model.py"},
        "## Maintenance",
        "a" * 40,
        validate_release.ENGINE_PATHS,
        "ENGINE_VERSION",
        "2.2.0",
    )

    assert errors == [
        "CHANGELOG.md additions must record ENGINE_VERSION 2.2.0 "
        "when its governed behavior changes."
    ]


def test_valid_engine_version_bump_passes(monkeypatch):
    monkeypatch.setattr(validate_release, "_base_version", lambda *_: "2.1.0")
    errors = []

    validate_release._validate_version_bump(
        errors,
        {"streamlit_app.py"},
        "## 2.2.0 - 2026-09-11",
        "a" * 40,
        validate_release.ENGINE_PATHS,
        "ENGINE_VERSION",
        "2.2.0",
    )

    assert errors == []


def test_non_governed_change_does_not_require_version_bump(monkeypatch):
    def unexpected_base_lookup(*_):
        raise AssertionError("base version should not be read")

    monkeypatch.setattr(validate_release, "_base_version", unexpected_base_lookup)
    errors = []

    validate_release._validate_version_bump(
        errors,
        {"README.md"},
        "",
        "a" * 40,
        validate_release.ENGINE_PATHS,
        "ENGINE_VERSION",
        "2.1.0",
    )

    assert errors == []


def test_version_only_increase_is_rejected(monkeypatch):
    monkeypatch.setattr(validate_release, "_base_version", lambda *_: "2.1.0")
    errors = []

    validate_release._validate_version_bump(
        errors,
        {"diagnostic/version.py"},
        "## 2.2.0",
        "a" * 40,
        validate_release.ENGINE_PATHS,
        "ENGINE_VERSION",
        "2.2.0",
    )

    assert errors == [
        "ENGINE_VERSION may change only with its associated governed behavior "
        "(base 2.1.0, proposed 2.2.0)."
    ]


def test_version_only_regression_is_rejected(monkeypatch):
    monkeypatch.setattr(validate_release, "_base_version", lambda *_: "2.1.0")
    errors = []

    validate_release._validate_version_bump(
        errors,
        {"diagnostic/version.py"},
        "## 2.0.0",
        "a" * 40,
        validate_release.ENGINE_PATHS,
        "ENGINE_VERSION",
        "2.0.0",
    )

    assert errors == [
        "ENGINE_VERSION may change only with its associated governed behavior "
        "(base 2.1.0, proposed 2.0.0)."
    ]


def test_manifest_scope_boundary_must_match_approved_value():
    versions = {
        "INSTRUMENT_VERSION": "2.0.0",
        "ENGINE_VERSION": "2.1.0",
        "RELEASE_POLICY_VERSION": "1.0.0",
    }
    manifest = validate_release._manifest_expectations(versions)
    manifest["scope_boundary"] = "Consequential autonomy is authorized."
    errors = []

    validate_release._validate_manifest(errors, manifest, versions)

    assert errors == [
        "release_manifest.json 'scope_boundary' must equal "
        f"{validate_release.APPROVED_SCOPE_BOUNDARY!r}"
    ]


def test_version_module_is_parsed_without_executable_statements():
    source = '''
INSTRUMENT_VERSION = "2.0.0"
ENGINE_VERSION = "2.1.0"
RELEASE_POLICY_VERSION = "1.0.0"
raise SystemExit(0)
'''

    try:
        validate_release._parse_version_constants(source)
    except ValueError as exc:
        assert str(exc).startswith(
            "diagnostic/version.py may contain only literal assignments"
        )
    else:
        raise AssertionError("Executable version-module statements must be rejected")


def test_integrity_workflow_protects_validator_package_initializer():
    workflow = (
        validate_release.ROOT / ".github/workflows/governance-integrity.yml"
    ).read_text(encoding="utf-8")

    assert '"scripts/__init__.py"' in workflow


def test_release_validation_precedes_dependency_installation():
    workflow = (validate_release.ROOT / ".github/workflows/python-app.yml").read_text(
        encoding="utf-8"
    )

    validation = workflow.index("python -I -S scripts/validate_release.py")
    dependency_installation = workflow.index("python -m pip install --upgrade pip")

    assert validation < dependency_installation


def test_public_package_entrypoint_is_engine_governed():
    assert "diagnostic/__init__.py" in validate_release.ENGINE_PATHS


def test_manifest_release_identity_fields_must_match():
    versions = {
        "INSTRUMENT_VERSION": "2.0.0",
        "ENGINE_VERSION": "2.1.0",
        "RELEASE_POLICY_VERSION": "1.0.0",
    }
    approved = validate_release._manifest_expectations(versions)

    for field in ("schema_version", "system", "runtime"):
        manifest = dict(approved)
        manifest.pop(field)
        errors = []

        validate_release._validate_manifest(errors, manifest, versions)

        assert any(f"{field!r} must equal" in error for error in errors)


def test_unclassified_product_python_path_is_rejected():
    tracked = (
        validate_release.INSTRUMENT_PATHS
        | validate_release.ENGINE_PATHS
        | {validate_release.VERSION_FILE, "diagnostic/evaluator.py"}
    )

    assert validate_release._unclassified_product_python_paths(tracked) == {
        "diagnostic/evaluator.py"
    }


def test_every_governed_path_exists():
    governed = (
        validate_release.INSTRUMENT_PATHS
        | validate_release.ENGINE_PATHS
        | validate_release.POLICY_PATHS
    )

    assert all((validate_release.ROOT / path).is_file() for path in governed)


def test_workflow_runs_protected_regression_oracle():
    workflow = (validate_release.ROOT / ".github/workflows/python-app.yml").read_text(
        encoding="utf-8"
    )
    integrity = (
        validate_release.ROOT / ".github/workflows/governance-integrity.yml"
    ).read_text(encoding="utf-8")

    assert "python -I scripts/run_regression_oracle.py" in workflow
    assert '"scripts/run_regression_oracle.py"' in integrity
    assert '"tests/"' in integrity
