import json
from dataclasses import asdict
from pathlib import Path

from evals.models import EvalResult

_RESPONSE_PREVIEW_LEN = 200


def build_report(results: list[EvalResult], config: dict | None = None) -> dict:
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    pass_rate = passed / total if total else 0.0

    return {
        "config": config or {},
        "summary": {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": round(pass_rate, 4),
        },
        "results": [
            {
                "case_id": r.case.id,
                "passed": r.passed,
                "last_agent": r.summary.last_agent,
                "handoff_chain": r.summary.handoff_chain,
                "tool_calls": [f"{a}:{t}" for a, t in r.summary.tool_calls],
                "final_output": r.summary.final_output,
                "latency_ms": round(r.summary.latency_ms, 1),
                "error": r.summary.error,
                "graders": [asdict(g) for g in r.grader_results],
            }
            for r in results
        ],
    }


def print_report(report: dict) -> None:
    if report.get("config"):
        cfg = report["config"]
        parts = [f"{k}: {v}" for k, v in cfg.items()]
        print(f"\nConfig: {' | '.join(parts)}")
    s = report["summary"]
    print(f"\nEval results: {s['passed']}/{s['total']} passed ({s['pass_rate']:.1%})\n")

    for r in report["results"]:
        status = "PASS" if r["passed"] else "FAIL"
        agent = r["last_agent"] or "?"
        print(f"  [{status}] {r['case_id']}  →  {agent}  ({r['latency_ms']}ms)")

        chain = r.get("handoff_chain", [])
        route = (
            " → ".join(["Supervisor"] + chain) if chain else "Supervisor (no handoff)"
        )
        print(f"         Route: {route}")

        if r["final_output"]:
            preview = r["final_output"].replace("\n", " ")
            if len(preview) > _RESPONSE_PREVIEW_LEN:
                preview = preview[:_RESPONSE_PREVIEW_LEN] + "…"
            print(f'         Response: "{preview}"')

        for g in r["graders"]:
            if g["detail"] == "no expectation set":
                continue
            mark = "✓" if g["passed"] else "✗"
            print(f"         {mark} {g['name']}: {g['detail']}")

        print()


def save_report(report: dict, path: str) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w") as f:
        json.dump(report, f, indent=2)
    print(f"Report saved to {path}")
