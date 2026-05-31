from __future__ import annotations

import os
from dataclasses import dataclass

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from ..config import KEY_LEN, NONCE_LEN, SALT_LEN, PBKDF2_ITERATIONS


@dataclass(frozen=True)
class CryptoMeta:
    salt: bytes
    nonce: bytes
    iterations: int


def derive_key(password: str, salt: bytes, iterations: int) -> bytes:
    if not isinstance(password, str) or password == "":
        raise ValueError("Password must be a non-empty string.")

    if not isinstance(salt, (bytes, bytearray)):
        raise TypeError("Salt must be bytes.")

    if len(salt) != SALT_LEN:
        raise ValueError(f"Salt must have length {SALT_LEN} bytes.")

    if iterations < 10_000:
        raise ValueError("Iterations too small.")

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LEN,
        salt=salt,
        iterations=iterations,
    )

    return kdf.derive(password.encode("utf-8"))


def encrypt_bytes(
    plaintext: bytes,
    password: str,
    *,
    aad: bytes | None = None,
    iterations: int = PBKDF2_ITERATIONS,
) -> tuple[bytes, CryptoMeta]:
    if not isinstance(plaintext, (bytes, bytearray)):
        raise TypeError("Plaintext must be bytes.")

    salt = os.urandom(SALT_LEN)
    nonce = os.urandom(NONCE_LEN)

    key = derive_key(password, salt, iterations)

    ciphertext = AESGCM(key).encrypt(
        nonce,
        bytes(plaintext),
        aad,
    )

    return ciphertext, CryptoMeta(
        salt=salt,
        nonce=nonce,
        iterations=iterations,
    )


def decrypt_bytes(
    ciphertext: bytes,
    password: str,
    meta: CryptoMeta,
    *,
    aad: bytes | None = None,
) -> bytes:
    if not isinstance(ciphertext, (bytes, bytearray)):
        raise TypeError("Ciphertext must be bytes.")

    key = derive_key(
        password,
        meta.salt,
        meta.iterations,
    )

    return AESGCM(key).decrypt(
        meta.nonce,
        bytes(ciphertext),
        aad,
    )