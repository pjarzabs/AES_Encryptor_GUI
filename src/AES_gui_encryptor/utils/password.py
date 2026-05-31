from __future__ import annotations
import secrets
import string


DEFAULT_ALPHABET = (
    string.ascii_letters +
    string.digits +
    "!@#$%^&*()-_=+[]{};:,.?/<>"
)

def generate_password(length: int = 20, alphabet: str = DEFAULT_ALPHABET) -> str:
    if length < 8:
        length = 8
    return "".join(secrets.choice(alphabet) for _ in range(length))