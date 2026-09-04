import json
import os
import shlex
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WATCHER = ROOT / "utilities/tmux-keep-waiting/tmux-keep-waiting"
BASH = shutil.which("bash")
TWO_OPTIONS = """Our systems are thinking a bit more about this request before responding.
› 1. Dismiss and keep waiting
  2. Learn more
No action is required. Codex will keep waiting
"""
THREE_OPTIONS = """Additional safety checks
This request requires additional safety checks
› 1. Retry with a faster model
  2. Keep waiting
  3. Learn more
Press enter to confirm or esc to go back
"""


class WatcherTests(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory(prefix="toolkit watcher ")
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.socket_path = self.root / "socket"
        listener = socket.socket(socket.AF_UNIX)
        listener.bind(str(self.socket_path))
        self.addCleanup(listener.close)
        binary = self.root / "bin/tmux"
        binary.parent.mkdir()
        binary.write_text(
            f"#!{sys.executable}\n"
            + """import json, os, sys
from pathlib import Path
root = Path(os.environ['TOOLKIT_WATCHER_TEST_ROOT'])
scenario = json.loads((root / 'scenario.json').read_text())
command = sys.argv[3]
if command == 'list-panes':
    print(scenario.get('pane', '%1 0 0'))
elif command == 'capture-pane':
    counter = root / 'captures'
    index = int(counter.read_text()) if counter.exists() else 0
    counter.write_text(str(index + 1))
    print(scenario['screens'][min(index, len(scenario['screens']) - 1)])
elif command == 'send-keys':
    with (root / 'keys').open('a') as stream:
        stream.write(sys.argv[-1] + '\\n')
"""
        )
        binary.chmod(0o755)

    def run_scan(
        self, screens: list[str], *, pane: str = "%1 0 0", current_socket: bool = False
    ) -> list[str]:
        (self.root / "scenario.json").write_text(json.dumps({"screens": screens, "pane": pane}))
        environment = dict(
            os.environ,
            PATH=str(self.root / "bin") + os.pathsep + os.environ["PATH"],
            TOOLKIT_WATCHER_TEST_ROOT=str(self.root),
            TMUX_KEEP_WAIT_SOCKET=str(self.socket_path),
        )
        if current_socket:
            environment.pop("TMUX_KEEP_WAIT_SOCKET")
            environment["TMUX"] = f"{self.socket_path},1,0"
        subprocess.run(
            [BASH, str(WATCHER), "--once"],
            env=environment,
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )
        path = self.root / "keys"
        return path.read_text().splitlines() if path.exists() else []

    def test_selected_wait_option_is_submitted(self) -> None:
        self.assertEqual(self.run_scan([TWO_OPTIONS]), ["Enter"])

    def test_three_option_menu_moves_and_rechecks_before_submitting(self) -> None:
        selected = THREE_OPTIONS.replace("› 1.", "  1.").replace("  2.", "› 2.")
        self.assertEqual(self.run_scan([THREE_OPTIONS, selected]), ["Down", "Enter"])

    def test_learn_more_selection_moves_up_to_wait(self) -> None:
        initial = TWO_OPTIONS.replace("› 1.", "  1.").replace("  2.", "› 2.")
        self.assertEqual(self.run_scan([initial, TWO_OPTIONS]), ["Up", "Enter"])

    def test_changed_menu_is_not_submitted_after_navigation(self) -> None:
        self.assertEqual(self.run_scan([THREE_OPTIONS, "A different screen"]), ["Down"])

    def test_permission_prompt_is_untouched(self) -> None:
        self.assertEqual(self.run_scan(["Allow this command?\n› 1. Yes\n  2. No"]), [])

    def test_copy_mode_panes_are_untouched(self) -> None:
        self.assertEqual(self.run_scan([TWO_OPTIONS], pane="%1 1 0"), [])

    def test_dead_panes_are_untouched(self) -> None:
        self.assertEqual(self.run_scan([TWO_OPTIONS], pane="%1 0 1"), [])

    def test_current_tmux_socket_is_discovered_without_personal_paths(self) -> None:
        self.assertEqual(self.run_scan([TWO_OPTIONS], current_socket=True), ["Enter"])

    def test_extra_arguments_are_rejected(self) -> None:
        result = subprocess.run([BASH, str(WATCHER), "--once", "extra"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Usage:", result.stderr)


@unittest.skipUnless(Path("/usr/bin/tmux").is_file(), "native tmux is not installed")
class LiveTmuxTests(unittest.TestCase):
    def test_wait_selection_reaches_a_real_private_tmux_pane(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            socket_path = root / "tmux.socket"
            receipt = root / "selected"
            menu = root / "menu.sh"
            menu.write_text(
                "#!/bin/bash\nprintf '%s' "
                + shlex.quote(TWO_OPTIONS)
                + "\nIFS= read -r answer\nprintf 'waiting' > "
                + shlex.quote(str(receipt))
                + "\nsleep 20\n"
            )
            command = ["/usr/bin/tmux", "-S", str(socket_path)]
            subprocess.run(
                [
                    *command,
                    "new-session",
                    "-d",
                    "-s",
                    "probe",
                    "-x",
                    "160",
                    "-y",
                    "30",
                    shlex.join([BASH, str(menu)]),
                ],
                check=True,
            )
            try:
                deadline = time.monotonic() + 3
                while time.monotonic() < deadline:
                    capture = subprocess.run(
                        [*command, "capture-pane", "-p", "-t", "probe:0.0"],
                        capture_output=True,
                        text=True,
                        check=True,
                    )
                    if "No action is required" in capture.stdout:
                        break
                    time.sleep(0.02)
                self.assertIn("No action is required", capture.stdout)
                environment = dict(os.environ, PATH="/usr/bin:/bin", TMUX_KEEP_WAIT_SOCKET=str(socket_path))
                subprocess.run(
                    [BASH, str(WATCHER), "--once"],
                    env=environment,
                    capture_output=True,
                    check=True,
                    timeout=3,
                )
                deadline = time.monotonic() + 2
                while not receipt.exists() and time.monotonic() < deadline:
                    time.sleep(0.02)
                self.assertEqual(receipt.read_text(), "waiting")
            finally:
                subprocess.run([*command, "kill-server"], capture_output=True)


if __name__ == "__main__":
    unittest.main()
