from evals.models import EvalCase, ExecutionSummary, GraderResult


def grade(case: EvalCase, summary: ExecutionSummary) -> GraderResult:
    if case.latency_budget_ms is None:
        return GraderResult(name="latency", passed=True, detail="no budget set")

    if summary.error:
        return GraderResult(
            name="latency", passed=False, detail=f"run error: {summary.error}"
        )

    passed = summary.latency_ms <= case.latency_budget_ms
    detail = f"{summary.latency_ms:.0f}ms (budget={case.latency_budget_ms:.0f}ms)"
    return GraderResult(name="latency", passed=passed, detail=detail)
