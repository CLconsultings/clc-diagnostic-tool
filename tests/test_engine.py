import pytest

from diagnostic import AssessmentInput, EvidenceConfidence, evaluate
from diagnostic.model import DecisionState, ServicePathway, WorkflowDisposition
from diagnostic.questions import DIMENSIONS


def case(score=4, evidence=EvidenceConfidence.HIGH, **overrides):
    data = dict(
        responses={i: score for i in range(1, 26)},
        evidence_confidence={name: evidence for name in DIMENSIONS},
        priority_workflow="Client reporting",
        accountable_owner="Process owner",
        baseline="10 hours per cycle",
        primary_outcome_measure="Cycle time",
        quality_risk_guardrail="Error rate does not increase",
        review_point="30 days",
        stop_revert_condition="Error rate exceeds baseline",
        invalidation_condition="No measurable workflow improvement",
        priority_defined=True,
        risk_boundary_clear=True,
    )
    data.update(overrides)
    return AssessmentInput(**data)


def test_requires_all_25_responses():
    data = case()
    responses = dict(data.responses)
    responses.pop(25)
    with pytest.raises(ValueError):
        evaluate(AssessmentInput(**{**data.__dict__, "responses": responses}))


def test_high_score_does_not_override_unresolved_risk():
    result = evaluate(case(score=5, risk_boundary_clear=False))
    assert "Risk gate" in result.gates_triggered
    assert result.service_pathway == ServicePathway.MEASURE
    assert result.decision_state == DecisionState.DEFER


def test_missing_baseline_blocks_prove_and_roi_claim():
    result = evaluate(case(score=5, baseline=None))
    assert "Evidence gate" in result.gates_triggered
    assert result.service_pathway == ServicePathway.MEASURE
    assert any("ROI remains unproven" in gap for gap in result.unresolved_gaps)


def test_low_evidence_constrains_commitment():
    result = evaluate(case(score=5, evidence=EvidenceConfidence.LOW))
    assert result.recommendation_confidence == EvidenceConfidence.LOW
    assert result.decision_state == DecisionState.DEFER


def test_workflow_gate_routes_to_optimization_when_measure_prerequisites_exist():
    responses = {i: 4 for i in range(1, 26)}
    for i in range(6, 11):
        responses[i] = 2
    result = evaluate(case(responses=responses))
    assert "Workflow gate" in result.gates_triggered
    assert result.service_pathway == ServicePathway.OPTIMIZE


def test_prove_requires_high_thresholds_and_credible_evidence():
    result = evaluate(case(score=5))
    assert result.total_score == 125
    assert result.service_pathway == ServicePathway.PROVE
    assert result.decision_state == DecisionState.ACT


def test_medium_evidence_yields_bounded_test():
    result = evaluate(case(score=5, evidence=EvidenceConfidence.MEDIUM))
    assert result.recommendation_confidence == EvidenceConfidence.MEDIUM
    assert result.decision_state == DecisionState.TEST


def test_keep_human_led_stays_separate_from_pathway_and_state():
    result = evaluate(case(score=5, human_led_required=True))
    assert result.workflow_disposition == WorkflowDisposition.KEEP_HUMAN_LED
    assert result.service_pathway == ServicePathway.PROVE
    assert result.decision_state == DecisionState.ACT


def test_explicit_stop_is_respected_even_with_high_scores():
    result = evaluate(case(score=5, explicit_stop=True))
    assert result.decision_state == DecisionState.STOP


def test_contradiction_reduces_confidence():
    result = evaluate(case(score=5, material_contradictions=["Claimed impact conflicts with records"]))
    assert "Contradiction validation" in result.gates_triggered
    assert result.recommendation_confidence == EvidenceConfidence.LOW
    assert result.decision_state == DecisionState.DEFER


def test_boolean_response_is_rejected():
    data = case()
    responses = dict(data.responses)
    responses[1] = True
    with pytest.raises(ValueError):
        evaluate(AssessmentInput(**{**data.__dict__, "responses": responses}))


def test_low_measurement_evidence_gate_routes_to_measure():
    responses = {i: 5 for i in range(1, 26)}
    for i in range(21, 26):
        responses[i] = 2
    result = evaluate(case(responses=responses))
    assert "Evidence gate" in result.gates_triggered
    assert result.service_pathway == ServicePathway.MEASURE


def test_undefined_priority_routes_to_measure():
    result = evaluate(case(score=5, priority_workflow="", priority_defined=True))
    assert result.service_pathway == ServicePathway.MEASURE
    assert result.decision_state == DecisionState.TEST
    assert "Priority workflow is not bounded." in result.unresolved_gaps


def test_missing_decision_controls_fail_closed():
    result = evaluate(case(score=5, accountable_owner=""))
    assert "Decision controls gate" in result.gates_triggered
    assert result.service_pathway == ServicePathway.MEASURE
    assert result.decision_state == DecisionState.DEFER
    assert "Accountable owner is missing." in result.unresolved_gaps


def test_whitespace_baseline_triggers_evidence_gate():
    result = evaluate(case(score=5, baseline="   "))
    assert "Evidence gate" in result.gates_triggered
    assert result.service_pathway == ServicePathway.MEASURE


def test_uncontrolled_evidence_value_is_rejected():
    confidence = {name: EvidenceConfidence.HIGH for name in DIMENSIONS}
    confidence["Purpose and Alignment"] = "High"
    with pytest.raises(ValueError):
        evaluate(case(evidence_confidence=confidence))


def test_result_records_governing_versions():
    result = evaluate(case(score=5))
    assert result.instrument_version == "2.0.0"
    assert result.engine_version == "2.1.0"
    assert result.release_policy_version == "1.0.0"


def test_invalid_decision_control_types_are_rejected():
    with pytest.raises(ValueError):
        evaluate(case(accountable_owner=None))
    with pytest.raises(ValueError):
        evaluate(case(material_contradictions="not-a-list"))
