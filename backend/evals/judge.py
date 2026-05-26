from pydantic import BaseModel

from config import get_settings
from llm.openai import get_async_client
from evals.models import EvalCase, ExecutionSummary, GraderResult


class JudgeVerdict(BaseModel):
    score: int  # 1-5
    reasoning: str
    passed: bool


_SYSTEM = """\
You are an evaluator for a customer service AI assistant called Zara (Brightloop).
Score the assistant's response on a scale of 1–5 and decide if it passes.

Scoring guide:
5 — accurate, helpful, on-topic, professional
4 — mostly good, minor issues
3 — acceptable but missing something important
2 — partially wrong or unhelpful
1 — wrong, harmful, or completely off-topic

Respond with JSON matching: {"score": int, "reasoning": str, "passed": bool}
Pass threshold: score >= 3
"""


async def grade(case: EvalCase, summary: ExecutionSummary) -> GraderResult:
    if case.quality_prompt is None:
        return GraderResult(name="quality", passed=True, detail="no expectation set")

    if summary.error or not summary.final_output:
        return GraderResult(
            name="quality", passed=False, detail=f"no output: {summary.error}"
        )

    client = get_async_client()
    prompt = (
        f"Customer message: {case.messages[-1]['content']}\n\n"
        f"Assistant response: {summary.final_output}\n\n"
        f"Evaluation criteria: {case.quality_prompt}"
    )

    response = await client.chat.completions.create(
        model=get_settings().eval_judge_model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": prompt},
        ],
        temperature=0,
        max_completion_tokens=300,
    )

    verdict = JudgeVerdict.model_validate_json(response.choices[0].message.content)
    return GraderResult(
        name="quality",
        passed=verdict.passed,
        detail=f"score={verdict.score}/5 — {verdict.reasoning}",
    )
