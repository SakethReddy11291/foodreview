import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")

from app.core.security import (  # noqa: E402
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_password_hash_and_verify():
    hashed = hash_password("secret123")
    assert hashed != "secret123"
    assert verify_password("secret123", hashed)
    assert not verify_password("wrong-pass", hashed)


def test_token_roundtrip():
    token = create_access_token(42)
    assert decode_access_token(token) == 42
    assert decode_access_token("not-a-token") is None
