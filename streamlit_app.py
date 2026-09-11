import streamlit as st

from diagnostic import AssessmentInput, EvidenceConfidence, evaluate
from diagnostic.questions import DIMENSIONS, QUESTIONS


st.set_page_config(page_title="CLConsulting AI Impact + Readiness", layout="wide")
st.title("AI Impact + Readiness")
st.caption("Measure. Optimize. Prove. | Decision-grade diagnostic")

st.info(
    "Rate current, consistent behavior and available evidence — not intent, enthusiasm, "
    "or theoretical capability. Scores diagnose; gates and evidence control the recommendation."
)

with st.form("assessment"):
    participant = st.text_input("Participant")
    organization = st.text_input("Role / organization")

    responses = {}
    confidence = {}
    for dimension, question_ids in DIMENSIONS.items():
        st.header(dimension)
        for qid in question_ids:
            responses[qid] = st.radio(
                f"{qid}. {QUESTIONS[qid]}",
                options=[1, 2, 3, 4, 5],
                horizontal=True,
                key=f"q{qid}",
            )
        confidence[dimension] = EvidenceConfidence(
            st.selectbox(
                f"Evidence confidence — {dimension}",
                ["High", "Medium", "Low"],
                index=1,
                key=f"confidence-{dimension}",
            )
        )

    st.header("Implementation decision inputs")
    priority_workflow = st.text_input("Priority workflow")
    accountable_owner = st.text_input("Accountable owner")
    baseline = st.text_input("Baseline (leave blank if not established)")
    primary_outcome_measure = st.text_input("Primary outcome measure")
    quality_risk_guardrail = st.text_input("Quality / risk guardrail")
    review_point = st.text_input("Review point")
    stop_revert_condition = st.text_input("Stop / revert condition")
    invalidation_condition = st.text_input("Invalidation condition")

    c1, c2, c3 = st.columns(3)
    priority_defined = c1.checkbox("Priority is clearly defined", value=True)
    risk_boundary_clear = c2.checkbox("Risk boundary is clear", value=True)
    human_led_required = c3.checkbox("Keep Human-Led required")
    explicit_stop = st.checkbox("A stop/hold condition is already triggered")
    contradictions = st.text_area(
        "Material contradiction flags (one per line)",
        help="Use when scores, examples, claimed outcomes, ownership, or risk evidence materially conflict.",
    )

    submitted = st.form_submit_button("Generate implementation decision", type="primary")

if submitted:
    result = evaluate(
        AssessmentInput(
            responses=responses,
            evidence_confidence=confidence,
            priority_workflow=priority_workflow or "Not yet bounded",
            accountable_owner=accountable_owner or "Not yet assigned",
            baseline=baseline.strip() or None,
            primary_outcome_measure=primary_outcome_measure or "Not yet defined",
            quality_risk_guardrail=quality_risk_guardrail or "Not yet defined",
            review_point=review_point or "Not yet defined",
            stop_revert_condition=stop_revert_condition or "Not yet defined",
            invalidation_condition=invalidation_condition or "Not yet defined",
            priority_defined=priority_defined,
            risk_boundary_clear=risk_boundary_clear,
            human_led_required=human_led_required,
            explicit_stop=explicit_stop,
            material_contradictions=[x.strip() for x in contradictions.splitlines() if x.strip()],
        )
    )

    st.divider()
    st.header("Implementation Decision")
    st.write(result.current_position)

    a, b, c, d = st.columns(4)
    a.metric("Service pathway", result.service_pathway.value)
    b.metric("Decision state", result.decision_state.value)
    c.metric("Recommendation confidence", result.recommendation_confidence.value)
    d.metric("Workflow disposition", result.workflow_disposition.value)

    st.subheader("Dimension profile")
    st.table(
        [
            {
                "Dimension": name,
                "Score": f"{score}/25",
                "Evidence confidence": confidence[name].value,
            }
            for name, score in result.dimension_scores.items()
        ]
    )

    st.subheader("Decision controls")
    st.write(f"**Primary limiting condition:** {result.primary_limiting_condition}")
    st.write(f"**Triggered gates:** {', '.join(result.gates_triggered) if result.gates_triggered else 'None'}")
    st.write(f"**Smallest responsible next action:** {result.smallest_responsible_next_action}")

    st.subheader("Proof plan")
    st.write(f"**Priority workflow:** {result.priority_workflow}")
    st.write(f"**Accountable owner:** {result.accountable_owner}")
    st.write(f"**Baseline:** {result.baseline or 'Not established — impact/ROI unproven'}")
    st.write(f"**Primary outcome measure:** {result.primary_outcome_measure}")
    st.write(f"**Quality / risk guardrail:** {result.quality_risk_guardrail}")
    st.write(f"**Review point:** {result.review_point}")
    st.write(f"**Stop / revert condition:** {result.stop_revert_condition}")
    st.write(f"**Invalidation condition:** {result.invalidation_condition}")

    if result.unresolved_gaps:
        st.warning("Unresolved gaps: " + " | ".join(result.unresolved_gaps))

    st.caption(
        "This diagnostic supports implementation decisions. It is not a legal, regulatory, security, "
        "compliance, or certification determination."
    )
