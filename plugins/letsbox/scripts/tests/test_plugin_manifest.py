import json
from pathlib import Path
import unittest


PLUGIN_ROOT = Path(__file__).resolve().parents[2]


class PluginManifestContractTests(unittest.TestCase):
    def test_plugin_registers_only_the_remote_mcp_server(self):
        manifest = json.loads(
            (PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text()
        )
        self.assertNotIn("skills", manifest)
        self.assertEqual(manifest["mcpServers"], "./.mcp.json")

        mcp = json.loads((PLUGIN_ROOT / ".mcp.json").read_text())
        self.assertEqual(set(mcp["mcpServers"]), {"letsbox"})

    def test_no_local_skill_components_are_packaged(self):
        skill_root = PLUGIN_ROOT / "skills"
        self.assertFalse(skill_root.exists())
        packaged_skill_files = [
            path
            for path in PLUGIN_ROOT.rglob("*")
            if path.is_file()
            and ".git" not in path.parts
            and path.name in {"SKILL.md", "openai.yaml"}
        ]
        self.assertEqual(packaged_skill_files, [])


if __name__ == "__main__":
    unittest.main()
