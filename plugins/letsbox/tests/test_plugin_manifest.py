import json
import unittest
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]


class PluginManifestContractTests(unittest.TestCase):
    def test_plugin_registers_only_the_native_remote_mcp_server(self):
        manifest = json.loads(
            (PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text()
        )
        self.assertNotIn("skills", manifest)
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

    def test_no_local_bridge_or_skill_components_are_packaged(self):
        self.assertFalse((PLUGIN_ROOT / "scripts").exists())
        skill_root = PLUGIN_ROOT / "skills"
        self.assertFalse(skill_root.exists())
        packaged = [
            path
            for path in PLUGIN_ROOT.rglob("*")
            if path.is_file()
            and ".git" not in path.parts
            and path.name in {"SKILL.md", "openai.yaml", "start_mcp.py"}
        ]
        self.assertEqual(packaged, [])


if __name__ == "__main__":
    unittest.main()
