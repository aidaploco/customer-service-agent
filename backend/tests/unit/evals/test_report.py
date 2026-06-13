import json

import pytest

from evals.models import EvalCase, EvalResult, ExecutionSummary, GraderResult
from evals.report import build_report, print_report, save_report


def _case(id_: str, tags: list[str] | None = None) -> EvalCase:
    return EvalCase(
        id=id_, messages=[{"role": "user", "content": "hi"}], tags=tags or []
    )


def _summary(
    case_id: str,
    last_agent: str = "Billing",
    input_tokens: int = 100,
    output_tokens: int = 50,
) -> ExecutionSummary:
    return ExecutionSummary(
        case_id=case_id,
        final_output="ok",
        last_agent=last_agent,
        handoff_chain=["Billing"],
        tool_calls=[("Billing", "get_subscription")],
        triggered_guardrails=[],
        latency_ms=200.0,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )


def _result(
    case_id: str, passed: bool = True, last_agent: str = "Billing"
) -> EvalResult:
    case = _case(case_id)
    summary = _summary(case_id, last_agent=last_agent)
    graders = [GraderResult("routing", passed, "detail")]
    return EvalResult(case=case, summary=summary, grader_results=graders)


def test_build_report_pass_rate():
    results = [_result("billing_1", True), _result("billing_2", False)]
    report = build_report(results)
    assert report["summary"]["total"] == 2
    assert report["summary"]["passed"] == 1
    assert report["summary"]["failed"] == 1
    assert report["summary"]["pass_rate"] == pytest.approx(0.5, abs=1e-4)


def test_build_report_empty_results():
    report = build_report([])
    assert report["summary"]["total"] == 0
    assert report["summary"]["pass_rate"] == 0.0


def test_build_report_usage_totals():
    r1 = _result("billing_1")
    r1.summary.input_tokens = 300
    r1.summary.output_tokens = 100
    r2 = _result("billing_2")
    r2.summary.input_tokens = 200
    r2.summary.output_tokens = 50
    report = build_report([r1, r2])
    u = report["summary"]["usage"]
    assert u["input_tokens"] == 500
    assert u["output_tokens"] == 150
    assert u["total_tokens"] == 650


def test_build_report_by_category():
    results = [
        _result("billing_1", True, "Billing"),
        _result("billing_2", False, "Billing"),
        _result("routing_1", True, "Supervisor"),
    ]
    report = build_report(results)
    by_cat = report["summary"]["by_category"]
    assert "billing" in by_cat
    assert "routing" in by_cat
    assert by_cat["billing"]["total"] == 2
    assert by_cat["billing"]["passed"] == 1
    assert by_cat["routing"]["total"] == 1
    assert by_cat["routing"]["passed"] == 1


def test_build_report_by_category_pass_rate():
    results = [
        _result("billing_1", True),
        _result("billing_2", True),
        _result("billing_3", False),
    ]
    report = build_report(results)
    assert report["summary"]["by_category"]["billing"]["pass_rate"] == pytest.approx(
        2 / 3, abs=1e-4
    )


def test_build_report_config_included():
    cfg = {"supervisor_model": "gpt-4o-mini", "billing_model": "gpt-4o"}
    report = build_report([_result("billing_1")], config=cfg)
    assert report["config"] == cfg


def test_build_report_results_list():
    results = [_result("billing_1", True), _result("support_2", False, "Support")]
    report = build_report(results)
    assert len(report["results"]) == 2
    ids = {r["case_id"] for r in report["results"]}
    assert ids == {"billing_1", "support_2"}


def test_build_report_result_fields():
    report = build_report([_result("billing_1", True)])
    r = report["results"][0]
    assert r["passed"] is True
    assert r["last_agent"] == "Billing"
    assert r["latency_ms"] == 200.0
    assert r["handoff_chain"] == ["Billing"]
    assert "Billing:get_subscription" in r["tool_calls"]


def test_build_report_cost_with_known_model():
    cfg = {"billing_model": "gpt-4o-mini"}
    results = [_result("billing_1")]
    results[0].summary.input_tokens = 1_000_000
    results[0].summary.output_tokens = 1_000_000
    report = build_report(results, config=cfg)
    u = report["summary"]["usage"]
    assert u["estimated_cost_usd"] is not None
    assert u["estimated_cost_usd"] > 0


def test_build_report_cost_none_for_unknown_model():
    cfg = {"billing_model": "gpt-unknown"}
    report = build_report([_result("billing_1")], config=cfg)
    assert report["summary"]["usage"]["estimated_cost_usd"] is None


def test_print_report_passes_all(capsys):
    results = [_result("billing_1", True), _result("billing_2", False)]
    report = build_report(results)
    print_report(report)
    captured = capsys.readouterr()
    assert "1/2" in captured.out


def test_print_report_with_config(capsys):
    cfg = {"supervisor_model": "gpt-4o-mini"}
    report = build_report([_result("billing_1")], config=cfg)
    print_report(report)
    captured = capsys.readouterr()
    assert "gpt-4o-mini" in captured.out


def test_save_report_writes_json(tmp_path):
    report = build_report([_result("billing_1")])
    out = tmp_path / "report.json"
    save_report(report, str(out))
    assert out.exists()
    data = json.loads(out.read_text())
    assert data["summary"]["total"] == 1


def test_save_report_creates_parent_dirs(tmp_path):
    report = build_report([])
    nested = tmp_path / "a" / "b" / "report.json"
    save_report(report, str(nested))
    assert nested.exists()


def test_by_category_sorted_alphabetically():
    results = [_result("routing_1"), _result("billing_1"), _result("billing_2")]
    report = build_report(results)
    keys = list(report["summary"]["by_category"].keys())
    assert keys == sorted(keys)
