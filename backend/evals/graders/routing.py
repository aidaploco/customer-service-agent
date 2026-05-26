from evals.models import EvalCase, ExecutionSummary, GraderResult


def grade(case: EvalCase, summary: ExecutionSummary) -> GraderResult:
    if case.expected_agent is None:
        return GraderResult(name="routing", passed=True, detail="no expectation set")

    if summary.error:
        return GraderResult(
            name="routing", passed=False, detail=f"run error: {summary.error}"
        )

    if summary.last_agent == case.expected_agent:
        return GraderResult(name="routing", passed=True, detail=summary.last_agent)

    return GraderResult(
        name="routing",
        passed=False,
        detail=f"expected={case.expected_agent} got={summary.last_agent}",
    )
