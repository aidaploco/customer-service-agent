import argparse
import asyncio
import sys
from datetime import datetime, timezone
from pathlib import Path

# Allow running from backend/ directory without installing the package.
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import get_settings
from evals.graders import guardrails, latency, routing, tools
from evals.judge import grade as judge_grade
from evals.loader import load_cases
from evals.models import EvalResult
from evals.phoenix_exporter import export as phoenix_export
from evals.report import build_report, print_report, save_report
from evals.runner import run_case


async def run_all(cases, concurrency: int) -> list[EvalResult]:
    sem = asyncio.Semaphore(concurrency)

    async def run_one(case):
        async with sem:
            print(f"  running {case.id}…")
            summary = await run_case(case)
            grader_results = [
                routing.grade(case, summary),
                tools.grade(case, summary),
                guardrails.grade(case, summary),
                latency.grade(case, summary),
            ]
            if case.quality_prompt:
                grader_results.append(await judge_grade(case, summary))
            return EvalResult(case=case, summary=summary, grader_results=grader_results)

    return await asyncio.gather(*[run_one(c) for c in cases])


def main():
    parser = argparse.ArgumentParser(description="Run agent evals")
    parser.add_argument("--cases", help="Path to a specific YAML cases file")
    parser.add_argument(
        "--threshold", type=float, default=0.9, help="Min pass rate (default 0.9)"
    )
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    default_output = str(Path(__file__).parent / "data" / f"eval_report_{ts}.json")
    parser.add_argument("--output", default=default_output, help="Report output path")
    parser.add_argument(
        "--skip-tags", nargs="*", default=[], help="Skip cases with these tags"
    )
    parser.add_argument(
        "--concurrency", type=int, default=3, help="Max parallel cases (default 3)"
    )
    args = parser.parse_args()

    skip = set(args.skip_tags) if args.skip_tags else None
    cases = load_cases(path=args.cases, skip_tags=skip)

    if not cases:
        print("No cases found.")
        sys.exit(0)

    print(f"\nRunning {len(cases)} eval case(s)…\n")

    results = asyncio.run(run_all(cases, concurrency=args.concurrency))

    s = get_settings()
    report = build_report(
        results,
        config={
            "supervisor_model": s.supervisor_model,
            "billing_model": s.billing_model,
            "support_model": s.support_model,
            "guardrail_model": s.guardrail_model,
            "eval_judge_model": s.eval_judge_model,
        },
    )
    print_report(report)
    save_report(report, args.output)

    endpoint = get_settings().phoenix_collector_endpoint
    if endpoint:
        try:
            dataset_name = phoenix_export(results, endpoint)
            print(f"\nUploaded to Phoenix dataset: {dataset_name}")
        except Exception as exc:
            print(f"\nPhoenix export failed (non-fatal): {exc}")

    pass_rate = report["summary"]["pass_rate"]
    if pass_rate < args.threshold:
        print(
            f"\nFAILED: pass rate {pass_rate:.1%} is below threshold {args.threshold:.1%}"
        )
        sys.exit(1)

    print(f"\nPASSED: {pass_rate:.1%} >= {args.threshold:.1%}")


if __name__ == "__main__":
    main()
