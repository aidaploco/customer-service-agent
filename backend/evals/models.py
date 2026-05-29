from dataclasses import dataclass, field


@dataclass
class EvalCase:
    id: str
    messages: list[dict]
    expected_agent: str | None = None
    expected_tools: list[str] | None = None  # ordered-subset match
    expected_guardrails: list[str] | None = None
    quality_prompt: str | None = None
    latency_budget_ms: float | None = None
    tags: list[str] = field(default_factory=list)


@dataclass
class ExecutionSummary:
    case_id: str
    final_output: str
    last_agent: str
    handoff_chain: list[str]
    tool_calls: list[tuple[str, str]]  # (agent_name, tool_name)
    triggered_guardrails: list[str]
    latency_ms: float
    input_tokens: int = 0
    output_tokens: int = 0
    error: str | None = None


@dataclass
class GraderResult:
    name: str
    passed: bool
    detail: str = ""


@dataclass
class EvalResult:
    case: EvalCase
    summary: ExecutionSummary
    grader_results: list[GraderResult]

    @property
    def passed(self) -> bool:
        return all(g.passed for g in self.grader_results)
