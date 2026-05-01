from agents import FunctionTool

from agent.supervisor.tools import greet


def test_greet_is_function_tool():
    assert isinstance(greet, FunctionTool)


def test_greet_name():
    assert greet.name == "greet"


def test_greet_has_description():
    assert greet.description is not None
    assert len(greet.description) > 0
