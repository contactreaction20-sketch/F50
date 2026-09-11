from future50.coding.agent import CodingAgent


def test_coding_agent_generates_python_function_for_fibonacci():
    agent = CodingAgent()
    output = agent.handle("write python function for fibonacci")
    assert "def fibonacci" in output


def test_coding_agent_supports_debug_and_test_plans():
    agent = CodingAgent()
    debug_output = agent.handle("debug failing code")
    test_output = agent.handle("run tests")
    assert "Debug plan" in debug_output
    assert "Test plan" in test_output
