import json
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]


class PluginManifestContractTests(unittest.TestCase):
    def test_plugin_registers_only_the_native_remote_mcp_server(self):
        manifest = json.loads(
            (PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text()
        )
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertEqual(manifest["mcpServers"], "./.mcp.json")

        mcp = json.loads((PLUGIN_ROOT / ".mcp.json").read_text())
        self.assertEqual(set(mcp["mcpServers"]), {"letsbox"})
        server = mcp["mcpServers"]["letsbox"]
        # Native remote registration: the host manages OAuth itself (the
        # "authenticate" button) and no local process, node runtime, or
        # credential file is involved. Runtime credentials live server-side
        # via set_runtime_credentials.
        self.assertEqual(server["type"], "http")
        self.assertEqual(server["url"], "https://mcp.letsai.team/mcp")
        self.assertNotIn("command", server)
        self.assertNotIn("args", server)

    def test_only_connection_guidance_skills_are_packaged(self):
        # ローカルブリッジや業務スキルのpackage同梱は引き続き禁止。プラグインが
        # 持ってよいローカルスキルは、接続・セットアップ案内の2つだけ。
        self.assertFalse((PLUGIN_ROOT / "scripts").exists())
        skills = sorted(
            path.parent.name
            for path in (PLUGIN_ROOT / "skills").glob("*/SKILL.md")
        )
        self.assertEqual(
            skills,
            [
                "letsbox-connection-check",
                "letsbox-credentials",
                "letsbox-progress",
                "letsbox-setup",
                "letsbox-support-report",
                "letsbox-switch-account",
            ],
        )
        packaged = [
            path
            for path in PLUGIN_ROOT.rglob("*")
            if path.is_file()
            and ".git" not in path.parts
            and path.name in {"openai.yaml", "start_mcp.py"}
        ]
        self.assertEqual(packaged, [])


if __name__ == "__main__":
    unittest.main()
