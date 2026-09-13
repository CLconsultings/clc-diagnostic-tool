from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class EvidenceConfidence(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class ServicePathway(str, Enum):
    MEASURE = "Measure"
    OPTIMIZE = "Optimize"
    PROVE = "Prove"


class DecisionState(str, Enum):
    ACT = "Act"
    TEST = "Test"
    DEFER = "Defer"
    STOP = "Stop"


class WorkflowDisposition(str, Enum):
    KEEP_HUMAN_LED = "Keep Human-Led"
    NOT_APPLICABLE = "Not Applicable"


@dataclass(frozen=True)
class AssessmentInput:
    responses: Dict[int, int]
    evidence_confidence: Dict[str, EvidenceConfidence]
    priority_workflow: str
    accountable_owner: str
    baseline: Optional[str]
    primary_outcome_measure: str
    quality_risk_guardrail: str
    review_point: str
    stop_revert_condition: str
    invalidation_condition: str
    priority_defined: bool = False
    risk_boundary_clear: bool = False
    human_led_required: bool = False
    explicit_stop: bool = False
    material_contradictions: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class AssessmentResult:
    instrument_version: str
    engine_version: str
    release_policy_version: str
    total_score: int
    dimension_scores: Dict[str, int]
    evidence_confidence: EvidenceConfidence
    maturity_band: str
    gates_triggered: List[str]
    primary_limiting_condition: str
    service_pathway: ServicePathway
    decision_state: DecisionState
    workflow_disposition: WorkflowDisposition
    recommendation_confidence: EvidenceConfidence
    current_position: str
    priority_workflow: str
    accountable_owner: str
    baseline: Optional[str]
    primary_outcome_measure: str
    quality_risk_guardrail: str
    review_point: str
    stop_revert_condition: str
    invalidation_condition: str
    smallest_responsible_next_action: str
    unresolved_gaps: List[str]
