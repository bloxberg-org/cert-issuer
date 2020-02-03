import unittest
import json
import glob
from cert_issuer import config
app_config = config.get_config()
cert_list = glob.glob(app_config.blockchain_certificates_dir+"*.json")


class TestSign(unittest.TestCase):
    """
    Tests if the anchor is being set correct
    """
    def test_ens_name(self):
        app_config.ens_name == data['signature']['anchors'][0]['ens_name']

    def test_contract_name(self):
        app_config.contract_address == data['signature']['anchors'][0]['sourceId']


if __name__ == "__main__":
    for i in range(len(cert_list)):
        read_file = open(cert_list[i], "r")
        data = json.load(read_file)
        unittest.main(argv=['first-arg-is-ignored'], exit=False)