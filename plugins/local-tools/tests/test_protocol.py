import json
import unittest
from pathlib import Path
from unittest import mock

from local_tools_mcp import await_instruction, jobs, monitoring, protocol, server, validation


class ProtocolTests(unittest.TestCase):
    def test_default_paths_follow_current_user_home(self) -> None:
        expected_job_root = Path.home() / ".codex" / "local-tools" / "jobs"

        self.assertEqual(validation.DEFAULT_CWD, str(Path.home()))
        self.assertEqual(jobs.DEFAULT_JOB_ROOT, expected_job_root)
        self.assertEqual(await_instruction.DEFAULT_JOB_ROOT, expected_job_root)

    def test_initialize_returns_server_info(self) -> None:
        response = server.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {"protocolVersion": "2024-11-05"},
            }
        )

        assert response is not None
        self.assertEqual(response["result"]["serverInfo"], {"name": "local-tools", "version": "0.8.0"})
        self.assertIn(
            "Use monitor only when you will end the current turn", response["result"]["instructions"]
        )
        self.assertIn("start_job followed by wait_job", response["result"]["instructions"])

    def test_tools_list_contains_expected_tools(self) -> None:
        response = server.handle_request({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})

        assert response is not None
        names = [tool["name"] for tool in response["result"]["tools"]]
        self.assertEqual(
            names,
            [
                "await_instruction",
                "sleep",
                "run_shell",
                "start_job",
                "wait_job",
                "status_job",
                "tail_job",
                "cancel_job",
                "list_jobs",
                "monitor",
            ],
        )

    def test_notifications_do_not_return_response(self) -> None:
        self.assertIsNone(server.handle_request({"jsonrpc": "2.0", "method": "notifications/initialized"}))

    def test_invalid_tool_arguments_return_jsonrpc_error(self) -> None:
        response = server.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": "run_shell", "arguments": {}},
            }
        )

        assert response is not None
        self.assertEqual(response["error"]["code"], -32602)
        self.assertIn("command is required", response["error"]["message"])

    def test_await_instruction_requires_native_codex_thread_metadata(self) -> None:
        response = server.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 5,
                "method": "tools/call",
                "params": {"name": "await_instruction", "arguments": {}},
            }
        )

        assert response is not None
        self.assertEqual(response["error"]["code"], -32602)
        self.assertIn("Codex thread ID is unavailable", response["error"]["message"])

    def test_await_instruction_schema_only_accepts_optional_comment(self) -> None:
        response = server.handle_request({"jsonrpc": "2.0", "id": 6, "method": "tools/list"})

        assert response is not None
        await_tool = next(tool for tool in response["result"]["tools"] if tool["name"] == "await_instruction")
        self.assertEqual(
            await_tool["inputSchema"]["properties"],
            {
                "comment": {
                    "type": "string",
                    "maxLength": 2000,
                    "description": "Optional agent message displayed on this thread's waiting card.",
                }
            },
        )
        self.assertNotIn("required", await_tool["inputSchema"])
        self.assertIn("persistent goal", await_tool["description"])
        self.assertIn("call await_instruction again", await_tool["description"])
        self.assertIn("Do not mark that goal complete", await_tool["description"])

    def test_await_instruction_validates_comment(self) -> None:
        for request_id, comment, expected in [
            (8, 123, "comment must be a string"),
            (9, "x" * 2001, "comment must be at most 2000 characters"),
        ]:
            with self.subTest(comment_type=type(comment).__name__, expected=expected):
                response = server.handle_request(
                    {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "method": "tools/call",
                        "params": {
                            "name": "await_instruction",
                            "arguments": {"comment": comment},
                            "_meta": {"threadId": "native-thread-id"},
                        },
                    }
                )
                assert response is not None
                self.assertEqual(response["error"]["code"], -32602)
                self.assertIn(expected, response["error"]["message"])

    def test_await_instruction_rejects_agent_populated_title(self) -> None:
        response = server.handle_request(
            {
                "jsonrpc": "2.0",
                "id": 7,
                "method": "tools/call",
                "params": {
                    "name": "await_instruction",
                    "arguments": {"thread_title": "Agent supplied"},
                    "_meta": {"threadId": "native-thread-id"},
                },
            }
        )

        assert response is not None
        self.assertEqual(response["error"]["code"], -32602)
        self.assertIn("does not accept arguments", response["error"]["message"])

    def test_monitor_receives_native_codex_thread_metadata(self) -> None:
        result = protocol.tool_result("started", {"job": {"job_id": "job-1"}})
        with mock.patch.object(monitoring, "monitor_tool", return_value=result) as monitor:
            response = server.handle_request(
                {
                    "jsonrpc": "2.0",
                    "id": 12,
                    "method": "tools/call",
                    "params": {
                        "name": "monitor",
                        "arguments": {"command": "sleep 1"},
                        "_meta": {"threadId": "native-thread-id"},
                    },
                }
            )

        assert response is not None
        self.assertEqual(response["result"], result)
        monitor.assert_called_once_with(
            {"command": "sleep 1"},
            {"threadId": "native-thread-id"},
        )

    def test_monitor_schema_requires_final_callback_or_manual_wait_workflows(self) -> None:
        response = server.handle_request({"jsonrpc": "2.0", "id": 13, "method": "tools/list"})

        assert response is not None
        monitor = next(tool for tool in response["result"]["tools"] if tool["name"] == "monitor")
        self.assertIn("end the current turn immediately", monitor["description"])
        self.assertIn("exactly one final-status callback", monitor["description"])
        self.assertIn("start_job followed by wait_job", monitor["description"])
        self.assertIn("takes manual ownership", monitor["description"])
        tail_lines = monitor["inputSchema"]["properties"]["tail_lines"]
        self.assertEqual(tail_lines["default"], 20)
        self.assertEqual(tail_lines["maximum"], 200)
        self.assertIn("initial response and final callback", tail_lines["description"])

    def test_wait_job_defaults_to_one_hour_and_advises_agents_to_keep_it(self) -> None:
        response = server.handle_request({"jsonrpc": "2.0", "id": 14, "method": "tools/list"})

        assert response is not None
        wait_job = next(tool for tool in response["result"]["tools"] if tool["name"] == "wait_job")
        timeout = wait_job["inputSchema"]["properties"]["timeout_seconds"]
        self.assertEqual(timeout["default"], 3600)
        self.assertIn("default wait is one hour", wait_job["description"])
        self.assertIn("unless they have a specific reason", wait_job["description"])

        payload = {
            "job": {"job_id": "job-1", "status": "completed", "exit_code": 0},
            "wait_timed_out": False,
        }
        with mock.patch.object(jobs, "wait_for_job", return_value=payload) as wait_for_job:
            server.wait_job_tool({"job_id": "job-1"})

        wait_for_job.assert_called_once_with(
            "job-1",
            timeout_seconds=3600.0,
            cancel_on_timeout=False,
            tail_lines=80,
        )

    def test_json_response_is_serializable(self) -> None:
        response = server.handle_request({"jsonrpc": "2.0", "id": 4, "method": "ping"})

        json.dumps(response)
