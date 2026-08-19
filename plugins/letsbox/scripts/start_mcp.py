#!/usr/bin/env python3
"""Start the local credential-injecting stdio bridge for Lets Box Remote MCP.

The bridge (mcp-remote) resolves credential headers once at startup, so this
launcher supervises it: it refuses to start a credential-less bridge (waiting
with a setup prompt until the local credentials file exists) and exits when
the file changes, so the next MCP spawn picks up new credentials without the
user restarting anything by hand.
"""

from __future__ import annotations

import os
import shutil
import signal
import subprocess
import sys
import time

from local_credentials import CredentialError, credentials_path, read_credentials


REMOTE_MCP_URL = "https://mcp.letsai.team/mcp"
MCP_REMOTE_VERSION = "0.1.38"
OAUTH_CALLBACK_PORT = "3334"
OAUTH_CLIENT_ID = "6OnzMqzQDxGJbOiz4iiySULm"
EPS_EMAIL_ENV = "LETSBOX_EPS_ACCOUNT_EMAIL"
SERPAPI_KEY_ENV = "LETSBOX_SERPAPI_KEY"
TRUSTED_EBAY_SCOPE = (
    "research:read research:run launcher:session "
    "eps:write listing:price_write listing:quantity_write listing:delete"
)


def build_mcp_command(include_credential_headers: bool = True) -> list[str]:
    command = [
        "npx",
        "--yes",
        f"mcp-remote@{MCP_REMOTE_VERSION}",
        REMOTE_MCP_URL,
        OAUTH_CALLBACK_PORT,
        "--host",
        "127.0.0.1",
        "--transport",
        "http-only",
        "--silent",
        "--static-oauth-client-metadata",
        json_client_metadata(),
        "--static-oauth-client-info",
        json_client_info(),
    ]
    if include_credential_headers:
        command.extend([
            "--header",
            f"X-LetsBox-Eps-Account-Email: ${{{EPS_EMAIL_ENV}}}",
            "--header",
            f"X-LetsBox-SerpApi-Key: ${{{SERPAPI_KEY_ENV}}}",
        ])
    return command


def json_client_metadata() -> str:
    return (
        '{"client_name":"Lets Box local bridge","scope":"'
        + TRUSTED_EBAY_SCOPE
        + '"}'
    )


def json_client_info() -> str:
    return (
        '{"client_id":"'
        + OAUTH_CLIENT_ID
        + '","redirect_uris":["http://127.0.0.1:'
        + OAUTH_CALLBACK_PORT
        + '/oauth/callback"],"token_endpoint_auth_method":"none","grant_types":["authorization_code","refresh_token"],"response_types":["code"],"scope":"'
        + TRUSTED_EBAY_SCOPE
        + '"}'
    )


CREDENTIAL_POLL_SECONDS = 3.0
SETUP_NOTICE_INTERVAL_SECONDS = 60.0


def credentials_state() -> tuple[int, int] | None:
    """A cheap change token for the credentials file (None = absent)."""
    try:
        status = os.stat(credentials_path())
    except OSError:
        return None
    return (status.st_mtime_ns, status.st_size)


def read_optional_credentials():
    try:
        return read_credentials()
    except CredentialError:
        return None


def setup_notice() -> str:
    return (
        "Lets Box: local credentials are not configured yet. "
        f"Create {credentials_path()} with scripts/configure_credentials.py "
        "(eps_account_email + serpapi_key). The bridge starts automatically "
        "as soon as the file exists."
    )


def main() -> int:
    npx = shutil.which("npx")
    if npx is None:
        print("Lets Box local bridge requires npx.", file=sys.stderr)
        return 69

    # Never run a credential-less bridge: it would cache "no headers" for its
    # whole lifetime. Prompt for setup and start the moment the file appears.
    credentials = read_optional_credentials()
    if credentials is None:
        print(setup_notice(), file=sys.stderr, flush=True)
        last_notice = time.monotonic()
        while credentials is None:
            time.sleep(CREDENTIAL_POLL_SECONDS)
            credentials = read_optional_credentials()
            if credentials is None and time.monotonic() - last_notice >= SETUP_NOTICE_INTERVAL_SECONDS:
                print(setup_notice(), file=sys.stderr, flush=True)
                last_notice = time.monotonic()

    state_at_spawn = credentials_state()
    child_environment = os.environ.copy()
    child_environment[EPS_EMAIL_ENV] = credentials.eps_account_email
    child_environment[SERPAPI_KEY_ENV] = credentials.serpapi_key
    try:
        child = subprocess.Popen(build_mcp_command(True), env=child_environment)
    except OSError:
        print("Lets Box local bridge could not start mcp-remote.", file=sys.stderr)
        return 69

    def forward_terminate(_signum: int, _frame: object) -> None:
        child.terminate()

    signal.signal(signal.SIGTERM, forward_terminate)
    signal.signal(signal.SIGINT, forward_terminate)

    # Exit when the credentials file changes; the client's next MCP spawn
    # re-runs this launcher and reads the fresh file. The child keeps the
    # session's stdio, so this supervisor never touches the protocol stream.
    while True:
        exit_code = child.poll()
        if exit_code is not None:
            return exit_code
        if credentials_state() != state_at_spawn:
            print(
                "Lets Box: credentials file changed; restarting the bridge so the "
                "next request uses the new credentials.",
                file=sys.stderr,
                flush=True,
            )
            child.terminate()
            try:
                child.wait(timeout=10)
            except subprocess.TimeoutExpired:
                child.kill()
                child.wait()
            return 0
        time.sleep(CREDENTIAL_POLL_SECONDS)


if __name__ == "__main__":
    raise SystemExit(main())
