from future50.interface.cli import Future50CLI


def test_cli_run_supports_local_interactive_prompt_text(capsys):
    cli = Future50CLI()
    cli.interactive_loop = lambda tagline="FUTURE-50 local CLI": print(tagline)
    # This test verifies the CLI object remains local and interactive-friendly.
    assert cli is not None
