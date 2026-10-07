# Security Policy

## Scope

This repository implements the CLConsulting AI Impact + Readiness Diagnostic.

The assessment score is diagnostic evidence only. It does not authorize AI expansion, automation, legal/compliance conclusions, security certification, or consequential autonomous action.

## Security priorities

Review findings with emphasis on:

1. Input validation failures that could bypass the 1-5 scoring contract or required evidence fields.
2. Logic paths that could incorrectly return Act, Prove, or another higher-commitment state when a risk, evidence, contradiction, or stop condition should constrain the result.
3. Code execution, injection, path traversal, unsafe deserialization, dependency, or secret-exposure risks.
4. Streamlit-specific risks that could expose assessment data or permit unintended execution.
5. Changes that weaken fail-closed behavior, regression coverage, or release evidence.

## Release-blocking findings

- **Critical:** block release.
- **High:** block release unless explicitly accepted by the authorized CLConsulting release owner with documented rationale and containment.
- **Incomplete security scan:** does not count as a passed security review.
- **Missing or failing regression tests:** block release.

Medium and low findings require an owner and disposition before client-facing release when they are material to the diagnostic's trustworthiness.

## Data boundary

Do not commit client assessment data, API keys, secrets, credentials, or sensitive client artifacts to this repository.

Security reports may contain source code or vulnerability details. Treat generated reports as internal evidence unless explicitly approved for broader distribution.

## Reporting

For private reporting, use the repository owner's established internal channel. Do not open a public issue containing exploitable vulnerability details or client data.
