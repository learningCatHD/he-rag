from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import hashlib
import json
import time

SECRET = '2WMuLu.f9My8cCAARrXhngqQ*8R24ump'  # 32 字符的密钥
algorithm = algorithms.AES
key = hashlib.sha256(SECRET.encode()).digest()[:32]

TOKEN_EXPIRE = 7 * 24 * 60 * 60 * 1000  # 7天过期，单位毫秒
ADMIN_TOKEN_EXPIRE = 2 * 24 * 60 * 60 * 1000  # 2天过期，单位毫秒

def generate_iv():
    random_str = str(int(time.time() * 1000))
    iv = hashlib.md5(random_str.encode()).digest()[:16]
    return iv

def encrypt(text):
    iv = generate_iv()  # 生成基于时间戳的 IV
    cipher = Cipher(algorithm(key), modes.CTR(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(text.encode()) + encryptor.finalize()
    return {
        'encrypted': ciphertext.hex(),
        'iv': iv.hex()
    }

def decrypt(encrypted_text, iv_hex):
    iv_bytes = bytes.fromhex(iv_hex)
    cipher = Cipher(algorithm(key), modes.CTR(iv_bytes), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted = decryptor.update(bytes.fromhex(encrypted_text)) + decryptor.finalize()
    return decrypted.decode()

def generate_session_token(phone):
    session = {
        'phone': phone,
        'signin_timestamp': int(round(time.time() * 1000)) - 5000 # 当前时间戳毫秒级 减去5000 有时前端时间比后端时间快 bug？
    }
    session_str = json.dumps(session)
    session_cipher = encrypt(session_str)
    token = f"{session_cipher['iv']}-{session_cipher['encrypted']}"
    return token

def parse_session_token(token):
    if not re.match(r'[0-9a-f]{32}-[0-9a-f]+', token):
        return {'status': 1}

    iv, encrypted = token.split('-')
    try:
        session_str = decrypt(encrypted, iv)
        session = json.loads(session_str)
        phone = session['phone']
        signin_timestamp = session['signin_timestamp']
    except Exception:
        return {'status': 2}

    now = int(round(time.time() * 1000))
    if now - signin_timestamp < 0:
        return {'status': 4, 'phone': phone}

    if now - signin_timestamp > ADMIN_TOKEN_EXPIRE:
        return {'status': 5, 'phone': phone}

    return {'status': 0, 'phone': phone}

def generate_random_hash():
    random_str = str(int(time.time() * 1000))
    return hashlib.md5(random_str.encode()).digest()[:16].hex()
