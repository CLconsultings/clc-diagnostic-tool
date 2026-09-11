# CLConsulting AI Impact + Readiness Diagnostic

A deterministic implementation of the CLConsulting AI Impact + Readiness assessment and Implementation Decision output.

## Governing behavior

- 25 statements across five dimensions, scored 1–5 (maximum 125).
- Scores diagnose; they do not independently authorize AI expansion or automation.
- Risk, evidence, weakest material constraint, sequence, and valid stop/hold conditions can override the total score.
- Service pathway remains **Measure / Optimize / Prove**.
- Decision state remains **Act / Test / Defer / Stop**.
- **Keep Human-Led** remains a separate workflow disposition.
- Missing baseline means impact/ROI remains unproven.
- Final output includes the implementation decision, owner, baseline, outcome measure, guardrail, review point, stop/revert condition, invalidation condition, and smallest responsible next action.

## Architecture

- `diagnostic/questions.py` — canonical assessment statements and dimensions.
- `diagnostic/model.py` — typed domain model and controlled vocabularies.
- `diagnostic/engine.py` — deterministic scoring, gates, routing, confidence, and decision logic.
- `streamlit_app.py` — client/internal assessment UI.
- `tests/test_engine.py` — fail-closed regression cases.

## Run

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Test

```bash
pytest -q
```

CI treats missing or failing tests as a release failure.

## Scope boundary

This diagnostic supports implementation decisions. It is not a legal, regulatory, security, compliance, or certification determination. Consequential agent/autonomy authorization requires its governing authority/containment controls and is not granted by an assessment score.
