"""Read and atomically write Lets Box local Remote MCP credentials.

This module is intentionally stdlib-only. The credential file lives below the
Codex home directory, outside the plugin cache and outside any Git checkout.
No function in this module prints credential values.
"""

from __future__ import annotations

import json
import os
import secrets
import stat
import tempfile
from dataclasses import dataclass
from pathlib import Path


PLUGIN_DATA_DIRNAME = "plugin-data/letsbox"
CREDENTIALS_FILENAME = "credentials.json"
MAX_EMAIL_LENGTH = 320
MAX_KEY_LENGTH = 4096


class CredentialError(ValueError):
    """A safe, non-secret configuration error."""


@dataclass(frozen=True)
class LocalCredentials:
    eps_account_email: str
    serpapi_key: str


def codex_home() -> Path:
    configured = os.environ.get("CODEX_HOME", "").strip()
    if configured:
        return Path(configured).expanduser().resolve()
    return (Path.home() / ".codex").resolve()


def credentials_path() -> Path:
    return codex_home() / PLUGIN_DATA_DIRNAME / CREDENTIALS_FILENAME


def validate_credentials(eps_account_email: str, serpapi_key: str) -> LocalCredentials:
    email = eps_account_email.strip().lower()
    key = serpapi_key.strip()
    if (
        not email
        or len(email) > MAX_EMAIL_LENGTH
        or any(character.isspace() for character in email)
        or email.count("@") != 1
        or email.startswith("@")
        or email.endswith("@")
        or "." not in email.rsplit("@", 1)[1]
    ):
        raise CredentialError("The EPS account email is invalid.")
    if not key or len(key) > MAX_KEY_LENGTH or any(ord(character) < 32 for character in key):
        raise CredentialError("The SerpApi key is invalid.")
    return LocalCredentials(eps_account_email=email, serpapi_key=key)


def write_credentials(credentials: LocalCredentials) -> Path:
    validated = validate_credentials(credentials.eps_account_email, credentials.serpapi_key)
    path = credentials_path()
    directory = path.parent
    data_root = codex_home() / "plugin-data"
    data_root.mkdir(parents=True, mode=0o700, exist_ok=True)
    os.chmod(data_root, 0o700)
    directory.mkdir(parents=True, mode=0o700, exist_ok=True)
    os.chmod(directory, 0o700)

    payload = json.dumps(
        {
            "version": 1,
            "eps_account_email": validated.eps_account_email,
            "serpapi_key": validated.serpapi_key,
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )
    temporary_path: Path | None = None
    try:
        file_descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{CREDENTIALS_FILENAME}.{secrets.token_hex(8)}.",
            dir=directory,
            text=True,
        )
        temporary_path = Path(temporary_name)
        os.fchmod(file_descriptor, 0o600)
        with os.fdopen(file_descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
        temporary_path = None
        os.chmod(path, 0o600)
        return path
    finally:
        if temporary_path is not None:
            try:
                temporary_path.unlink()
            except FileNotFoundError:
                pass


def read_credentials(path: Path | None = None) -> LocalCredentials:
    target = path or credentials_path()
    file_descriptor: int | None = None
    try:
        open_flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        file_descriptor = os.open(target, open_flags)
    except FileNotFoundError as error:
        raise CredentialError("Lets Box local credentials are not configured.") from error
    except OSError as error:
        raise CredentialError("Lets Box local credentials file cannot be opened safely.") from error
    try:
        file_stat = os.fstat(file_descriptor)
        if not stat.S_ISREG(file_stat.st_mode):
            raise CredentialError("Lets Box local credentials file is not a regular file.")
        if file_stat.st_uid != os.getuid() or stat.S_IMODE(file_stat.st_mode) != 0o600:
            raise CredentialError("Lets Box local credentials file permissions are unsafe.")
        with os.fdopen(file_descriptor, "r", encoding="utf-8") as handle:
            file_descriptor = None
            document = json.load(handle)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise CredentialError("Lets Box local credentials file cannot be read.") from error
    finally:
        if file_descriptor is not None:
            os.close(file_descriptor)
    if not isinstance(document, dict) or document.get("version") != 1:
        raise CredentialError("Lets Box local credentials file has an unsupported format.")
    email = document.get("eps_account_email")
    key = document.get("serpapi_key")
    if not isinstance(email, str) or not isinstance(key, str):
        raise CredentialError("Lets Box local credentials file is incomplete.")
    return validate_credentials(email, key)


def is_configured(path: Path | None = None) -> bool:
    try:
        read_credentials(path)
    except CredentialError:
        return False
    return True
