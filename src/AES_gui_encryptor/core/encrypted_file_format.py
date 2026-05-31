from __future__ import annotations

import base64
import struct
from dataclasses import dataclass
from ..config import (
    FORMAT_MAGIC,
    FORMAT_VERSION,
    KDF_ID_PBKDF2_SHA256,
    CIPHER_ID_AES_256_GCM,
)
from .errors import InvalidFormatError, UnsupportedVersionError
from .crypto import CryptoMeta, decrypt_bytes
from cryptography.exceptions import InvalidTag


# Binary container format (v1):
# [magic:4][ver:1][kdf_id:1][cipher_id:1][iters:u32be][salt_len:u8][nonce_len:u8][salt][nonce][ciphertext...]
#
# AAD = header bytes up to end of nonce (everything except ciphertext). This authenticates metadata too.


@dataclass(frozen=True)
class ContainerMeta:
    version: int
    kdf_id: int
    cipher_id: int
    iterations: int
    salt: bytes
    nonce: bytes


def _build_header(meta: ContainerMeta) -> bytes:
    if meta.version != FORMAT_VERSION:
        raise UnsupportedVersionError(f"Unsupported container version: {meta.version}")

    if meta.kdf_id != KDF_ID_PBKDF2_SHA256:
        raise InvalidFormatError(f"Unsupported KDF id: {meta.kdf_id}")

    if meta.cipher_id != CIPHER_ID_AES_256_GCM:
        raise InvalidFormatError(f"Unsupported cipher id: {meta.cipher_id}")

    if not (0 < len(meta.salt) < 256):
        raise ValueError("Salt length invalid.")
    if not (0 < len(meta.nonce) < 256):
        raise ValueError("Nonce length invalid.")

    fixed = struct.pack(
        ">4sBBBIBB",
        FORMAT_MAGIC,
        meta.version,
        meta.kdf_id,
        meta.cipher_id,
        meta.iterations,
        len(meta.salt),
        len(meta.nonce),
    )
    return fixed + meta.salt + meta.nonce


def pack_container(ciphertext: bytes, meta: ContainerMeta) -> bytes:
    header = _build_header(meta)
    return header + ciphertext


def unpack_container(data: bytes) -> tuple[bytes, ContainerMeta, bytes]:
    """Returns: ciphertext, meta, aad(header bytes)"""
    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("Data must be bytes.")
    data = bytes(data)

    if len(data) < 4 + 1 + 1 + 1 + 4 + 1 + 1:
        raise InvalidFormatError("Data too short.")

    magic = data[:4]
    if magic != FORMAT_MAGIC:
        raise InvalidFormatError("Magic mismatch (not an AGF1 container).")

    # Parse fixed header
    # >4sBBBIBB matches:
    # magic(4), ver(1), kdf_id(1), cipher_id(1), iters(u32), salt_len(u8), nonce_len(u8)
    fixed_len = struct.calcsize(">4sBBBIBB")
    magic, ver, kdf_id, cipher_id, iters, salt_len, nonce_len = struct.unpack(">4sBBBIBB", data[:fixed_len])

    if ver != FORMAT_VERSION:
        raise UnsupportedVersionError(f"Unsupported container version: {ver}")

    offset = fixed_len
    need = offset + salt_len + nonce_len
    if len(data) < need:
        raise InvalidFormatError("Truncated header.")

    salt = data[offset : offset + salt_len]
    offset += salt_len
    nonce = data[offset : offset + nonce_len]
    offset += nonce_len

    aad = data[:offset]
    ciphertext = data[offset:]
    if len(ciphertext) == 0:
        raise InvalidFormatError("Missing ciphertext payload.")

    meta = ContainerMeta(
        version=ver,
        kdf_id=kdf_id,
        cipher_id=cipher_id,
        iterations=iters,
        salt=salt,
        nonce=nonce,
    )
    return ciphertext, meta, aad


def maybe_decode_base64(raw: bytes) -> bytes:
    """
    If raw is a valid container -> return raw.
    Else, try base64 decode -> if valid container -> return decoded.
    Else raise InvalidFormatError.
    """
    # Try direct
    try:
        _ = unpack_container(raw)
        return raw
    except Exception:
        pass

    # Try base64 (strip whitespace)
    try:
        stripped = b"".join(raw.split())
        decoded = base64.b64decode(stripped, validate=True)
        _ = unpack_container(decoded)
        return decoded
    except Exception as e:
        raise InvalidFormatError("Input is not a valid container (raw or base64).") from e


def encrypt_to_container(plaintext: bytes, password: str, *, iterations: int, salt: bytes, nonce: bytes, encrypt_fn) -> bytes:
    """
    Helper: build header first and use it as AAD.
    encrypt_fn must be: (nonce, plaintext, aad) -> ciphertext
    """
    meta = ContainerMeta(
        version=FORMAT_VERSION,
        kdf_id=KDF_ID_PBKDF2_SHA256,
        cipher_id=CIPHER_ID_AES_256_GCM,
        iterations=iterations,
        salt=salt,
        nonce=nonce,
    )
    header = _build_header(meta)
    ciphertext = encrypt_fn(nonce, plaintext, header)
    return pack_container(ciphertext, meta)


def decrypt_container(data: bytes, password: str) -> bytes:
    ciphertext, meta, aad = unpack_container(data)
    crypto_meta = CryptoMeta(salt=meta.salt, nonce=meta.nonce, iterations=meta.iterations)
    try:
        return decrypt_bytes(ciphertext, password, crypto_meta, aad=aad)
    except InvalidTag as e:
        # wrong password OR file modified
        from .errors import WrongPasswordOrCorruptedFileError
        raise WrongPasswordOrCorruptedFileError("Wrong password or corrupted file.") from e