"""Desktop notification: builds the right OS command. Tests don't actually notify."""

from improving_assistant.notify import notify_command


def test_linux_uses_notify_send():
    assert notify_command("linux", "T", "hello") == ["notify-send", "--app-name=Improving Assistant", "T", "hello"]


def test_macos_uses_osascript_and_escapes_quotes():
    cmd = notify_command("macos", "T", 'say "hi"')

    assert cmd[0] == "osascript"
    assert 'display notification "say \\"hi\\"" with title "T"' in cmd[-1]


def test_windows_uses_powershell_toast():
    cmd = notify_command("windows", "T", "it's done")

    assert cmd[0] == "powershell"
    assert "it''s done" in cmd[-1]  # single quotes doubled for PowerShell
