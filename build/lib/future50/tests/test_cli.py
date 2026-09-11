from future50.app import Future50App


def test_app_run_returns_futur50_string():
    app = Future50App(task="code")
    output = app.run()
    assert "FUTURE-50 started" in output
    assert "coding" in output
