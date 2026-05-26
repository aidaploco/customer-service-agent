from datetime import datetime, timezone
from urllib.parse import urlparse

import pandas as pd
from phoenix.client import Client

from evals.models import EvalResult


def _phoenix_base_url(collector_endpoint: str) -> str:
    """Derive Phoenix base URL from the OTel collector endpoint."""
    parsed = urlparse(collector_endpoint)
    return f"{parsed.scheme}://{parsed.netloc}"


def export(results: list[EvalResult], collector_endpoint: str) -> str:
    """Upload eval results to Phoenix as a versioned dataset. Returns the dataset name."""
    rows = []
    for r in results:
        grader_map = {g.name: g for g in r.grader_results}

        rows.append(
            {
                # inputs — what we fed / expected
                "case_id": r.case.id,
                "user_message": r.case.messages[-1]["content"],
                "expected_agent": r.case.expected_agent or "",
                "expected_tools": ", ".join(r.case.expected_tools or []),
                "expected_guardrails": ", ".join(r.case.expected_guardrails or []),
                # outputs — what the agent produced
                "final_output": r.summary.final_output,
                "last_agent": r.summary.last_agent,
                "tool_calls": ", ".join(f"{t}" for _, t in r.summary.tool_calls),
                "triggered_guardrails": ", ".join(r.summary.triggered_guardrails),
                # metadata — grader verdicts + perf
                "passed": r.passed,
                "latency_ms": round(r.summary.latency_ms, 1),
                "routing_ok": grader_map["routing"].passed
                if "routing" in grader_map
                else None,
                "tools_ok": grader_map["tools"].passed
                if "tools" in grader_map
                else None,
                "guardrails_ok": grader_map["guardrails"].passed
                if "guardrails" in grader_map
                else None,
                "latency_ok": grader_map["latency"].passed
                if "latency" in grader_map
                else None,
                "quality_score": _extract_score(grader_map.get("quality")),
                "error": r.summary.error or "",
            }
        )

    df = pd.DataFrame(rows)
    run_ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    dataset_name = f"evals-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}"

    client = Client(base_url=_phoenix_base_url(collector_endpoint))
    client.datasets.create_dataset(
        name=dataset_name,
        dataframe=df,
        input_keys=[
            "case_id",
            "user_message",
            "expected_agent",
            "expected_tools",
            "expected_guardrails",
        ],
        output_keys=[
            "final_output",
            "last_agent",
            "tool_calls",
            "triggered_guardrails",
        ],
        metadata_keys=[
            "passed",
            "latency_ms",
            "routing_ok",
            "tools_ok",
            "guardrails_ok",
            "latency_ok",
            "quality_score",
            "error",
        ],
        dataset_description=f"Automated eval run — {run_ts}",
    )
    return dataset_name


def _extract_score(grader_result) -> int | None:
    if grader_result is None or not grader_result.detail:
        return None
    # detail format: "score=4/5 — ..."
    try:
        return int(grader_result.detail.split("score=")[1].split("/")[0])
    except (IndexError, ValueError):
        return None
