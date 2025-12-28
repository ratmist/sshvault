from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from argon2.low_level import hash_secret_raw, Type
import os
import json

ARGON_PARAMS = {
    "time_cost": 3,
    "memory_cost": 64 * 1024, 
    "parallelism": 2,
    "hash_len": 32,
    "type": Type.ID,
}

def derive_key(password: str, salt: bytes) -> bytes:
    return hash_secret_raw(
        password.encode(),
        salt,
        **ARGON_PARAMS
    )

def encrypt(data: dict, key: bytes) -> bytes:
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)

    plaintext = json.dumps(data).encode()
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)

    return nonce + ciphertext

def decrypt(blob: bytes, key: bytes) -> dict:
    aesgcm = AESGCM(key)

    nonce = blob[:12]
    ciphertext = blob[12:]

    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return json.loads(plaintext)