# tmux-keep-waiting

Automatically select **Keep waiting** or **Dismiss and keep waiting** when Codex
shows a waiting menu inside tmux. Supports the two-option menu where waiting is
option 1 and the older three-option menus where waiting is option 2.

When Codex shows “Selected model is at capacity” immediately above an empty chat
prompt and reports “Goal stalled (/goal resume)”, the watcher sends `continue`.
It sends once while that error remains on screen and rearms after the screen changes.
Draft messages and errors followed by newer transcript output are left untouched.

The watcher scans panes every 0.5 seconds, checks the selected menu row, moves to
the waiting option when needed, and presses Enter. After moving, it checks the
screen again before submitting. It skips dead panes and panes in copy mode, with
a three-second cooldown between actions in each pane.

## Requirements

- Linux with Bash 4 or later.
- tmux available on `PATH`.
- Codex running inside tmux with an English waiting menu.
- A systemd user manager for the optional background service.

## Run

From the Agent Toolkit repository root, enter the utility directory first. The remaining commands on this page run from that directory:

```sh
cd utilities/tmux-keep-waiting
./tmux-keep-waiting
```

Run a single scan, including selecting the waiting option when detected:

```sh
./tmux-keep-waiting --once
```

By default, the script checks the standard tmux socket under
`${TMUX_TMPDIR:-/tmp}/tmux-$(id -u)/default` and the current socket from `TMUX`,
when launched inside tmux.

To target a custom socket or one session:

```sh
TMUX_KEEP_WAIT_SOCKET=/path/to/tmux/socket TMUX_KEEP_WAIT_SESSION=main ./tmux-keep-waiting
```

| Variable | Default | Purpose |
| --- | --- | --- |
| `TMUX_KEEP_WAIT_SOCKET` | Standard and current sockets | Check only this socket when nonempty. |
| `TMUX_KEEP_WAIT_SESSION` | All sessions | Check only the named session when nonempty. |
| `TMUX_KEEP_WAIT_INTERVAL` | `0.5` | Seconds between scans. |

## Install as a user service

From the utility directory:

```sh
install -Dm755 tmux-keep-waiting "$HOME/bin/tmux-keep-waiting"
install -Dm644 systemd/tmux-keep-waiting.service "$HOME/.config/systemd/user/tmux-keep-waiting.service"
systemctl --user daemon-reload
systemctl --user enable --now tmux-keep-waiting.service
```

The service uses `%h/bin/tmux-keep-waiting`, so it resolves the executable under
the current user's home directory. To configure a custom socket or session, run
`systemctl --user edit tmux-keep-waiting.service` and add your values:

```ini
[Service]
Environment=TMUX_KEEP_WAIT_SOCKET=/path/to/tmux/socket
Environment=TMUX_KEEP_WAIT_SESSION=main
Environment=TMUX_KEEP_WAIT_INTERVAL=0.5
```

Restart after updating the script or service settings:

```sh
systemctl --user restart tmux-keep-waiting.service
```

Check status and follow selections:

```sh
systemctl --user status tmux-keep-waiting.service
journalctl --user -u tmux-keep-waiting.service -f
```

Stop automatic selection:

```sh
systemctl --user disable --now tmux-keep-waiting.service
```
