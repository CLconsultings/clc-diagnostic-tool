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
