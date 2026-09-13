# Changelog

All governed releases are recorded here using semantic versioning.

## 2.1.0 - 2026-09-11

- Established automated release governance and a machine-readable manifest.
- Established release policy version 1.0.0.
- Replaced the inherited open-source license with a proprietary notice.
- Corrected repository ownership and separated runtime from test dependencies.
- Added release-control, regression, static-analysis, and dependency-audit gates.
- Added an independent base-branch gate that prevents routine changes from weakening the control plane.
- Protected control-file renames, all workflow definitions, and the exact proprietary license.
- Enforced semantic version and changelog updates for governed behavior changes.
- Made large pull requests fail closed when GitHub cannot return a complete file inventory.
- Bound release evidence to the exact pull-request head SHA.
- Protected the validator package initializer and parsed version declarations without execution.
- Enforced the approved diagnostic scope boundary in the release manifest.
- Moved isolated release validation ahead of pull-request dependency installation.
- Added the diagnostic package entry point to engine version controls.
- Added governing versions to every assessment result.
- Made decision controls and interface defaults fail closed.

## 2.0.1 - 2026-09-11

- Rejected malformed Boolean scores.
- Routed Evidence gate failures to Measure.
- Derived workflow-definition state from bounded input in the interface.

## 2.0.0 - 2026-09-11

- Rebuilt the diagnostic around the governed 25-question, five-dimension model.
