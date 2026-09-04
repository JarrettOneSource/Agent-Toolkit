import json
import os
import subprocess
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest import mock

from local_tools_mcp import jobs, monitoring, server


class MonitorNotificationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)

        self.patchers = [
            mock.patch.object(jobs, "JOB_ROOT", self.root / "jobs"),
            mock.patch.object(jobs, "STATE_FILE", self.root / "jobs" / "jobs.json"),
            mock.patch.object(monitoring, "MONITOR_NOTIFICATION_RETRY_DELAYS", (0.0,)),
        ]
        for patcher in self.patchers:
            patcher.start()
            self.addCleanup(patcher.stop)

        with jobs.LOCK:
            jobs.JOBS.clear()
            jobs.PROCESSES.clear()

    def test_capture_monitor_origin_records_thread_and_tmux_pane(self) -> None:
        with mock.patch.dict(
            os.environ,
            {"TMUX": "/tmp/tmux-test/default,123,0", "TMUX_PANE": "%7"},
            clear=False,
        ):
            origin = monitoring.capture_monitor_origin({"threadId": " thread-123 "})

        self.assertEqual(
            origin,
            {
                "thread_id": "thread-123",
                "tmux_pane": "%7",
                "tmux_socket": "/tmp/tmux-test/default",
            },
        )

    def test_queue_codex_message_uses_native_thread_command(self) -> None:
        completed = subprocess.CompletedProcess([], 0, stdout="queued\n", stderr="")
        with (
            mock.patch.dict(os.environ, {"LOCAL_TOOLS_MCP_CODEX_BIN": "/opt/codex"}),
            mock.patch.object(monitoring.subprocess, "run", return_value=completed) as run,
        ):
            monitoring.queue_codex_message("thread-123", "[Local Tools] Job ID: job-1\nfinished")

        self.assertEqual(
            run.call_args.args[0],
            [
                "/opt/codex",
                "queue",
                "--thread",
                "thread-123",
                "--message",
                "[Local Tools] Job ID: job-1\nfinished",
            ],
        )

    def test_format_monitor_notification_uses_clean_output_and_status(self) -> None:
        events_path = self.root / "events.jsonl"
        events_path.write_text(
            "\n".join(
                [
                    json.dumps({"stream": "stdout", "line": "progress 50%"}),
                    json.dumps({"stream": "stderr", "line": "warning"}),
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        message = monitoring.format_monitor_notification(
            {
                "job_id": "job-1",
                "events_path": str(events_path),
                "status": "completed",
                "exit_code": 0,
                "finished_at": "2026-08-31T03:30:02+00:00",
            },
            start_line=0,
            end_line=2,
            tail_lines=20,
        )

        self.assertEqual(
            message,
            "[Local Tools] Job ID: job-1\n"
            "Status: completed (exit code 0).\n"
            "Finished at: 2026-08-31T03:30:02+00:00.\n"
            "progress 50%\n"
            "[stderr] warning",
        )

    def test_monitor_queues_only_terminal_status(self) -> None:
        queued: list[tuple[str, str]] = []
        terminal_delivery = threading.Event()

        def capture_queue(thread_id: str, message: str) -> None:
            queued.append((thread_id, message))
            if "Status: completed" in message:
                terminal_delivery.set()

        with (
            mock.patch.dict(
                os.environ,
                {"TMUX": "/tmp/tmux-test/default,123,0", "TMUX_PANE": "%9"},
                clear=False,
            ),
            mock.patch.object(monitoring, "queue_codex_message", side_effect=capture_queue),
        ):
            result = monitoring.monitor_tool(
                {
                    "command": "printf 'initial\\n'; sleep 0.2; printf 'update\\n'; sleep 0.4",
                    "cwd": str(self.root),
                    "startup_wait_seconds": 0.5,
                },
                {"threadId": "thread-monitor"},
            )
            job_id = result["structuredContent"]["job"]["job_id"]
            self.assertTrue(terminal_delivery.wait(3), "terminal monitor notification was not queued")

        self._wait_for_notification_state(job_id, "finished")
        self.assertEqual(len(queued), 1)
        self.assertEqual(queued[0][0], "thread-monitor")
        self.assertIn(f"[Local Tools] Job ID: {job_id}", queued[0][1])
        self.assertIn("Status: completed (exit code 0).", queued[0][1])
        self.assertIn("Finished at:", queued[0][1])
        self.assertIn("update", queued[0][1])
        self.assertNotIn("initial", queued[0][1])
        self.assertIn("End this turn now", result["content"][0]["text"])
        self.assertIn("start_job followed by wait_job", result["content"][0]["text"])
        self.assertIn("combined_tail", result["structuredContent"])
        self.assertNotIn("stdout_tail", result["structuredContent"])
        self.assertNotIn("stderr_tail", result["structuredContent"])

        job = jobs.job_payload(job_id)
        self.assertEqual(
            job["origin"],
            {
                "thread_id": "thread-monitor",
                "tmux_pane": "%9",
                "tmux_socket": "/tmp/tmux-test/default",
            },
        )
        self.assertEqual(job["notification"]["messages_queued"], 1)
        self.assertEqual(job["notification"]["next_line"], 2)

    def test_chatty_monitor_queues_only_requested_terminal_tail(self) -> None:
        queued: list[tuple[str, str]] = []
        terminal_delivery = threading.Event()

        def capture_queue(thread_id: str, message: str) -> None:
            queued.append((thread_id, message))
            if "Status: completed" in message:
                terminal_delivery.set()

        with mock.patch.object(monitoring, "queue_codex_message", side_effect=capture_queue):
            result = monitoring.monitor_tool(
                {
                    "command": (
                        "printf 'initial\\n'; sleep 0.15; "
                        "printf 'first update\\n'; sleep 0.15; "
                        "printf 'second update\\n'; sleep 0.15; "
                        "printf 'third update\\n'; sleep 0.15"
                    ),
                    "cwd": str(self.root),
                    "startup_wait_seconds": 0.5,
                    "tail_lines": 2,
                },
                {"threadId": "thread-monitor"},
            )
            job_id = result["structuredContent"]["job"]["job_id"]
            self.assertTrue(terminal_delivery.wait(3), "terminal monitor notification was not queued")

        self._wait_for_notification_state(job_id, "finished")
        self.assertEqual(len(queued), 1)
        self.assertIn("Status: completed (exit code 0).", queued[0][1])
        self.assertIn("[... 1 earlier output lines omitted ...]", queued[0][1])
        self.assertNotIn("first update", queued[0][1])
        self.assertIn("second update", queued[0][1])
        self.assertIn("third update", queued[0][1])

        job = jobs.job_payload(job_id)
        self.assertEqual(job["notification"]["messages_queued"], 1)
        self.assertEqual(job["notification"]["next_line"], 4)

    def test_wait_job_takes_ownership_and_suppresses_monitor_callback(self) -> None:
        queued: list[tuple[str, str]] = []

        with mock.patch.object(
            monitoring, "queue_codex_message", side_effect=lambda *args: queued.append(args)
        ):
            result = monitoring.monitor_tool(
                {
                    "command": "printf 'initial\\n'; sleep 0.2; printf 'finished\\n'",
                    "cwd": str(self.root),
                    "startup_wait_seconds": 0.5,
                },
                {"threadId": "thread-monitor"},
            )
            job_id = result["structuredContent"]["job"]["job_id"]
            waited = server.wait_job_tool({"job_id": job_id, "timeout_seconds": 2})

        self.assertEqual(queued, [])
        self.assertIn("Automatic monitor callback was suppressed", waited["content"][0]["text"])
        notification = jobs.job_payload(job_id)["notification"]
        self.assertEqual(notification["state"], "suppressed")
        self.assertEqual(notification["suppressed_by"], "wait_job")

    def test_cancel_job_takes_ownership_and_suppresses_monitor_callback(self) -> None:
        queued: list[tuple[str, str]] = []

        with mock.patch.object(
            monitoring, "queue_codex_message", side_effect=lambda *args: queued.append(args)
        ):
            result = monitoring.monitor_tool(
                {
                    "command": "printf 'initial\\n'; sleep 10",
                    "cwd": str(self.root),
                    "startup_wait_seconds": 0.5,
                },
                {"threadId": "thread-monitor"},
            )
            job_id = result["structuredContent"]["job"]["job_id"]
            cancelled = server.cancel_job_tool({"job_id": job_id, "grace_seconds": 0})

        self.assertEqual(queued, [])
        self.assertIn("Automatic monitor callback was suppressed", cancelled["content"][0]["text"])
        notification = jobs.job_payload(job_id)["notification"]
        self.assertEqual(notification["state"], "suppressed")
        self.assertEqual(notification["suppressed_by"], "cancel_job")

    def test_monitor_without_thread_metadata_keeps_running_with_notifications_disabled(self) -> None:
        result = monitoring.monitor_tool(
            {
                "command": "sleep 0.1",
                "cwd": str(self.root),
                "startup_wait_seconds": 0,
            }
        )
        payload = result["structuredContent"]
        job_id = payload["job"]["job_id"]

        self.assertFalse(payload["job"]["notification"]["enabled"])
        self.assertEqual(payload["job"]["notification"]["state"], "disabled")
        self.assertIn("Automatic callbacks are unavailable", result["content"][0]["text"])
        jobs.wait_for_job(
            job_id,
            timeout_seconds=2,
            cancel_on_timeout=True,
            tail_lines=5,
        )

    def _wait_for_notification_state(self, job_id: str, expected: str) -> None:
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            if jobs.job_payload(job_id).get("notification", {}).get("state") == expected:
                return
            time.sleep(0.01)
        self.fail(f"notification state did not become {expected!r}")


if __name__ == "__main__":
    unittest.main()
