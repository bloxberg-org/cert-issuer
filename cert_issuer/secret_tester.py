import requests

from cert_issuer.signer import FileSecretManager
from cert_issuer.config import get_config
from path_tools import get_pk_path


secret_path = get_pk_path()
secret = FileSecretManager("x", secret_path)
print(secret.issuing_address)
print(secret.path_to_secret)
print(secret.signer)