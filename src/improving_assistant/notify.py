"""Native desktop notifications with no third-party dependencies."""

from __future__ import annotations

import platform
import subprocess


def current_os() -> str:
    return {"Darwin": "macos", "Windows": "windows"}.get(platform.system(), "linux")


def notify_command(os_name: str, title: str, message: str) -> list[str]:
    if os_name == "macos":
        q = lambda s: s.replace("\\", "\\\\").replace('"', '\\"')  # noqa: E731
        return ["osascript", "-e", f'display notification "{q(message)}" with title "{q(title)}"']
    if os_name == "windows":
        q = lambda s: s.replace("'", "''")  # noqa: E731
        script = (
            "[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType=WindowsRuntime] | Out-Null;"
            "$t=[Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02);"
            f"$x=$t.GetElementsByTagName('text');$x.Item(0).InnerText='{q(title)}';$x.Item(1).InnerText='{q(message)}';"
            "[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier('Improving Assistant').Show([Windows.UI.Notifications.ToastNotification]::new($t))"
        )
        return ["powershell", "-NoProfile", "-Command", script]
    return ["notify-send", "--app-name=Improving Assistant", title, message]


def send(title: str, message: str) -> None:
    """Best effort: never crash the scheduled job because notifications are unavailable."""
    try:
        subprocess.run(notify_command(current_os(), title, message), check=False, timeout=15)
    except (OSError, subprocess.SubprocessError):
        print(f"{title}: {message}")
