import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

def get_aes_key(base64_key: str) -> bytes:
    try:
        raw = base64.b64decode(base64_key + "===")
        return raw[:32]
    except Exception as e:
        raise ValueError(f"Invalid AES key: {e}")

def encrypt_message(base64_key: str, plaintext: str) -> str:
    try:
        key = base64.b64decode(base64_key)
        iv = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        ciphertext = cipher.encrypt(pad(plaintext.encode("utf-8"), AES.block_size))
        return base64.b64encode(iv + ciphertext).decode()
    except Exception as e:
        print("Encryption failed:", e)
        raise e

def decrypt_message(base64_key: str, b64_cipher: str) -> str:
    try:
        key = base64.b64decode(base64_key)
        raw = base64.b64decode(b64_cipher)
        iv = raw[:16]
        ciphertext = raw[16:]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(ciphertext), AES.block_size)
        return decrypted.decode("utf-8")
    except Exception as e:
        print("Decryption failed:", e)
        raise e
