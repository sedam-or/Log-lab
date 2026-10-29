from __future__ import annotations

import hashlib
import hmac
import secrets

_SCRYPT_N = 1 << 14
_SCRYPT_R = 8
_SCRYPT_P = 1
_SCRYPT_MAXMEM = 128 * 1024 * 1024


def hash_password(password: str, salt: bytes | None = None) -> str:
    if len(password) < 12:
        raise ValueError("password must contain at least 12 characters")
    salt = salt or secrets.token_bytes(16)
    derived = hashlib.scrypt(password.encode(), salt=salt, n=_SCRYPT_N, r=_SCRYPT_R,
                             p=_SCRYPT_P, dklen=32, maxmem=_SCRYPT_MAXMEM)
    return f"scrypt${_SCRYPT_N}${_SCRYPT_R}${_SCRYPT_P}${salt.hex()}${derived.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, n_text, r_text, p_text, salt_hex, expected = encoded.split("$", 5)
        if algorithm != "scrypt":
            return False
        n, r, p = int(n_text), int(r_text), int(p_text)
        if n < 1 << 14 or n > 1 << 16 or n & (n - 1) or r != 8 or not 1 <= p <= 2:
            return False
        salt = bytes.fromhex(salt_hex)
        if len(salt) != 16 or len(expected) != 64:
            return False
        actual = hashlib.scrypt(password.encode(), salt=salt, n=n, r=r, p=p,
                                dklen=32, maxmem=_SCRYPT_MAXMEM).hex()
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError, OverflowError):
        return False


def pseudonym(key: bytes, namespace: str, value: str) -> str:
    normalized = value.strip().casefold().encode("utf-8")
    return hmac.new(key, namespace.encode() + b":" + normalized, hashlib.sha256).hexdigest()


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
