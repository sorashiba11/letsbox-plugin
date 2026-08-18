#!/usr/bin/env python3
"""Interactively configure Lets Box local Remote MCP credentials.

The SerpApi key is collected with terminal echo disabled. Use ``--stdin-json``
only for an already-secured local automation channel; neither mode prints the
submitted values.
"""

from __future__ import annotations

import argparse
import getpass
import json
import sys

from local_credentials import CredentialError, LocalCredentials, write_credentials


def parse_arguments(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Configure Lets Box Remote MCP credentials.")
    parser.add_argument(
        "--stdin-json",
        action="store_true",
        help="Read {eps_account_email, serpapi_key} from stdin without echoing it.",
    )
    return parser.parse_args(argv)


def read_input(stdin_json: bool) -> LocalCredentials:
    if stdin_json:
        document = json.load(sys.stdin)
        if not isinstance(document, dict):
            raise CredentialError("Credential input must be a JSON object.")
        email = document.get("eps_account_email")
        key = document.get("serpapi_key")
        if not isinstance(email, str) or not isinstance(key, str):
            raise CredentialError("Credential input is incomplete.")
        return LocalCredentials(eps_account_email=email, serpapi_key=key)
    email = getpass.getpass("EPS account email: ")
    key = getpass.getpass("SerpApi key: ")
    return LocalCredentials(eps_account_email=email, serpapi_key=key)


def main(argv: list[str] | None = None) -> int:
    try:
        arguments = parse_arguments(argv or sys.argv[1:])
        credentials = read_input(arguments.stdin_json)
        path = write_credentials(credentials)
    except (CredentialError, EOFError, OSError, ValueError, json.JSONDecodeError):
        print("Unable to save Lets Box local credentials.", file=sys.stderr)
        return 2
    print(f"Lets Box local credentials saved: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
