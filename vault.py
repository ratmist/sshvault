from pathlib import Path
from crypto import encrypt, decrypt, derive_key
import json
import os

VAULT_DIR = Path.home() / ".sshvault"
VAULT_FILE = VAULT_DIR / "vault.bin"
SALT_FILE = VAULT_DIR / "salt.bin"

DEFAULT_VAULT_DATA = {
    "version": 1,
    "services": {}
}

class Vault:

    def __init__(self, path: Path, data: dict, key: bytes):
        self.path = path
        self.version = data["version"]
        self.services = data["services"]
        self._key = key

    @staticmethod
    def exists() -> bool:
        return VAULT_FILE.exists() and SALT_FILE.exists()
    
    @classmethod
    def open_or_create(cls, master_password: str):
        VAULT_DIR.mkdir(parents=True, exist_ok=True)

        if not SALT_FILE.exists():
            salt = os.urandom(16)
            SALT_FILE.write_bytes(salt)
        else:
            salt = SALT_FILE.read_bytes()

        key = derive_key(master_password, salt)

        if not VAULT_FILE.exists():
            encrypted = encrypt(DEFAULT_VAULT_DATA, key)
            VAULT_FILE.write_bytes(encrypted)
            data = DEFAULT_VAULT_DATA.copy()
        else:
            blob = VAULT_FILE.read_bytes()
            data = decrypt(blob, key)

            return cls(VAULT_FILE, data, key)

    def save(self):
        encrypted = encrypt(self.to_dict(), self._key)
        self.path.write_bytes(encrypted)

    def add_service(self, name: str, service: dict):
        if name in self.services:
            raise ValueError('Service already exists')
        
        self.services[name] = service

    def del_service(self, name: str,):
        if name not in self.services:
            raise ValueError("Service not found")
        
        del self.services[name]

    def list_services(self) -> list[str]:
        return list(self.services.keys())
    
    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "services": self.services
        }
    
    def change_master_password(self, old_password: str, new_password: str):
        old_salt = SALT_FILE.read_bytes()
        old_key = derive_key(old_password, old_salt)

        blob = self.path.read_bytes()
        data = decrypt(blob, old_key)

        new_salt = os.urandom(16)
        SALT_FILE.write_bytes(new_salt)
        new_key = derive_key(new_password, new_salt)

        encrypted = encrypt(data, new_key)
        self.path.write_bytes(encrypted)

        self._key = new_key

    def update_service(self, name: str, **fields):
        if name not in self.services:
            raise ValueError("Service not found")
    
        self.services[name].update(fields)