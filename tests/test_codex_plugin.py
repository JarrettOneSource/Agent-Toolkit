import json
import os
import selectors
import shutil
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODEX = shutil.which("codex")


@unittest.skipUnless(CODEX, "Codex CLI is not installed")
class NativeCodexPluginTests(unittest.TestCase):
    def test_installed_local_tools_starts_and_exposes_ten_tools(self) -> None:
        with tempfile.TemporaryDirectory(prefix="toolkit native ") as directory:
            scratch = Path(directory)
            codex_home = scratch / "codex"
            codex_home.mkdir()
            environment = dict(os.environ, CODEX_HOME=str(codex_home))
            for arguments in (
                ["plugin", "marketplace", "add", str(ROOT)],
                ["plugin", "add", "local-tools@agent-toolkit"],
            ):
                subprocess.run(
                    [CODEX, *arguments], env=environment, capture_output=True, check=True, timeout=30
                )
            version = (ROOT / "VERSION").read_text().strip()
            config_path = (
                codex_home / f"plugins/cache/agent-toolkit/local-tools/{version}/.codex-plugin/plugin.json"
            )
            config = json.loads(config_path.read_text())
            config["mcpServers"]["local_tools"]["env"].update(
                {
                    "LOCAL_TOOLS_MCP_JOB_ROOT": str(scratch / "jobs"),
                    "LOCAL_TOOLS_MCP_AWAIT_ROOT": str(scratch / "await"),
                    "LOCAL_TOOLS_MCP_AWAIT_PORT": "0",
                }
            )
            config_path.write_text(json.dumps(config))
            process = subprocess.Popen(
                [CODEX, "app-server"],
                env=environment,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
            )
            try:
                with selectors.DefaultSelector() as selector:
                    selector.register(process.stdout, selectors.EVENT_READ)
                    buffer = bytearray()
                    self.rpc(
                        process,
                        selector,
                        buffer,
                        1,
                        "initialize",
                        {
                            "clientInfo": {"name": "toolkit_validation", "version": version},
                            "capabilities": {"experimentalApi": True},
                        },
                    )
                    process.stdin.write(b'{"method":"initialized","params":{}}\n')
                    process.stdin.flush()
                    thread = self.rpc(process, selector, buffer, 2, "thread/start", {"cwd": str(ROOT)})[
                        "thread"
                    ]["id"]
                    result = self.rpc(
                        process, selector, buffer, 3, "mcpServerStatus/list", {"threadId": thread}
                    )
                    server = next(item for item in result["data"] if item["name"] == "local_tools")
                    self.assertEqual(server["runtimeStatus"], "connected")
                    self.assertEqual(server["serverInfo"]["name"], "local-tools")
                    self.assertEqual(len(server["tools"]), 10)
            finally:
                process.stdin.close()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                process.stdout.close()

    def rpc(self, process, selector, buffer, identifier: int, method: str, parameters: dict) -> dict:
        request = {"id": identifier, "method": method, "params": parameters}
        process.stdin.write((json.dumps(request) + "\n").encode())
        process.stdin.flush()
        deadline = time.monotonic() + 25
        while time.monotonic() < deadline:
            while b"\n" in buffer:
                line, _, rest = buffer.partition(b"\n")
                buffer[:] = rest
                message = json.loads(line)
                if message.get("id") == identifier:
                    self.assertNotIn("error", message)
                    return message["result"]
            if selector.select(timeout=0.2):
                chunk = os.read(process.stdout.fileno(), 65536)
                self.assertTrue(chunk, "Codex closed its protocol stream")
                buffer.extend(chunk)
        self.fail(f"Codex timed out handling {method}")


if __name__ == "__main__":
    unittest.main()
