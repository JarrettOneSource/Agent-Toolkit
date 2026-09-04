import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import quality, sync_package

ROOT = Path(__file__).resolve().parents[1]


class PackageTests(unittest.TestCase):
    def test_quality_gate_rejects_excessive_function_complexity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scripts = root / "scripts"
            scripts.mkdir()
            source = "def excessive(value):\n"
            source += "".join(f"    if value == {number}:\n        return {number}\n" for number in range(23))
            (scripts / "fixture.py").write_text(source)
            with (
                mock.patch.object(quality, "__file__", str(scripts / "quality.py")),
                mock.patch("builtins.print"),
            ):
                self.assertEqual(quality.main(), 1)

    def test_release_versions_guidance_and_resources_are_complete(self) -> None:
        self.assertEqual(sync_package.synchronize(ROOT, check=True), [])
        subprocess.run([sys.executable, str(ROOT / "scripts/sync_package.py"), "--check"], check=True)
        inventory = json.loads((ROOT / "SOURCES.json").read_text())
        names = set(inventory["custom_skills"]) | set(inventory["matt_pocock"]["skills"])
        skills = ROOT / "plugins/agent-toolkit/skills"
        self.assertEqual(names, {path.name for path in skills.iterdir() if path.is_dir()})
        direct = set(re.findall(r"\$([a-z][a-z0-9-]+)", (ROOT / "AGENTS.md").read_text()))
        self.assertLessEqual(direct, names)
        for name in names:
            path = skills / name / "SKILL.md"
            text = path.read_text()
            self.assertRegex(text, r"(?m)^name:\s*[\"']?" + re.escape(name) + r"[\"']?\s*$")
            prose = re.sub(r"(?ms)^```.*?^```[^\n]*", "", text)
            prose = re.sub(r"`[^`\n]+`", "", prose)
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", prose):
                if target.startswith(("http:", "https:", "#")):
                    continue
                with self.subTest(skill=name, resource=target):
                    self.assertTrue((path.parent / target.split("#", 1)[0]).is_file())

    def test_sync_check_is_read_only_and_update_preserves_other_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "plugins/agent-toolkit/.codex-plugin").mkdir(parents=True)
            manifest = root / "plugins/agent-toolkit/.codex-plugin/plugin.json"
            manifest.write_text('{"name":"agent-toolkit","version":"0.1.0","description":"keep me"}')
            (root / "AGENTS.md").write_text("Working instructions\n")
            (root / "VERSION").write_text("0.2.0\n")
            self.assertEqual(len(sync_package.synchronize(root, check=True)), 2)
            self.assertEqual(json.loads(manifest.read_text())["version"], "0.1.0")
            sync_package.synchronize(root, check=False)
            self.assertEqual(json.loads(manifest.read_text())["description"], "keep me")
            self.assertEqual(json.loads(manifest.read_text())["version"], "0.2.0")
            self.assertEqual((root / "plugins/agent-toolkit/AGENTS.md").read_text(), "Working instructions\n")
            self.assertEqual(sync_package.synchronize(root, check=True), [])

    def test_sync_cli_reports_stale_files_and_updated_files(self) -> None:
        for arguments, changed, expected_code, prefix in (
            (["sync_package.py", "--check"], [ROOT / "AGENTS.md"], 1, "Out of date"),
            (["sync_package.py"], [ROOT / "AGENTS.md"], 0, "Updated"),
            (["sync_package.py", "--check"], [], 0, ""),
        ):
            with (
                self.subTest(arguments=arguments, changed=changed),
                mock.patch.object(sys, "argv", arguments),
                mock.patch.object(sync_package, "synchronize", return_value=changed),
                mock.patch("builtins.print") as output,
            ):
                self.assertEqual(sync_package.main(), expected_code)
                if prefix:
                    self.assertTrue(output.call_args.args[0].startswith(prefix))
                else:
                    output.assert_not_called()

    def test_startup_hook_resolves_its_packaged_guide_from_paths_with_spaces(self) -> None:
        with tempfile.TemporaryDirectory(prefix="toolkit hook ") as directory:
            plugin = Path(directory) / "plugin with spaces"
            shutil.copytree(ROOT / "plugins/agent-toolkit", plugin)
            result = subprocess.run(
                ["sh", str(plugin / "scripts/session-start.sh")], capture_output=True, text=True, check=True
            )
            self.assertIn(str(plugin / "AGENTS.md"), result.stdout)
            self.assertIn("Read and apply", result.stdout)
            self.assertLess(len(result.stdout), 1000)

    def test_utilities_are_separate_from_the_skills_plugin(self) -> None:
        for client in ("codex", "claude"):
            main = json.loads((ROOT / f"plugins/agent-toolkit/.{client}-plugin/plugin.json").read_text())
            self.assertNotIn("mcpServers", main)
        self.assertFalse((ROOT / "plugins/agent-toolkit/.mcp.json").exists())
        mcp = json.loads((ROOT / "plugins/local-tools/.mcp.json").read_text())["mcpServers"]["local_tools"]
        self.assertEqual(mcp["command"], "python3")
        self.assertEqual(mcp["tool_timeout_sec"], 604800)
        self.assertEqual(mcp["omit_tools_from"], ["code_mode", "deferred"])

    def test_mcp_entry_point_can_list_tools_without_package_installation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            environment = dict(
                os.environ,
                LOCAL_TOOLS_MCP_JOB_ROOT=str(Path(directory) / "jobs"),
                LOCAL_TOOLS_MCP_AWAIT_ROOT=str(Path(directory) / "await"),
                LOCAL_TOOLS_MCP_AWAIT_PORT="0",
                LOCAL_TOOLS_MCP_AWAIT_OPEN_BROWSER="0",
            )
            result = subprocess.run(
                [sys.executable, str(ROOT / "plugins/local-tools/scripts/run.py")],
                input='{"jsonrpc":"2.0","id":7,"method":"tools/list"}\n',
                env=environment,
                capture_output=True,
                text=True,
                timeout=10,
                check=True,
            )
            response = json.loads(result.stdout)
            self.assertEqual(response["id"], 7)
            self.assertEqual(len(response["result"]["tools"]), 10)


if __name__ == "__main__":
    unittest.main()
