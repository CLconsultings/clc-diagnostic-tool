# CLConsulting Diagnostic Release Governance

| Control | Value |
| --- | --- |
| Policy version | 1.0.0 |
| Owner | CLConsulting |
| Status | Active when merged to `main` |
| Authorization | Automated gates |
| Required checks | `Governed release / release-gate`; `Governance integrity / immutable-controls` |

## Purpose

This policy controls changes to the assessment statements, scoring, thresholds,
gates, routing, controlled vocabularies, decision outputs, interface, and
release automation. It is designed to preserve decision integrity without a
heavy approval process.

## Release rule

A change is eligible for production only when all of the following are true:

1. The change reaches `main` through a pull request.
2. The exact pull-request head passes the required governed release check.
3. All review conversations are resolved.
4. The branch is current enough for GitHub to report it mergeable.
5. Governing versions and `release_manifest.json` agree.
6. The change preserves the scope boundary and proprietary license.

Passing automation authorizes routine product releases. There is no separate
human-approval gate for those releases. Failed, skipped, stale, or unavailable
checks do not authorize release.

## Automated gate

The single required gate performs:

- release-manifest and ownership validation;
- Python compilation and critical static checks;
- the complete regression suite;
- runtime dependency vulnerability auditing; and
- verification that the release-control files remain present and consistent.

The workflow uses read-only repository permissions, pinned first-party action
revisions, a time limit, and concurrency cancellation for superseded runs.

## Control-plane integrity

The integrity check runs from the trusted base branch using
`pull_request_target`; it does not check out or execute pull-request code. It
automatically rejects routine pull requests that change CODEOWNERS, either
required workflow, this policy, or the release validator. This prevents the
release gate from authorizing its own removal or weakening.

Changing the control plane requires an explicit governance re-bootstrap
authorized by the repository owner. The proposed controls must be reviewed and
verified before activation, then the required-check settings must be
re-established against the new trusted baseline. This is not an emergency
bypass and cannot authorize a product release in the same change.

## Change classification

- **Patch:** defect correction with no intended change to the assessment model.
- **Minor:** backward-compatible change to outputs, controls, or workflow.
- **Major:** change to questions, dimensions, scoring, thresholds, pathway
  semantics, decision states, or authority boundaries.

Any governed-behavior change must update the appropriate version in
`diagnostic/version.py`, `release_manifest.json`, and `CHANGELOG.md`.

## Evidence retained

GitHub is the release evidence record. Each release retains the pull-request
diff, exact head SHA, automated results, review history, merge commit, and
versioned manifest. Squash merge is the default so each release is one coherent
change set.

## Failure and rollback

- Do not merge a failed or stale release candidate.
- A defect found after release is corrected through a new pull request and the
  same gate; controls are not bypassed for urgency.
- Stop external use when a defect could materially change a decision outcome.
- Revert to the last verified release when containment is safer than a forward
  fix.
- Record the defect, affected versions, containment, correction, and evidence
  in the corrective pull request.

## Repository controls

`main` must block force pushes and deletion, require both status checks,
require resolved conversations, and reject direct changes that bypass the
pull-request path. The repository must remain private unless an explicit
CLConsulting IP decision supersedes this policy.

## Exceptions

There is no emergency product-release bypass. If GitHub or a required control
is unavailable, the release remains pending.
