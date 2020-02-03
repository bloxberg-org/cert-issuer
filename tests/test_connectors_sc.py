import cert_issuer.blockchain_handlers.ethereum_sc.ens
import unittest
import json
from cert_issuer import config
app_config = config.get_config()
with open("/home/xenia/Documents/PAS/cert-issuer/data/blockchain_certificates/4e7d75c5-281c-45de-93cc-3212b1349ee9.json", "r") as read_file
data = json.loads(read_file)


class TestSign(unittest.TestCase):
    """
    Tests if the anchor is being set correct
    """
    def test_ens_name(self):
        app_config.ens_name == data

    def test_contract_name(self):


if __name__ == "__main__":
    unittest.main()
    print("Everything passed")