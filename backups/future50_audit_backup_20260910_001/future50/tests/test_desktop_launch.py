from future50.interface.desktop import Future50DesktopShell


def test_desktop_shell_can_render_dashboard_and_route():
    shell = Future50DesktopShell()
    shell.dashboard("research")
    output = shell.route_task("code python debug test")
    assert "Route:" in output
    assert "coding" in output
