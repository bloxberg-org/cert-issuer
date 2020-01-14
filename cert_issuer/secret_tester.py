import requests

from cert_issuer.models import SecretManager
from cert_issuer.signer import FileSecretManager
from cert_issuer.config import get_config

secret = FileSecretManager("x", "/home/xenia/key.txt")
print(secret.issuing_address)
print(secret.path_to_secret)
print(secret.signer)