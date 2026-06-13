from evals.models import EvalCase, EvalResult, ExecutionSummary, GraderResult


def _make_summary(**kwargs) -> ExecutionSummary:
    defaults = dict(
        case_id="test_1",
        final_output="hello",
        last_agent="Supervisor",
        handoff_chain=[],
        tool_calls=[],
        triggered_guardrails=[],
        latency_ms=123.4,
    )
    return ExecutionSummary(**{**defaults, **kwargs})


def test_eval_case_required_fields():
    case = EvalCase(id="routing_1", messages=[{"role": "user", "content": "hi"}])
    assert case.id == "routing_1"
    assert len(case.messages) == 1


def test_eval_case_defaults():
    case = EvalCase(id="x", messages=[])
    assert case.expected_agent is None
    assert case.expected_tools is None
    assert case.expected_guardrails is None
    assert case.quality_prompt is None
    assert case.latency_budget_ms is None
    assert case.tags == []


def test_eval_case_tags_are_independent():
    a = EvalCase(id="a", messages=[])
    b = EvalCase(id="b", messages=[])
    a.tags.append("db")
    assert b.tags == []


def test_execution_summary_defaults():
    s = _make_summary()
    assert s.input_tokens == 0
    assert s.output_tokens == 0
    assert s.error is None


def test_execution_summary_with_error():
    s = _make_summary(error="timeout")
    assert s.error == "timeout"


def test_grader_result():
    gr = GraderResult(name="routing", passed=True, detail="matched Billing")
    assert gr.name == "routing"
    assert gr.passed is True
    assert gr.detail == "matched Billing"


def test_grader_result_default_detail():
    gr = GraderResult(name="latency", passed=False)
    assert gr.detail == ""


def test_eval_result_passed_all_pass():
    case = EvalCase(id="x", messages=[])
    summary = _make_summary()
    graders = [GraderResult("routing", True), GraderResult("tools", True)]
    result = EvalResult(case=case, summary=summary, grader_results=graders)
    assert result.passed is True


def test_eval_result_failed_any_fails():
    case = EvalCase(id="x", messages=[])
    summary = _make_summary()
    graders = [GraderResult("routing", True), GraderResult("tools", False)]
    result = EvalResult(case=case, summary=summary, grader_results=graders)
    assert result.passed is False


def test_eval_result_passed_empty_graders():
    case = EvalCase(id="x", messages=[])
    summary = _make_summary()
    result = EvalResult(case=case, summary=summary, grader_results=[])
    assert result.passed is True
