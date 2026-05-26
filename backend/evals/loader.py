from pathlib import Path

import yaml

from evals.models import EvalCase

_CASES_DIR = Path(__file__).parent / "cases"


def load_cases(
    path: str | None = None, skip_tags: set[str] | None = None
) -> list[EvalCase]:
    if path:
        files = [Path(path)]
    else:
        files = sorted(_CASES_DIR.glob("*.yaml"))

    cases = []
    for file in files:
        with open(file) as f:
            raw = yaml.safe_load(f)
        for item in raw:
            case = EvalCase(
                id=item["id"],
                messages=item["messages"],
                expected_agent=item.get("expected_agent"),
                expected_tools=item.get("expected_tools"),
                expected_guardrails=item.get("expected_guardrails"),
                quality_prompt=item.get("quality_prompt"),
                latency_budget_ms=item.get("latency_budget_ms"),
                tags=item.get("tags", []),
            )
            if skip_tags and set(case.tags) & skip_tags:
                continue
            cases.append(case)

    return cases
