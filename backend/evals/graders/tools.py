from evals.models import EvalCase, ExecutionSummary, GraderResult


def grade(case: EvalCase, summary: ExecutionSummary) -> GraderResult:
    if case.expected_tools is None:
        return GraderResult(name="tools", passed=True, detail="no expectation set")

    if summary.error:
        return GraderResult(
            name="tools", passed=False, detail=f"run error: {summary.error}"
        )

    actual_tool_names = [t for _, t in summary.tool_calls]

    # Ordered-subset: every expected tool must appear in order; extras allowed.
    it = iter(actual_tool_names)
    for expected in case.expected_tools:
        if not any(actual == expected for actual in it):
            return GraderResult(
                name="tools",
                passed=False,
                detail=f"expected ordered subset {case.expected_tools}, got {actual_tool_names}",
            )

    return GraderResult(
        name="tools",
        passed=True,
        detail=f"found {case.expected_tools} in {actual_tool_names}",
    )
