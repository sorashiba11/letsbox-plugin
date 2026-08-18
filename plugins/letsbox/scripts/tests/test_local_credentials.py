from __future__ import annotations

import io
import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

from configure_credentials import main as configure_main  # noqa: E402
from local_credentials import (  # noqa: E402
    LocalCredentials,
    credentials_path,
    is_configured,
    read_credentials,
    write_credentials,
)
from start_mcp import build_mcp_command  # noqa: E402


class LocalCredentialsTests(unittest.TestCase):
    def test_write_read_and_permissions_are_private(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            with patch.dict(os.environ, {"CODEX_HOME": temporary_directory}, clear=False):
                credentials = LocalCredentials("customer@example.invalid", "synthetic-serpapi-key")
                path = write_credentials(credentials)
                self.assertEqual(path, credentials_path())
                self.assertEqual(read_credentials(), credentials)
                self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
                self.assertEqual(stat.S_IMODE(path.parent.stat().st_mode), 0o700)
                self.assertTrue(is_configured())

    def test_unconfigured_state_does_not_create_or_print_values(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            with patch.dict(os.environ, {"CODEX_HOME": temporary_directory}, clear=False):
                self.assertFalse(is_configured())
                self.assertFalse(credentials_path().exists())

    def test_bridge_command_contains_only_environment_placeholders(self) -> None:
        command = " ".join(build_mcp_command())
        self.assertIn("${LETSBOX_EPS_ACCOUNT_EMAIL}", command)
        self.assertIn("${LETSBOX_SERPAPI_KEY}", command)
        self.assertNotIn("synthetic-serpapi-key", command)
        self.assertIn("mcp-remote@0.1.38", command)
        self.assertIn("research:read research:run launcher:session", command)
        self.assertIn("http://127.0.0.1:3334/oauth/callback", command)
        self.assertIn("6OnzMqzQDxGJbOiz4iiySULm", command)
        command_without_credentials = " ".join(build_mcp_command(False))
        self.assertNotIn("X-LetsBox-Eps-Account-Email", command_without_credentials)
        self.assertNotIn("X-LetsBox-SerpApi-Key", command_without_credentials)

    def test_payload_shape_does_not_allow_extra_runtime_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            with patch.dict(os.environ, {"CODEX_HOME": temporary_directory}, clear=False):
                path = write_credentials(LocalCredentials("customer@example.invalid", "synthetic-serpapi-key"))
                payload = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(sorted(payload), ["eps_account_email", "serpapi_key", "version"])

    def test_setup_output_does_not_include_submitted_values(self) -> None:
        email = "customer@example.invalid"
        key = "synthetic-serpapi-key"
        with tempfile.TemporaryDirectory() as temporary_directory:
            with patch.dict(os.environ, {"CODEX_HOME": temporary_directory}, clear=False):
                with patch("sys.stdin", io.StringIO(json.dumps({"eps_account_email": email, "serpapi_key": key}))):
                    with patch("sys.stdout", new_callable=io.StringIO) as stdout:
                        with patch("sys.stderr", new_callable=io.StringIO) as stderr:
                            self.assertEqual(configure_main(["--stdin-json"]), 0)
                self.assertNotIn(email, stdout.getvalue())
                self.assertNotIn(key, stdout.getvalue())
                self.assertNotIn(email, stderr.getvalue())
                self.assertNotIn(key, stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
