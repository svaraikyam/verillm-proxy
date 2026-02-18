from google.cloud import kms
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed

PROJECT_ID = "verillm-prod"
LOCATION_ID = "asia-south1"
KEY_RING_ID = "verillm-keyring"
KEY_ID = "verillm-signing-key"
KEY_VERSION = "1"

def get_key_version_path():
    client = kms.KeyManagementServiceClient()
    return client.crypto_key_version_path(
        PROJECT_ID,
        LOCATION_ID,
        KEY_RING_ID,
        KEY_ID,
        KEY_VERSION,
    )

def sign_hash(session_hash: str) -> str:
    client = kms.KeyManagementServiceClient()
    name = get_key_version_path()

    digest = {"sha256": bytes.fromhex(session_hash)}

    response = client.asymmetric_sign(
        request={"name": name, "digest": digest}
    )

    return response.signature.hex()

def get_public_key_pem():
    client = kms.KeyManagementServiceClient()
    name = get_key_version_path()
    public_key = client.get_public_key(request={"name": name})
    return public_key.pem

def verify_signature(session_hash: str, signature_hex: str) -> bool:
    public_key_pem = get_public_key_pem()

    public_key = serialization.load_pem_public_key(
        public_key_pem.encode()
    )

    try:
        public_key.verify(
            bytes.fromhex(signature_hex),
            bytes.fromhex(session_hash),
            padding.PKCS1v15(),
            Prehashed(hashes.SHA256())
        )
        return True
    except Exception as e:
        print("SIGNATURE VERIFY ERROR:", str(e))
        return False