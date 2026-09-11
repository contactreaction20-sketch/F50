from future50.interface.chat_app import Future50ChatApp


def test_chat_app_handles_code_task_and_returns_coding_agent_output():
    app = Future50ChatApp()
    output = app.handle("write python function for fibonacci")
    assert "Coding agent:" in output
    assert "def fibonacci" in output


def test_chat_app_handles_local_pytest_command():
    app = Future50ChatApp()
    output = app.handle("run tests")
    assert "Command:" in output
    assert "Return code:" in output
