import html
import json
import os
import re
import selectors
import socket
import sqlite3
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.parse
import urllib.request
from pathlib import Path
from unittest import mock

from local_tools_mcp.await_instruction import format_waiting_since


class AwaitInstructionTests(unittest.TestCase):
    def test_waiting_since_uses_host_timezone_and_daylight_saving(self) -> None:
        try:
            for timezone, summer, winter in (
                ("UTC", "2026-08-24 17:45:00 UTC", "2026-01-15 18:05:00 UTC"),
                ("America/Los_Angeles", "2026-08-24 10:45:00 PDT", "2026-01-15 10:05:00 PST"),
            ):
                with self.subTest(timezone=timezone), mock.patch.dict(os.environ, {"TZ": timezone}):
                    time.tzset()
                    self.assertEqual(format_waiting_since("2026-08-24T17:45:00+00:00"), summer)
                    self.assertEqual(format_waiting_since("2026-01-15T18:05:00+00:00"), winter)
        finally:
            time.tzset()

    def test_dashboard_starts_eagerly_and_exposes_live_feed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            self._create_codex_state(temp_path, {})
            process, dashboard_file = self._start_server(temp_path)
            self.addCleanup(self._stop_process, process)

            dashboard_url = self._wait_for_dashboard_url(dashboard_file, [process])
            with urllib.request.urlopen(dashboard_url, timeout=2) as response:
                page = response.read().decode("utf-8")
            with urllib.request.urlopen(
                urllib.parse.urljoin(dashboard_url, "api/waits"), timeout=2
            ) as response:
                live_feed = json.loads(response.read())
            with urllib.request.urlopen(
                urllib.parse.urljoin(dashboard_url, "dashboard.js"), timeout=2
            ) as response:
                script = response.read().decode("utf-8")

            self.assertIn("No threads are waiting", page)
            self.assertIn('id="live-status"', page)
            self.assertEqual(live_feed, {"waits": []})
            self.assertIn("setInterval(refreshWaits, 1000)", script)

    def test_one_stdio_server_handles_multiple_waiting_threads(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            self._create_codex_state(
                temp_path,
                {
                    "thread-api": "API timeout investigation",
                    "thread-copy": "Dashboard copy review",
                },
            )
            process, dashboard_file = self._start_server(temp_path)
            self.addCleanup(self._stop_process, process)

            self._send_await(process, request_id=41, thread_id="thread-api")
            agent_comment = "Waiting for a copy decision from the user."
            self._send_await(
                process,
                request_id=42,
                thread_id="thread-copy",
                comment=agent_comment,
            )

            dashboard_url = self._wait_for_dashboard_url(dashboard_file, [process])
            page = self._wait_for_titles(
                dashboard_url,
                ["API timeout investigation", "Dashboard copy review"],
                [process],
            )
            with urllib.request.urlopen(
                urllib.parse.urljoin(dashboard_url, "api/waits"), timeout=2
            ) as response:
                live_feed = json.loads(response.read())
            self.assertEqual(
                {wait["thread_label"] for wait in live_feed["waits"]},
                {"API timeout investigation", "Dashboard copy review"},
            )
            copy_wait = next(wait for wait in live_feed["waits"] if wait["thread_id"] == "thread-copy")
            self.assertEqual(copy_wait["comment"], agent_comment)
            self.assertRegex(copy_wait["waiting_since"], r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} .+$")
            self.assertIn(agent_comment, page)
            second_action, second_token = self._form_for_title(page, "Dashboard copy review")
            second_wait_id = second_action.rsplit("/", 1)[-1]
            with urllib.request.urlopen(
                f"{dashboard_url}?{urllib.parse.urlencode({'wait_id': second_wait_id})}",
                timeout=2,
            ) as response:
                selected_page = response.read().decode("utf-8")
            self.assertIn(
                "<title>Thread Awaiting Instruction - Dashboard copy review</title>",
                selected_page,
            )

            second_instruction = "Use the shorter button label."
            self._submit(dashboard_url, second_action, second_token, second_instruction)
            second_response = self._read_protocol_response(process)
            self.assertEqual(second_response["id"], 42)
            self.assertEqual(second_response["result"]["content"][0]["text"], second_instruction)
            self.assertEqual(
                second_response["result"]["structuredContent"]["thread_title"],
                "Dashboard copy review",
            )
            self.assertEqual(
                second_response["result"]["structuredContent"]["thread_id"],
                "thread-copy",
            )
            self.assertEqual(
                second_response["result"]["structuredContent"]["comment"],
                agent_comment,
            )
            self._assert_no_protocol_response(process)

            page = self._wait_for_titles(dashboard_url, ["API timeout investigation"], [process])
            self.assertNotIn("Dashboard copy review", page)
            first_action, first_token = self._form_for_title(page, "API timeout investigation")
            first_instruction = "Continue tracing the provider deadline."
            self._submit(dashboard_url, first_action, first_token, first_instruction)
            first_response = self._read_protocol_response(process)
            self.assertEqual(first_response["id"], 41)
            self.assertEqual(first_response["result"]["content"][0]["text"], first_instruction)

    def test_dashboard_falls_back_to_native_thread_id_when_title_is_missing(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            self._create_codex_state(temp_path, {})
            process, dashboard_file = self._start_server(temp_path)
            self.addCleanup(self._stop_process, process)

            self._send_await(
                process,
                request_id=43,
                thread_id="019f-native-thread-id",
            )
            dashboard_url = self._wait_for_dashboard_url(dashboard_file, [process])
            fallback_title = "Codex thread 019f-native-thread-id"
            page = self._wait_for_titles(dashboard_url, [fallback_title], [process])
            action, token = self._form_for_title(page, fallback_title)
            self._submit(dashboard_url, action, token, "Resume the unidentified thread.")

            response = self._read_protocol_response(process)
            self.assertEqual(
                response["result"]["structuredContent"]["thread_id"],
                "019f-native-thread-id",
            )
            self.assertIsNone(response["result"]["structuredContent"]["thread_title"])

    def test_dashboard_combines_waits_from_multiple_mcp_processes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            self._create_codex_state(
                temp_path,
                {
                    "thread-first": "First MCP process",
                    "thread-second": "Second MCP process",
                },
            )
            dashboard_port = self._available_port()
            first_process, dashboard_file = self._start_server(temp_path, dashboard_port=dashboard_port)
            second_process, _ = self._start_server(temp_path, dashboard_port=dashboard_port)
            self.addCleanup(self._stop_process, second_process)
            self.addCleanup(self._stop_process, first_process)

            self._send_await(first_process, request_id=51, thread_id="thread-first")
            self._send_await(second_process, request_id=52, thread_id="thread-second")

            dashboard_url = self._wait_for_dashboard_url(
                dashboard_file,
                [first_process, second_process],
            )
            page = self._wait_for_titles(
                dashboard_url,
                ["First MCP process", "Second MCP process"],
                [first_process, second_process],
            )

            second_action, second_token = self._form_for_title(page, "Second MCP process")
            self._submit(
                dashboard_url,
                second_action,
                second_token,
                "Resume the second process first.",
            )
            second_response = self._read_protocol_response(second_process)
            self.assertEqual(second_response["id"], 52)
            self._assert_no_protocol_response(first_process)

            page = self._wait_for_titles(dashboard_url, ["First MCP process"], [first_process])
            first_action, first_token = self._form_for_title(page, "First MCP process")
            self._submit(
                dashboard_url,
                first_action,
                first_token,
                "Now resume the first process.",
            )
            first_response = self._read_protocol_response(first_process)
            self.assertEqual(first_response["id"], 51)

    def test_cancelling_await_instruction_removes_only_that_wait(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            self._create_codex_state(
                temp_path,
                {
                    "thread-kept": "Thread that keeps waiting",
                    "thread-cancelled": "Thread cancelled with Escape",
                },
            )
            process, dashboard_file = self._start_server(temp_path)
            self.addCleanup(self._stop_process, process)

            self._send_await(process, request_id=61, thread_id="thread-kept")
            self._send_await(process, request_id=62, thread_id="thread-cancelled")

            dashboard_url = self._wait_for_dashboard_url(dashboard_file, [process])
            self._wait_for_titles(
                dashboard_url,
                ["Thread that keeps waiting", "Thread cancelled with Escape"],
                [process],
            )

            self._cancel_request(process, request_id=62)

            page = self._wait_for_titles(
                dashboard_url,
                ["Thread that keeps waiting"],
                [process],
                absent_titles=["Thread cancelled with Escape"],
            )
            self.assertNotIn("Thread cancelled with Escape", page)
            self._assert_no_protocol_response(process)

            action, token = self._form_for_title(page, "Thread that keeps waiting")
            self._submit(
                dashboard_url,
                action,
                token,
                "Finish the remaining wait.",
            )
            response = self._read_protocol_response(process)
            self.assertEqual(response["id"], 61)

    @staticmethod
    def _start_server(
        temp_path: Path,
        *,
        dashboard_host: str = "127.0.0.1",
        dashboard_port: int = 0,
    ) -> tuple[subprocess.Popen[str], Path]:
        repo_root = Path(__file__).resolve().parents[1]
        source_root = repo_root / "src"
        dashboard_file = temp_path / "await_instruction.url"
        env = os.environ.copy()
        env.pop("CODEX_HOME", None)
        env.update(
            {
                "LOCAL_TOOLS_MCP_AWAIT_OPEN_BROWSER": "0",
                "LOCAL_TOOLS_MCP_AWAIT_HOST": dashboard_host,
                "LOCAL_TOOLS_MCP_AWAIT_PORT": str(dashboard_port),
                "LOCAL_TOOLS_MCP_AWAIT_URL_FILE": str(dashboard_file),
                "LOCAL_TOOLS_MCP_JOB_ROOT": str(temp_path / "jobs"),
                "HOME": str(temp_path / "home"),
                "PYTHONPATH": os.pathsep.join(filter(None, [str(source_root), env.get("PYTHONPATH", "")])),
            }
        )
        process = subprocess.Popen(
            [sys.executable, "-m", "local_tools_mcp"],
            cwd=repo_root,
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return process, dashboard_file

    @staticmethod
    def _create_codex_state(temp_path: Path, titles: dict[str, str]) -> None:
        codex_home = temp_path / "home" / ".codex-custom"
        codex_home.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(codex_home / "state_5.sqlite")
        try:
            connection.execute("CREATE TABLE threads (id TEXT PRIMARY KEY, title TEXT NOT NULL)")
            connection.executemany(
                "INSERT INTO threads (id, title) VALUES (?, ?)",
                titles.items(),
            )
            connection.commit()
        finally:
            connection.close()

    @staticmethod
    def _available_port() -> int:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            return int(sock.getsockname()[1])

    @staticmethod
    def _send_await(
        process: subprocess.Popen[str],
        *,
        request_id: int,
        thread_id: str,
        comment: str | None = None,
    ) -> None:
        assert process.stdin is not None
        process.stdin.write(
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "method": "tools/call",
                    "params": {
                        "name": "await_instruction",
                        "arguments": {"comment": comment} if comment is not None else {},
                        "_meta": {
                            "callId": f"call-{request_id}",
                            "threadId": thread_id,
                        },
                    },
                }
            )
            + "\n"
        )
        process.stdin.flush()

    @staticmethod
    def _cancel_request(
        process: subprocess.Popen[str],
        *,
        request_id: int | str,
    ) -> None:
        assert process.stdin is not None
        process.stdin.write(
            json.dumps(
                {
                    "jsonrpc": "2.0",
                    "method": "notifications/cancelled",
                    "params": {
                        "requestId": request_id,
                        "reason": "User cancelled the tool call",
                    },
                }
            )
            + "\n"
        )
        process.stdin.flush()

    @staticmethod
    def _wait_for_dashboard_url(
        dashboard_file: Path,
        processes: list[subprocess.Popen[str]],
    ) -> str:
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            AwaitInstructionTests._raise_if_exited(processes)
            if dashboard_file.exists():
                try:
                    payload = json.loads(dashboard_file.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    payload = {}
                dashboard_url = payload.get("dashboard_url")
                if isinstance(dashboard_url, str) and dashboard_url:
                    return dashboard_url
            time.sleep(0.02)
        raise AssertionError("MCP server did not publish its await_instruction dashboard URL")

    @staticmethod
    def _wait_for_titles(
        dashboard_url: str,
        titles: list[str],
        processes: list[subprocess.Popen[str]],
        *,
        absent_titles: list[str] | None = None,
    ) -> str:
        absent_titles = absent_titles or []
        deadline = time.monotonic() + 5
        last_page = ""
        while time.monotonic() < deadline:
            AwaitInstructionTests._raise_if_exited(processes)
            try:
                with urllib.request.urlopen(dashboard_url, timeout=1) as response:
                    last_page = response.read().decode("utf-8")
            except OSError:
                time.sleep(0.02)
                continue
            if all(html.escape(title) in last_page for title in titles) and all(
                html.escape(title) not in last_page for title in absent_titles
            ):
                return last_page
            time.sleep(0.02)
        raise AssertionError(f"Dashboard did not show titles {titles!r}. Last page: {last_page}")

    @staticmethod
    def _form_for_title(page: str, title: str) -> tuple[str, str]:
        expected_heading = f"<h2>{html.escape(title)}</h2>"
        for article in re.findall(
            r'<article class="thread-card[^"]*"[^>]*>(.*?)</article>',
            page,
            flags=re.DOTALL,
        ):
            if expected_heading not in article:
                continue
            action_match = re.search(r'<form method="post" action="([^"]+)">', article)
            token_match = re.search(r'name="token" value="([^"]+)"', article)
            if action_match is not None and token_match is not None:
                return html.unescape(action_match.group(1)), html.unescape(token_match.group(1))
        raise AssertionError(f"No response form found for thread title {title!r}")

    @staticmethod
    def _submit(dashboard_url: str, action: str, token: str, instruction: str) -> None:
        body = urllib.parse.urlencode({"token": token, "instruction": instruction}).encode("utf-8")
        request = urllib.request.Request(
            urllib.parse.urljoin(dashboard_url, action),
            data=body,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=2) as response:
            confirmation = response.read().decode("utf-8")
        if "Instruction sent" not in confirmation:
            raise AssertionError("Dashboard did not confirm the submitted instruction")

    @staticmethod
    def _read_protocol_response(process: subprocess.Popen[str]) -> dict[str, object]:
        assert process.stdout is not None
        selector = selectors.DefaultSelector()
        try:
            selector.register(process.stdout, selectors.EVENT_READ)
            if not selector.select(timeout=5):
                raise AssertionError("MCP server did not return the submitted instruction")
            return json.loads(process.stdout.readline())
        finally:
            selector.close()

    @staticmethod
    def _assert_no_protocol_response(process: subprocess.Popen[str]) -> None:
        assert process.stdout is not None
        selector = selectors.DefaultSelector()
        try:
            selector.register(process.stdout, selectors.EVENT_READ)
            if selector.select(timeout=0.25):
                raise AssertionError(f"Unexpected MCP response: {process.stdout.readline()}")
        finally:
            selector.close()

    @staticmethod
    def _raise_if_exited(processes: list[subprocess.Popen[str]]) -> None:
        for process in processes:
            if process.poll() is None:
                continue
            stderr = process.stderr.read() if process.stderr is not None else ""
            raise AssertionError(f"MCP server exited unexpectedly: {stderr}")

    @staticmethod
    def _stop_process(process: subprocess.Popen[str]) -> None:
        if process.stdin is not None:
            process.stdin.close()
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.terminate()
            process.wait(timeout=2)
        if process.stdout is not None:
            process.stdout.close()
        if process.stderr is not None:
            process.stderr.close()


if __name__ == "__main__":
    unittest.main()
