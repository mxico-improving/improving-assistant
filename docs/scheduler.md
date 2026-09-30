# Weekly reminder (OS scheduler)

`ia.py install-scheduler` registers a job that runs `ia.py notify`:
- every Monday at 09:00, and
- again about 5 minutes after login or boot, so a laptop that was off on Monday still gets
  reminded later in the week.

`notify` does nothing on weekends and nothing once the week is marked done (`/weekly-checkin`
does this after a successful submit). Otherwise it shows a desktop notification.

Before registering the job, the installer copies the stdlib-only app to
`~/.improving-assistant/app/`. Claude Code plugin updates move the plugin directory, so the
job must not point there. After updating the plugin, re-run `install-scheduler`.

| OS | Mechanism | Files | Catch-up |
|---|---|---|---|
| Linux | systemd user timer | `~/.config/systemd/user/improving-assistant.{service,timer}` | `Persistent=true` + `OnStartupSec=5min` |
| macOS | launchd LaunchAgent | `~/Library/LaunchAgents/com.improving.assistant.plist` | `RunAtLoad` (login) + launchd runs missed calendar jobs on wake |
| Windows | Task Scheduler | task "ImprovingAssistant" (XML in `~/.improving-assistant/scheduler/`) | `StartWhenAvailable` + logon trigger |

Notifications use `notify-send` on Linux (from the libnotify package), `osascript` on macOS, and
a PowerShell toast on Windows. If notifications are unavailable, the message is printed instead.

## Check and test

    python3 ia.py remind-check        # prints the reminder, or exits 1 if nothing is due
    python3 ia.py notify              # shows the notification now if the week is pending
    # Linux:   systemctl --user list-timers improving-assistant.timer
    # macOS:   launchctl list | grep com.improving.assistant
    # Windows: schtasks /Query /TN ImprovingAssistant

## Remove

    # Linux
    systemctl --user disable --now improving-assistant.timer
    rm ~/.config/systemd/user/improving-assistant.{service,timer}
    # macOS
    launchctl unload ~/Library/LaunchAgents/com.improving.assistant.plist
    rm ~/Library/LaunchAgents/com.improving.assistant.plist
    # Windows
    schtasks /Delete /TN ImprovingAssistant /F

Then optionally delete `~/.improving-assistant/`.
