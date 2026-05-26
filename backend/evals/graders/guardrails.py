from evals.models import EvalCase, ExecutionSummary, GraderResult


def grade(case: EvalCase, summary: ExecutionSummary) -> GraderResult:
    if case.expected_guardrails is None:
        return GraderResult(name="guardrails", passed=True, detail="no expectation set")

    if summary.error:
        return GraderResult(
            name="guardrails", passed=False, detail=f"run error: {summary.error}"
        )

    expected = set(case.expected_guardrails)
    actual = set(summary.triggered_guardrails)

    if expected == actual:
        return GraderResult(name="guardrails", passed=True, detail=str(actual))

    missing = expected - actual
    unexpected = actual - expected
    parts = []
    if missing:
        parts.append(f"missing={sorted(missing)}")
    if unexpected:
        parts.append(f"unexpected={sorted(unexpected)}")

    return GraderResult(name="guardrails", passed=False, detail=", ".join(parts))
