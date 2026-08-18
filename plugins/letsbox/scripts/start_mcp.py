#!/usr/bin/env python3
"""Start the local credential-injecting stdio bridge for Lets Box Remote MCP."""

from __future__ import annotations

import os
import shutil
import sys

from local_credentials import CredentialError, read_credentials


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


def main() -> int:
    try:
        credentials = read_credentials()
    except CredentialError:
        credentials = None
    npx = shutil.which("npx")
    if npx is None:
        print("Lets Box local bridge requires npx.", file=sys.stderr)
        return 69
    child_environment = os.environ.copy()
    if credentials is not None:
        child_environment[EPS_EMAIL_ENV] = credentials.eps_account_email
        child_environment[SERPAPI_KEY_ENV] = credentials.serpapi_key
    try:
        os.execvpe(npx, build_mcp_command(credentials is not None), child_environment)
    except OSError:
        print("Lets Box local bridge could not start mcp-remote.", file=sys.stderr)
        return 69
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
