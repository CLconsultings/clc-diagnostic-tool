# CLConsulting Assurance Pilot — CLC Diagnostic Tool

Date: 2026-10-07
Status: Internal validation
Pilot target: CLConsulting AI Impact + Readiness Diagnostic

## Why this repository was selected

The diagnostic is a real CLConsulting client-facing decision-support workflow with deterministic scoring, evidence gates, decision states, and existing regression tests. It is therefore a useful test of whether newly identified public OpenAI components improve control quality without adding unnecessary complexity.

## Applicability decision

### OpenAI Guardrails — NOT APPLICABLE to current engine

The current diagnostic does not call an LLM. Its decision logic is deterministic Python.

Adding LLM input/output guardrails to the scoring engine would increase dependencies and failure modes without controlling an existing model risk.

Re-evaluate only if a future feature introduces model-generated interpretation, recommendations, narrative summaries, or free-text analysis.

### OpenAI Agents SDK — NOT APPLICABLE to current engine

The diagnostic does not require agent orchestration or tool use.

Do not introduce the Agents SDK unless the product later gains multi-step model/tool execution that cannot be handled more simply.

### Deterministic regression testing — ALREADY APPLICABLE AND ACTIVE

The repository already contains fail-closed pytest coverage for:
- unresolved risk overriding high scores;
- missing baselines blocking Prove/ROI claims;
- low evidence constraining commitment;
- explicit Stop behavior;
- contradiction-driven confidence reduction;
- response validation;
- evidence and workflow gates;
- bounded-test routing.

This is the correct control pattern for the current architecture.

### Codex Security — APPLICABLE

Security review adds a distinct control not currently covered by deterministic business-logic tests.

Initial integration uses a pinned GitHub Action in dry-run mode. This validates configuration without an API key or model call.

The dry-run is not a vulnerability scan and must not be represented as one.

## Promotion criteria for live Codex Security scanning

Do not make live scanning a required release check until all of the following are true:

1. The pinned Action commit has been reviewed and intentionally approved.
2. `CODEX_SECURITY_API_KEY` is stored as a repository secret.
3. A first repository scan completes successfully.
4. Coverage is complete; incomplete scans do not count as passed.
5. False positives and operational cost are reviewed.
6. High and critical severity policy is confirmed.
7. The release owner approves making the scan blocking.

## Intended live policy after validation

- PR diff scan for same-repository trusted branches.
- High and critical findings block merge when the scan is complete.
- Incomplete scans remain HOLD / not evaluated.
- Existing pytest CI remains independently required.
- Security findings do not replace CLConsulting's release decision or human review.

## Pilot conclusion

The strongest implementation decision from this test is selective adoption:

- Guardrails: **hold / not applicable**
- Agents SDK: **hold / not applicable**
- Deterministic regression testing: **retain and strengthen**
- Codex Security: **pilot**

This avoids adopting new components merely because they are available and preserves the simpler deterministic architecture where it is already the safer design.
