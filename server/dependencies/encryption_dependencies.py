from base64 import b64encode, b64decode
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

from typing import Dict

def encrypt_aes_gcm(plaintext: str, key_b64: str) -> Dict:
    key = b64decode(key_b64)
    iv = os.urandom(12)
    aesgcm = AESGCM(key)
    ct = aesgcm.encrypt(iv, plaintext.encode(), None)
    return {
        "ciphertext": b64encode(ct).decode(),
        "iv": b64encode(iv).decode()
    }

def decrypt_aes_gcm(ciphertext_b64: str, iv_b64: str, key_b64: str) -> str:
    key = b64decode(key_b64)
    iv = b64decode(iv_b64)
    ciphertext = b64decode(ciphertext_b64)
    
    print(f"[DEBUG] Key (len={len(key)}): {key.hex()}")
    print(f"[DEBUG] IV (len={len(iv)}): {iv.hex()}")
    print(f"[DEBUG] Ciphertext (len={len(ciphertext)}): {ciphertext.hex()}")
    
    
    
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(iv, ciphertext, None).decode()