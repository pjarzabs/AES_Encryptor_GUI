from __future__ import annotations

import base64
import os
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from ..config import PBKDF2_ITERATIONS, SALT_LEN, NONCE_LEN
from .encrypted_file_format import encrypt_to_file_format, decrypt_from_file_format, decode_base64
from .crypto import derive_key


def encrypt_file(
    input_path: str,
    output_path: str,
    password: str,
    *,
    as_base64: bool,
    output_ext: str,
) -> str:
    plaintext = Path(input_path).read_bytes()

    salt = os.urandom(SALT_LEN)
    nonce = os.urandom(NONCE_LEN)
    key = derive_key(password, salt, PBKDF2_ITERATIONS)
    aesgcm = AESGCM(key)

    encrypted = encrypt_to_file_format(
        plaintext=plaintext,
        iterations=PBKDF2_ITERATIONS,
        salt=salt,
        nonce=nonce,
        encrypt_fn=lambda n, p, aad: aesgcm.encrypt(n, p, aad),
    )

    if as_base64:
        encrypted = base64.b64encode(encrypted) + b"\n"

    final_path = _with_extension(output_path, output_ext)
    Path(final_path).write_bytes(encrypted)

    return final_path


def decrypt_file(input_path: str, output_path: str, password: str) -> str:
    raw = Path(input_path).read_bytes()
    data = decode_base64(raw)
    plaintext = decrypt_from_file_format(data, password)

    Path(output_path).write_bytes(plaintext)
    return output_path


def normalize_extension(ext: str) -> str:
    ext = (ext or "").strip()

    if not ext:
        return ".aes"

    if not ext.startswith("."):
        return "." + ext

    return ext


def _with_extension(path: str, ext: str) -> str:
    ext = normalize_extension(ext)

    if path.lower().endswith(ext.lower()):
        return path

    return path + ext