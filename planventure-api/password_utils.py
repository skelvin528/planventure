import bcrypt


def generate_salt() -> bytes:
    return bcrypt.gensalt()


def hash_password(password: str, salt: bytes | None = None) -> str:
    password_bytes = password.encode("utf-8")
    password_hash = bcrypt.hashpw(password_bytes, salt or generate_salt())
    return password_hash.decode("utf-8")


def check_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(
        password.encode("utf-8"),
        password_hash.encode("utf-8"),
    )
