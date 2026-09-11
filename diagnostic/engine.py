from typing import Dict, List

from .model import (
    AssessmentInput,
    AssessmentResult,
    DecisionState,
    EvidenceConfidence,
    ServicePathway,
    WorkflowDisposition,
)
from .questions import DIMENSIONS
from .version import ENGINE_VERSION, INSTRUMENT_VERSION, RELEASE_POLICY_VERSION


CONFIDENCE_RANK = {
    EvidenceConfidence.LOW: 0,
    EvidenceConfidence.MEDIUM: 1,
    EvidenceConfidence.HIGH: 2,
}

PLACEHOLDER_VALUES = {
    "not yet assigned",
    "not yet bounded",
    "not yet defined",
    "not established",
}


def _is_blank(value: str | None) -> bool:
    return value is None or not value.strip() or value.strip().lower() in PLACEHOLDER_VALUES


def _priority_is_defined(data: AssessmentInput) -> bool:
    return data.priority_defined and not _is_blank(data.priority_workflow)


def _missing_decision_controls(data: AssessmentInput) -> List[str]:
    fields = {
        "Accountable owner": data.accountable_owner,
        "Primary outcome measure": data.primary_outcome_measure,
        "Quality/risk guardrail": data.quality_risk_guardrail,
        "Review point": data.review_point,
        "Stop/revert condition": data.stop_revert_condition,
        "Invalidation condition": data.invalidation_condition,
    }
    return [label for label, value in fields.items() if _is_blank(value)]


def _validate(data: AssessmentInput) -> None:
    if set(data.responses) != set(range(1, 26)):
        raise ValueError("Exactly 25 responses numbered 1 through 25 are required.")
    if any(isinstance(score, bool) or not isinstance(score, int) or score not in range(1, 6) for score in data.responses.values()):
        raise ValueError("Every assessment response must be an integer from 1 through 5.")
    expected_dimensions = set(DIMENSIONS)
    supplied_dimensions = set(data.evidence_confidence)
    if supplied_dimensions != expected_dimensions:
        missing = sorted(expected_dimensions - supplied_dimensions)
        unexpected = sorted(supplied_dimensions - expected_dimensions)
        raise ValueError(f"Evidence confidence dimensions are invalid. Missing: {missing}; unexpected: {unexpected}")
    if any(not isinstance(value, EvidenceConfidence) for value in data.evidence_confidence.values()):
        raise ValueError("Every evidence confidence value must use the controlled EvidenceConfidence vocabulary.")
    text_fields = (
        data.priority_workflow,
        data.accountable_owner,
        data.primary_outcome_measure,
        data.quality_risk_guardrail,
        data.review_point,
        data.stop_revert_condition,
        data.invalidation_condition,
    )
    if any(not isinstance(value, str) for value in text_fields):
        raise ValueError("Decision-control text fields must be strings.")
    if data.baseline is not None and not isinstance(data.baseline, str):
        raise ValueError("Baseline must be text or None.")
    if not isinstance(data.material_contradictions, list) or any(
        not isinstance(value, str) for value in data.material_contradictions
    ):
        raise ValueError("Material contradictions must be a list of strings.")
    flags = (
        data.priority_defined,
        data.risk_boundary_clear,
        data.human_led_required,
        data.explicit_stop,
    )
    if any(not isinstance(flag, bool) for flag in flags):
        raise ValueError("Decision-control flags must be booleans.")


def _scores(responses: Dict[int, int]) -> Dict[str, int]:
    return {name: sum(responses[q] for q in questions) for name, questions in DIMENSIONS.items()}


def _overall_evidence(confidence: Dict[str, EvidenceConfidence]) -> EvidenceConfidence:
    # Conservative aggregation: the weakest material evidence level controls the overall label.
    return min(confidence.values(), key=lambda item: CONFIDENCE_RANK[item])


def _maturity_band(total: int) -> str:
    if total >= 105:
        return "Embedded and measurable"
    if total >= 80:
        return "Developing maturity"
    if total >= 55:
        return "Fragmented use"
    return "Early-stage use"


def _gates(data: AssessmentInput, scores: Dict[str, int]) -> List[str]:
    gates: List[str] = []
    if scores["Risk and Responsible Use"] <= 14 or not data.risk_boundary_clear:
        gates.append("Risk gate")
    if scores["Workflow Integration"] <= 14:
        gates.append("Workflow gate")
    if scores["Impact and Measurement"] <= 14 or _is_blank(data.baseline):
        gates.append("Evidence gate")
    if _missing_decision_controls(data):
        gates.append("Decision controls gate")
    if any(score < 18 for score in scores.values()):
        gates.append("Maturity ceiling")
    if data.material_contradictions:
        gates.append("Contradiction validation")
    return gates


def _limiting_condition(data: AssessmentInput, scores: Dict[str, int], gates: List[str]) -> str:
    if "Risk gate" in gates:
        return "Risk/control"
    if "Evidence gate" in gates:
        return "Evidence/measurement"
    if not _priority_is_defined(data) or scores["Purpose and Alignment"] <= 14:
        return "Purpose"
    if "Decision controls gate" in gates:
        return "Decision controls"
    weakest = min(scores, key=scores.get)
    return {
        "Purpose and Alignment": "Purpose",
        "Workflow Integration": "Workflow",
        "Skill and Judgment": "Skill/judgment",
        "Risk and Responsible Use": "Risk/control",
        "Impact and Measurement": "Evidence/measurement",
    }[weakest]


def _pathway(data: AssessmentInput, scores: Dict[str, int], total: int, gates: List[str]) -> ServicePathway:
    # Governing v2.0 routing: risk/evidence/priority and low totals route to Measure first.
    if (
        total < 80
        or scores["Purpose and Alignment"] <= 14
        or not _priority_is_defined(data)
        or _is_blank(data.baseline)
        or "Evidence gate" in gates
        or "Risk gate" in gates
        or "Decision controls gate" in gates
    ):
        return ServicePathway.MEASURE

    # Prove requires the explicit v2.0 thresholds and credible evidence.
    evidence = _overall_evidence(data.evidence_confidence)
    if (
        total >= 105
        and scores["Workflow Integration"] >= 20
        and scores["Risk and Responsible Use"] >= 20
        and scores["Impact and Measurement"] >= 20
        and evidence != EvidenceConfidence.LOW
        and not data.material_contradictions
    ):
        return ServicePathway.PROVE

    return ServicePathway.OPTIMIZE


def _recommendation_confidence(data: AssessmentInput, gates: List[str]) -> EvidenceConfidence:
    evidence = _overall_evidence(data.evidence_confidence)
    if evidence == EvidenceConfidence.LOW or data.material_contradictions or "Risk gate" in gates:
        return EvidenceConfidence.LOW
    if evidence == EvidenceConfidence.MEDIUM or gates:
        return EvidenceConfidence.MEDIUM
    return EvidenceConfidence.HIGH


def _decision_state(
    data: AssessmentInput,
    pathway: ServicePathway,
    recommendation_confidence: EvidenceConfidence,
    gates: List[str],
) -> DecisionState:
    if data.explicit_stop:
        return DecisionState.STOP
    if "Decision controls gate" in gates:
        return DecisionState.DEFER
    if "Risk gate" in gates and not data.risk_boundary_clear:
        return DecisionState.DEFER
    if recommendation_confidence == EvidenceConfidence.LOW:
        return DecisionState.DEFER
    if recommendation_confidence == EvidenceConfidence.MEDIUM:
        return DecisionState.TEST
    if pathway == ServicePathway.MEASURE:
        return DecisionState.TEST
    return DecisionState.ACT


def _next_action(
    pathway: ServicePathway,
    decision: DecisionState,
    limiting: str,
    data: AssessmentInput,
) -> str:
    if decision == DecisionState.STOP:
        return "Stop the proposed AI change and resolve the named stop/revert condition before reconsideration."
    if limiting == "Risk/control":
        return "Clarify approved-use, data, verification, review, approval, and escalation boundaries before expansion."
    if limiting == "Evidence/measurement":
        return "Establish or confirm the baseline and collect decision-grade evidence against the primary outcome measure."
    if limiting == "Purpose":
        return "Bound one priority workflow, accountable owner, intended outcome, and success measure before further AI expansion."
    if limiting == "Decision controls":
        return "Complete the owner, outcome measure, guardrail, review point, stop/revert condition, and invalidation condition before testing."
    if pathway == ServicePathway.OPTIMIZE:
        return "Redesign and test one repeatable workflow with explicit human-review points, controls, and adoption ownership."
    if pathway == ServicePathway.PROVE:
        return "Run the bounded proof period and compare the workflow outcome against baseline, guardrail, and stop criteria."
    return "Run one bounded test that resolves the primary limiting condition before committing further resources."


def evaluate(data: AssessmentInput) -> AssessmentResult:
    _validate(data)
    scores = _scores(data.responses)
    total = sum(scores.values())
    evidence = _overall_evidence(data.evidence_confidence)
    gates = _gates(data, scores)
    limiting = _limiting_condition(data, scores, gates)
    pathway = _pathway(data, scores, total, gates)
    recommendation_confidence = _recommendation_confidence(data, gates)
    decision = _decision_state(data, pathway, recommendation_confidence, gates)
    disposition = (
        WorkflowDisposition.KEEP_HUMAN_LED
        if data.human_led_required
        else WorkflowDisposition.NOT_APPLICABLE
    )

    gaps: List[str] = []
    if _is_blank(data.baseline):
        gaps.append("Baseline missing; impact/ROI remains unproven.")
    if not _priority_is_defined(data):
        gaps.append("Priority workflow is not bounded.")
    if not data.risk_boundary_clear:
        gaps.append("Risk boundary is unresolved.")
    gaps.extend(f"{label} is missing." for label in _missing_decision_controls(data))
    gaps.extend(data.material_contradictions)

    current_position = (
        f"{total}/125; {evidence.value} evidence confidence; "
        f"{_maturity_band(total)}. Score is diagnostic evidence, not authorization."
    )

    return AssessmentResult(
        instrument_version=INSTRUMENT_VERSION,
        engine_version=ENGINE_VERSION,
        release_policy_version=RELEASE_POLICY_VERSION,
        total_score=total,
        dimension_scores=scores,
        evidence_confidence=evidence,
        maturity_band=_maturity_band(total),
        gates_triggered=gates,
        primary_limiting_condition=limiting,
        service_pathway=pathway,
        decision_state=decision,
        workflow_disposition=disposition,
        recommendation_confidence=recommendation_confidence,
        current_position=current_position,
        priority_workflow=data.priority_workflow,
        accountable_owner=data.accountable_owner,
        baseline=data.baseline,
        primary_outcome_measure=data.primary_outcome_measure,
        quality_risk_guardrail=data.quality_risk_guardrail,
        review_point=data.review_point,
        stop_revert_condition=data.stop_revert_condition,
        invalidation_condition=data.invalidation_condition,
        smallest_responsible_next_action=_next_action(pathway, decision, limiting, data),
        unresolved_gaps=gaps,
    )
