import json
from dataclasses import asdict
from pathlib import Path

from evals.models import EvalResult
from evals.pricing import estimate_cost_usd

_RESPONSE_PREVIEW_LEN = 200


def _category(case_id: str) -> str:
    return case_id.split("_")[0]


def build_report(results: list[EvalResult], config: dict | None = None) -> dict:
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    pass_rate = passed / total if total else 0.0

    total_input = sum(r.summary.input_tokens for r in results)
    total_output = sum(r.summary.output_tokens for r in results)

    cfg = config or {}
    by_category: dict[str, dict] = {}
    unknown_pricing: set[str] = set()

    for r in results:
        cat = _category(r.case.id)
        entry = by_category.setdefault(
            cat,
            {
                "total": 0,
                "passed": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "cost_usd": None,
            },
        )
        entry["total"] += 1
        entry["passed"] += int(r.passed)
        entry["input_tokens"] += r.summary.input_tokens
        entry["output_tokens"] += r.summary.output_tokens
        cost = estimate_cost_usd(
            r.summary.last_agent, r.summary.input_tokens, r.summary.output_tokens, cfg
        )
        if cost is None:
            unknown_pricing.add(r.summary.last_agent)
        else:
            entry["cost_usd"] = (entry["cost_usd"] or 0.0) + cost

    known_costs = [
        v["cost_usd"] for v in by_category.values() if v["cost_usd"] is not None
    ]
    total_cost: float | None = round(sum(known_costs), 6) if known_costs else None

    def _case_cost(r: EvalResult) -> float | None:
        c = estimate_cost_usd(
            r.summary.last_agent, r.summary.input_tokens, r.summary.output_tokens, cfg
        )
        return round(c, 6) if c is not None else None

    return {
        "config": cfg,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": round(pass_rate, 4),
            "usage": {
                "input_tokens": total_input,
                "output_tokens": total_output,
                "total_tokens": total_input + total_output,
                "estimated_cost_usd": total_cost,
                "unknown_pricing_agents": sorted(unknown_pricing) or None,
            },
            "by_category": {
                cat: {
                    "pass_rate": round(v["passed"] / v["total"], 4)
                    if v["total"]
                    else 0,
                    "passed": v["passed"],
                    "total": v["total"],
                    "input_tokens": v["input_tokens"],
                    "output_tokens": v["output_tokens"],
                    "estimated_cost_usd": round(v["cost_usd"], 6)
                    if v["cost_usd"] is not None
                    else None,
                }
                for cat, v in sorted(by_category.items())
            },
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
                "usage": {
                    "input_tokens": r.summary.input_tokens,
                    "output_tokens": r.summary.output_tokens,
                    "estimated_cost_usd": _case_cost(r),
                },
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
    u = s.get("usage", {})
    if u.get("total_tokens"):
        cost = u.get("estimated_cost_usd")
        cost_str = f"  ~${cost:.4f}" if cost is not None else ""
        print(
            f"  Tokens: {u['input_tokens']:,} in / {u['output_tokens']:,} out / {u['total_tokens']:,} total{cost_str}"
        )
        unknown = u.get("unknown_pricing_agents")
        if unknown:
            print(
                f"  Warning: no pricing data for agents {unknown} — add to evals/pricing.py"
            )
        print()

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
