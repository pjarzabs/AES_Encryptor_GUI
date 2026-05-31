from __future__ import annotations

import base64
import struct
from dataclasses import dataclass

from cryptography.exceptions import InvalidTag

from ..config import (
    FORMAT_MAGIC,
    FORMAT_VERSION,
    KDF_ID_PBKDF2_SHA256,
    CIPHER_ID_AES_256_GCM,
)
from .crypto import CryptoMeta, decrypt_bytes
from .errors import (
    InvalidFormatError,
    UnsupportedVersionError,
    WrongPasswordOrCorruptedFileError,
)


# Format pliku (wersja 1):
# [magic:4][ver:1][kdf_id:1][cipher_id:1][iters:u32be]
# [salt_len:u8][nonce_len:u8][salt][nonce][ciphertext...]

# AAD = wszystkie bajty nagłówka (wszystko oprócz zaszyfrowanych danych).


@dataclass(frozen=True)
class FileFormatMeta:
    version: int
    kdf_id: int
    cipher_id: int
    iterations: int
    salt: bytes
    nonce: bytes


def _build_header(meta: FileFormatMeta) -> bytes:
    if meta.version != FORMAT_VERSION:
        raise UnsupportedVersionError(
            f"Nieobsługiwana wersja formatu pliku: {meta.version}"
        )

    if meta.kdf_id != KDF_ID_PBKDF2_SHA256:
        raise InvalidFormatError(
            f"Nieobsługiwany identyfikator KDF: {meta.kdf_id}"
        )

    if meta.cipher_id != CIPHER_ID_AES_256_GCM:
        raise InvalidFormatError(
            f"Nieobsługiwany identyfikator szyfru: {meta.cipher_id}"
        )

    if not (0 < len(meta.salt) < 256):
        raise ValueError("Nieprawidłowa długość soli.")

    if not (0 < len(meta.nonce) < 256):
        raise ValueError("Nieprawidłowa długość nonce.")

    fixed_header = struct.pack(
        ">4sBBBIBB",
        FORMAT_MAGIC,
        meta.version,
        meta.kdf_id,
        meta.cipher_id,
        meta.iterations,
        len(meta.salt),
        len(meta.nonce),
    )

    return fixed_header + meta.salt + meta.nonce


def build_file_format(
    ciphertext: bytes,
    meta: FileFormatMeta,
) -> bytes:
    header = _build_header(meta)
    return header + ciphertext


def parse_file_format(
    data: bytes,
) -> tuple[bytes, FileFormatMeta, bytes]:
    """
    Zwraca:
        zaszyfrowane dane,
        metadane,
        AAD (bajty nagłówka)
    """

    if not isinstance(data, (bytes, bytearray)):
        raise TypeError("Dane muszą być typu bytes.")

    data = bytes(data)

    minimum_header_size = 4 + 1 + 1 + 1 + 4 + 1 + 1

    if len(data) < minimum_header_size:
        raise InvalidFormatError("Dane są zbyt krótkie.")

    if data[:4] != FORMAT_MAGIC:
        raise InvalidFormatError(
            "Nieprawidłowy nagłówek pliku (błędna sygnatura)."
        )

    fixed_header_size = struct.calcsize(">4sBBBIBB")

    (
        _magic,
        version,
        kdf_id,
        cipher_id,
        iterations,
        salt_len,
        nonce_len,
    ) = struct.unpack(
        ">4sBBBIBB",
        data[:fixed_header_size],
    )

    if version != FORMAT_VERSION:
        raise UnsupportedVersionError(
            f"Nieobsługiwana wersja formatu pliku: {version}"
        )

    offset = fixed_header_size

    required_size = offset + salt_len + nonce_len

    if len(data) < required_size:
        raise InvalidFormatError(
            "Nagłówek pliku jest niekompletny."
        )

    salt = data[offset: offset + salt_len]
    offset += salt_len

    nonce = data[offset: offset + nonce_len]
    offset += nonce_len

    aad = data[:offset]

    ciphertext = data[offset:]

    if not ciphertext:
        raise InvalidFormatError(
            "Brak zaszyfrowanych danych w pliku."
        )

    metadata = FileFormatMeta(
        version=version,
        kdf_id=kdf_id,
        cipher_id=cipher_id,
        iterations=iterations,
        salt=salt,
        nonce=nonce,
    )

    return ciphertext, metadata, aad


def decode_base64(raw: bytes) -> bytes:
    """
    Akceptuje:
      - zaszyfrowany plik binarny
      - zaszyfrowany plik zapisany w Base64
    """

    try:
        parse_file_format(raw)
        return raw

    except Exception:
        pass

    try:
        stripped = b"".join(raw.split())

        decoded = base64.b64decode(
            stripped,
            validate=True,
        )

        parse_file_format(decoded)

        return decoded

    except Exception as exc:
        raise InvalidFormatError(
            "Plik nie jest prawidłowym zaszyfrowanym plikiem "
            "(format binarny lub Base64)."
        ) from exc


def encrypt_to_file_format(
    plaintext: bytes,
    *,
    iterations: int,
    salt: bytes,
    nonce: bytes,
    encrypt_fn,
) -> bytes:
    metadata = FileFormatMeta(
        version=FORMAT_VERSION,
        kdf_id=KDF_ID_PBKDF2_SHA256,
        cipher_id=CIPHER_ID_AES_256_GCM,
        iterations=iterations,
        salt=salt,
        nonce=nonce,
    )

    header = _build_header(metadata)

    ciphertext = encrypt_fn(
        nonce,
        plaintext,
        header,
    )

    return build_file_format(
        ciphertext,
        metadata,
    )


def decrypt_from_file_format(
    data: bytes,
    password: str,
) -> bytes:
    ciphertext, metadata, aad = parse_file_format(data)

    crypto_meta = CryptoMeta(
        salt=metadata.salt,
        nonce=metadata.nonce,
        iterations=metadata.iterations,
    )

    try:
        return decrypt_bytes(
            ciphertext,
            password,
            crypto_meta,
            aad=aad,
        )

    except InvalidTag as exc:
        raise WrongPasswordOrCorruptedFileError(
            "Nieprawidłowe hasło lub uszkodzony plik."
        ) from exc
