from __future__ import annotations

import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

from local_credentials import LocalCredentials, write_credentials  # noqa: E402
from start_mcp import (  # noqa: E402
    build_mcp_command,
    credentials_state,
    read_optional_credentials,
    resolve_npx,
    setup_notice,
)


class StartMcpSupervisorTests(unittest.TestCase):
    def test_credentials_state_tracks_absence_and_changes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            with patch.dict(os.environ, {"CODEX_HOME": temporary_directory}, clear=False):
                self.assertIsNone(credentials_state())
                self.assertIsNone(read_optional_credentials())

                write_credentials(LocalCredentials(
                    eps_account_email="seller@example.test",
                    serpapi_key="synthetic-key-1",
                ))
                first = credentials_state()
                self.assertIsNotNone(first)
                self.assertIsNotNone(read_optional_credentials())

                time.sleep(0.02)
                write_credentials(LocalCredentials(
                    eps_account_email="seller@example.test",
                    serpapi_key="synthetic-key-2-rotated",
                ))
                second = credentials_state()
                self.assertIsNotNone(second)
                self.assertNotEqual(first, second)

    def test_setup_notice_names_the_file_and_the_configure_tool(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            with patch.dict(os.environ, {"CODEX_HOME": temporary_directory}, clear=False):
                notice = setup_notice()
                self.assertIn("credentials.json", notice)
                self.assertIn("configure_credentials.py", notice)
                self.assertNotIn("serpapi_key\":", notice)

    def test_bridge_command_always_carries_both_credential_headers(self) -> None:
        command = " ".join(build_mcp_command(True))
        self.assertIn("X-LetsBox-Eps-Account-Email: ${LETSBOX_EPS_ACCOUNT_EMAIL}", command)
        self.assertIn("X-LetsBox-SerpApi-Key: ${LETSBOX_SERPAPI_KEY}", command)

    def test_bridge_command_runs_the_resolved_npx_path(self) -> None:
        command = build_mcp_command(True, "/synthetic/node/bin/npx")
        self.assertEqual(command[0], "/synthetic/node/bin/npx")

    def test_resolve_npx_finds_known_installs_without_shell_path(self) -> None:
        # GUI-launched hosts spawn the launcher without the user's shell PATH;
        # the resolver must still find a standard node install under HOME.
        with tempfile.TemporaryDirectory() as temporary_directory:
            node_bin = Path(temporary_directory) / ".local" / "node" / "bin"
            node_bin.mkdir(parents=True)
            npx = node_bin / "npx"
            npx.write_text("#!/bin/sh\n")
            npx.chmod(0o755)
            with patch.dict(os.environ, {"PATH": "", "HOME": temporary_directory}, clear=False):
                self.assertEqual(resolve_npx(), str(npx))

    def test_resolve_npx_reports_absence_instead_of_guessing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            with patch.dict(os.environ, {"PATH": "", "HOME": temporary_directory}, clear=False):
                self.assertIsNone(resolve_npx())


if __name__ == "__main__":
    unittest.main()
