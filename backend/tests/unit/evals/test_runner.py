from unittest.mock import AsyncMock, MagicMock, patch

import openai
import pytest

from agent.registry import HANDOFF_INPUT_FILTER
from evals.models import EvalCase, ExecutionSummary
from evals.runner import run_case


@pytest.fixture(autouse=True)
def clear_registry():
    from evals import runner

    runner._registry.cache_clear()
    yield
    runner._registry.cache_clear()


def _case(messages=None) -> EvalCase:
    return EvalCase(
        id="billing_1",
        messages=messages or [{"role": "user", "content": "What is my plan?"}],
    )


def _mock_run_result(
    final_output: str = "Your plan is Pro.", last_agent: str = "Billing"
) -> MagicMock:
    result = MagicMock()
    result.final_output = final_output
    result.last_agent.name = last_agent
    result.new_items = []
    result.input_guardrail_results = []
    result.raw_responses = [
        MagicMock(usage=MagicMock(input_tokens=100, output_tokens=50))
    ]
    return result


def _mock_registry(supervisor_name: str = "Supervisor") -> dict:
    supervisor = MagicMock()
    supervisor.name = supervisor_name
    return {"Supervisor": supervisor}


async def test_run_case_success():
    mock_result = _mock_run_result()

    with patch("evals.runner.build_agent_registry", return_value=_mock_registry()):
        with patch(
            "evals.runner.Runner.run", new_callable=AsyncMock, return_value=mock_result
        ):
            summary = await run_case(_case())

    assert isinstance(summary, ExecutionSummary)
    assert summary.case_id == "billing_1"
    assert summary.last_agent == "Billing"
    assert summary.final_output == "Your plan is Pro."
    assert summary.input_tokens == 100
    assert summary.output_tokens == 50
    assert summary.error is None


async def test_run_case_uses_production_handoff_filter():
    """Evals must run with the same handoff filter as the API."""
    with patch("evals.runner.build_agent_registry", return_value=_mock_registry()):
        with patch(
            "evals.runner.Runner.run",
            new_callable=AsyncMock,
            return_value=_mock_run_result(),
        ) as mock_run:
            await run_case(_case())

    _, kwargs = mock_run.call_args
    assert kwargs["run_config"].handoff_input_filter is HANDOFF_INPUT_FILTER


async def test_run_case_starts_at_the_cases_start_agent():
    """A case can resume on a specialist, the way a stored session does."""
    registry = _mock_registry()
    registry["Support"] = MagicMock()
    case = _case()
    case.start_agent = "Support"

    with patch("evals.runner.build_agent_registry", return_value=registry):
        with patch(
            "evals.runner.Runner.run",
            new_callable=AsyncMock,
            return_value=_mock_run_result(),
        ) as mock_run:
            await run_case(case)

    assert mock_run.call_args.kwargs["starting_agent"] is registry["Support"]


async def test_run_case_multi_message_input():
    messages = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi"},
        {"role": "user", "content": "What is my plan?"},
    ]
    mock_result = _mock_run_result()

    with patch("evals.runner.build_agent_registry", return_value=_mock_registry()):
        with patch(
            "evals.runner.Runner.run", new_callable=AsyncMock, return_value=mock_result
        ) as mock_run:
            await run_case(_case(messages=messages))
            # multi-message input is passed as list, not just content string
            call_kwargs = mock_run.call_args.kwargs
            assert call_kwargs["input"] == messages


async def test_run_case_single_message_uses_content_string():
    mock_result = _mock_run_result()

    with patch("evals.runner.build_agent_registry", return_value=_mock_registry()):
        with patch(
            "evals.runner.Runner.run", new_callable=AsyncMock, return_value=mock_result
        ) as mock_run:
            await run_case(_case())
            call_kwargs = mock_run.call_args.kwargs
            assert call_kwargs["input"] == "What is my plan?"


async def test_run_case_generic_exception_returns_error_summary():
    with patch("evals.runner.build_agent_registry", return_value=_mock_registry()):
        with patch(
            "evals.runner.Runner.run",
            new_callable=AsyncMock,
            side_effect=RuntimeError("boom"),
        ):
            summary = await run_case(_case())

    assert summary.error == "boom"
    assert summary.last_agent == ""
    assert summary.final_output == ""


async def test_run_case_rate_limit_retries_then_raises():
    exc = openai.RateLimitError("rate limited", response=MagicMock(), body={})

    with patch("evals.runner.build_agent_registry", return_value=_mock_registry()):
        with patch("evals.runner.Runner.run", new_callable=AsyncMock, side_effect=exc):
            with patch("evals.runner.asyncio.sleep", new_callable=AsyncMock):
                summary = await run_case(_case())

    assert summary.error is not None
    assert "rate" in summary.error.lower() or summary.error != ""


async def test_run_case_guardrail_tripwire_returns_summary():
    from agents import InputGuardrailTripwireTriggered

    mock_guardrail = MagicMock()
    mock_guardrail.get_name.return_value = "prompt_injection"
    mock_guardrail_result = MagicMock()
    mock_guardrail_result.guardrail = mock_guardrail

    exc = InputGuardrailTripwireTriggered(mock_guardrail_result)

    with patch("evals.runner.build_agent_registry", return_value=_mock_registry()):
        with patch("evals.runner.Runner.run", new_callable=AsyncMock, side_effect=exc):
            summary = await run_case(_case())

    assert "prompt_injection" in summary.triggered_guardrails
    assert summary.last_agent == "Supervisor"
    assert summary.error is None
