from unittest.mock import MagicMock, patch

import pytest

from evals.models import EvalCase, EvalResult, ExecutionSummary, GraderResult
from evals.phoenix_exporter import _extract_score, _phoenix_base_url, export


def _make_result(case_id: str = "billing_1", passed: bool = True) -> EvalResult:
    case = EvalCase(
        id=case_id,
        messages=[{"role": "user", "content": "hello"}],
        expected_agent="Billing",
        expected_tools=["get_subscription"],
        expected_guardrails=[],
    )
    summary = ExecutionSummary(
        case_id=case_id,
        final_output="Here is your plan.",
        last_agent="Billing",
        handoff_chain=["Billing"],
        tool_calls=[("Billing", "get_subscription")],
        triggered_guardrails=[],
        latency_ms=150.0,
        input_tokens=200,
        output_tokens=80,
    )
    graders = [
        GraderResult("routing", passed, "matched Billing"),
        GraderResult("tools", passed, "found get_subscription"),
        GraderResult("guardrails", True, "no expectation set"),
        GraderResult("latency", True, "150ms < 5000ms"),
    ]
    return EvalResult(case=case, summary=summary, grader_results=graders)


def test_phoenix_base_url_strips_path():
    assert _phoenix_base_url("http://localhost:6006/v1/traces") == "http://localhost:6006"


def test_phoenix_base_url_preserves_scheme():
    assert _phoenix_base_url("https://phoenix.example.com/otel") == "https://phoenix.example.com"


def test_extract_score_valid():
    gr = GraderResult("quality", True, "score=4/5 — good response")
    assert _extract_score(gr) == 4


def test_extract_score_none_when_grader_none():
    assert _extract_score(None) is None


def test_extract_score_none_when_no_detail():
    gr = GraderResult("quality", True, "")
    assert _extract_score(gr) is None


def test_extract_score_none_on_bad_format():
    gr = GraderResult("quality", True, "no score here")
    assert _extract_score(gr) is None


def test_export_calls_create_dataset():
    results = [_make_result("billing_1", True), _make_result("billing_2", False)]
    endpoint = "http://localhost:6006/v1/traces"

    mock_client = MagicMock()
    with patch("evals.phoenix_exporter.Client", return_value=mock_client):
        dataset_name = export(results, endpoint)

    mock_client.datasets.create_dataset.assert_called_once()
    call_kwargs = mock_client.datasets.create_dataset.call_args.kwargs
    assert call_kwargs["name"] == dataset_name
    assert "case_id" in call_kwargs["input_keys"]
    assert "final_output" in call_kwargs["output_keys"]
    assert "passed" in call_kwargs["metadata_keys"]


def test_export_returns_dataset_name():
    results = [_make_result()]
    with patch("evals.phoenix_exporter.Client"):
        name = export(results, "http://localhost:6006/v1/traces")
    assert name.startswith("evals-")


def test_export_dataframe_has_correct_rows():
    import pandas as pd

    results = [_make_result("billing_1"), _make_result("routing_1")]
    captured_df = {}

    def capture_create(**kwargs):
        captured_df["df"] = kwargs["dataframe"]

    mock_client = MagicMock()
    mock_client.datasets.create_dataset.side_effect = capture_create

    with patch("evals.phoenix_exporter.Client", return_value=mock_client):
        export(results, "http://localhost:6006/v1/traces")

    df = captured_df["df"]
    assert len(df) == 2
    assert "case_id" in df.columns
    assert set(df["case_id"]) == {"billing_1", "routing_1"}
