import json
import shlex
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from local_tools_mcp import jobs, server


class JobLifecycleTests(unittest.TestCase):
    def setUp(self) -> None:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        for name, value in (("JOB_ROOT", self.root / "jobs"), ("STATE_FILE", self.root / "jobs/jobs.json")):
            patcher = mock.patch.object(jobs, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        with jobs.LOCK:
            jobs.JOBS.clear()
            jobs.PROCESSES.clear()

    def call(self, name: str, arguments: dict) -> dict:
        response = server.handle_request(
            {"id": 42, "method": "tools/call", "params": {"name": name, "arguments": arguments}}
        )
        self.assertEqual(response["id"], 42)
        self.assertNotIn("error", response)
        json.dumps(response)
        return response["result"]["structuredContent"]

    def command(self, program: str) -> dict:
        return {"command": shlex.join([sys.executable, "-c", program]), "cwd": str(self.root)}

    def test_shell_preserves_cwd_environment_output_and_exit_status(self) -> None:
        arguments = self.command(
            "import os,sys; print(os.getcwd()); print(os.environ['TOOLKIT_TEST']); print('warning',file=sys.stderr); sys.exit(7)"
        )
        arguments["env"] = {"TOOLKIT_TEST": "expected"}
        result = self.call("run_shell", arguments)
        self.assertEqual(result["job"]["status"], "failed")
        self.assertEqual(result["job"]["exit_code"], 7)
        self.assertEqual(result["stdout_tail"]["lines"], [str(self.root), "expected"])
        self.assertEqual(result["stderr_tail"]["lines"], ["warning"])

    def test_background_job_can_be_waited_filtered_and_read_with_cursor(self) -> None:
        started = self.call("start_job", self.command("print('first'); print('second'); print('third')"))
        job_id = started["job"]["job_id"]
        result = self.call("wait_job", {"job_id": job_id, "timeout_seconds": 3})
        self.assertEqual(result["job"]["status"], "completed")
        self.assertFalse(result["wait_timed_out"])
        tail = self.call("tail_job", {"job_id": job_id, "stream": "stdout", "since_line": 1, "lines": 1})
        self.assertEqual(tail["output"]["lines"], ["second"])
        self.assertEqual(self.call("status_job", {"job_id": job_id})["job"]["exit_code"], 0)
        self.assertEqual(self.call("list_jobs", {"status": "completed"})["count"], 1)
        self.assertEqual(self.call("list_jobs", {"status": "running"})["count"], 0)

    def test_non_cancelling_wait_preserves_running_job(self) -> None:
        started = self.call("start_job", self.command("import time; time.sleep(0.2); print('finished')"))
        job_id = started["job"]["job_id"]
        result = self.call("wait_job", {"job_id": job_id, "timeout_seconds": 0})
        self.assertTrue(result["wait_timed_out"])
        self.assertFalse(result["cancelled_on_timeout"])
        completed = self.call("wait_job", {"job_id": job_id, "timeout_seconds": 3})
        self.assertEqual(completed["stdout_tail"]["lines"], ["finished"])

    def test_wait_timeout_terminates_the_process_group(self) -> None:
        started = self.call("start_job", self.command("import time; time.sleep(20)"))
        result = self.call(
            "wait_job", {"job_id": started["job"]["job_id"], "timeout_seconds": 0, "cancel_on_timeout": True}
        )
        self.assertTrue(result["cancelled_on_timeout"])
        self.assertEqual(result["job"]["status"], "timed_out")
        self.assertFalse(jobs.process_exists(result["job"]["pid"]))

    def test_cancel_terminates_a_running_job_and_is_idempotent(self) -> None:
        started = self.call("start_job", self.command("import time; time.sleep(20)"))
        arguments = {"job_id": started["job"]["job_id"], "grace_seconds": 0.1}
        self.assertEqual(self.call("cancel_job", arguments)["job"]["status"], "cancelled")
        self.assertEqual(self.call("cancel_job", arguments)["job"]["status"], "cancelled")

    def test_start_failure_is_reported_and_recorded(self) -> None:
        arguments = self.command("print('unused')")
        arguments["shell"] = str(self.root / "missing-shell")
        result = self.call("run_shell", arguments)
        self.assertEqual(result["job"]["status"], "start_failed")
        self.assertIn("error", result["job"])
        jobs.JOBS.clear()
        jobs.load_jobs()
        self.assertEqual(jobs.JOBS[result["job"]["job_id"]]["status"], "start_failed")

    def test_invalid_arguments_return_protocol_errors(self) -> None:
        for name, arguments in (
            ("sleep", {"seconds": float("nan")}),
            ("sleep", {"seconds": -1}),
            ("sleep", {"seconds": 604801}),
            ("sleep", {"seconds": True}),
            ("run_shell", {"command": "true", "env": {"X": None}}),
            ("run_shell", {"command": "true", "cwd": str(self.root / "missing")}),
            ("run_shell", {"command": "true", "cwd": __file__}),
            ("start_job", {"command": "true", "tail_lines": -1}),
            ("list_jobs", {"status": 5}),
            ("tail_job", {"job_id": "missing", "stream": "invalid"}),
        ):
            with self.subTest(tool=name, arguments=arguments):
                response = server.handle_request(
                    {"id": 5, "method": "tools/call", "params": {"name": name, "arguments": arguments}}
                )
                self.assertEqual(response["error"]["code"], -32602)
                self.assertEqual(response["id"], 5)

    def test_empty_and_malformed_storage_does_not_hide_new_jobs(self) -> None:
        jobs.load_jobs()
        jobs.STATE_FILE.write_text("invalid json")
        jobs.load_jobs()
        result = self.call("run_shell", self.command("print('new job')"))
        self.assertEqual(result["stdout_tail"]["lines"], ["new job"])
