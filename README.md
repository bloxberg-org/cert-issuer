[![Build Status](https://travis-ci.org/blockchain-certificates/cert-issuer.svg?branch=master)](https://travis-ci.org/blockchain-certificates/cert-issuer)
[![PyPI version](https://badge.fury.io/py/cert-issuer.svg)](https://badge.fury.io/py/cert-issuer)



# cert-issuer

The cert-issuer project issues blockchain certificates by creating a transaction from the issuing institution to the
recipient on the Bitcoin blockchain that includes the hash of the certificate itself. 

## Issuing certificates

1. Add your certificates to /cert-issuer/data/unsigned_certificates/. 

    ```
    # To use a sample unsigned certificate as follows:
    cp /cert-issuer/examples/data-testnet/unsigned_certificates/3bc1a96a-3501-46ed-8f75-49612bbac257.json /cert-issuer/data/unsigned_certificates/ 
    
    # If you created your own unsigned certificate using cert-tools (assuming you placed it under data/unsigned_certificates):
    cp <cert-issuer-home>/data/unsigned_certificates/<your-cert-guid>.json /etc/cert-issuer/data/unsigned_certificates/
    ```

2. Make sure you have enough ETH in your issuing address.

    a. Go to https://faucet.bloxberg.org and enter your bloxberg address to receive bergs.

3. Issue the certificates on the blockchain

    ```
    cert-issuer -c /etc/cert-issuer/conf.ini
    ```
    
4. Your Blockchain certificates are located in `/etc/cert-issuer/data/blockchain_certificates`. Copy these to your local machine, and add them to cert-viewer's `cert_data` folder to see your certificates in the Certificate Viewer.

```
docker ps  // shows the docker containerId
docker cp <containerId>:/etc/cert-issuer/data/blockchain_certificates <localPath>/cert-viewer/cert_data
```

# How batch issuing works

While it is possible to issue one certificate with one Ethereum transaction, it is far more efficient to use one Ethereum transaction to issue a batch of certificates. 

The issuer builds a Merkle tree of certificate hashes and registers the Merkle root as the cryptographic identifier in an Ethereum smart contract. 

Suppose the batch contains `n` certificates, and certificate `i` contains recipient `i`'s information. The issuer hashes each certificate and combines them into a Merkle tree:

![](img/merkle.png)


The root of the Merkle tree, which is a 256-bit hash, is issued on the bloxberg blockchain. 

The Blockchain Certificate given to recipient `i` contains a [2019 Merkle Proof Signature Suite](https://w3c-ccg.github.io/lds-merkle-proof-2019/)-formatted signature, proving that certificate `i` is contained in the Merkle tree. 

![](img/blockchain_certificate_components.png)

This receipt contains:

*   The Ethereum transaction ID storing the Merkle root
*   The expected Merkle root on the blockchain
*   The expected hash for recipient `i`'s certificate
*   The Merkle path from recipient `i`'s certificate to the Merkle root, i.e. the path highlighted in orange above. `h_i -> … -> Merkle root`

The [verification process](https://github.com/blockchain-certificates/cert-verifier-js#verification-process) performs computations to check that:

*   The hash of certificate `i` matches the value in the receipt
*   The Merkle path is valid
*   The Merkle root stored on the blockchain matches the value in the receipt

These steps establish that the certificate has not been tampered with since it was issued.

## Hashing a certificate

The Blockchain Certificate JSON contents without the `signature` node is the certificate that the issuer created. This is the value needed to hash for comparison against the receipt. Because there are no guarantees about ordering or formatting of JSON, first canonicalize the certificate (without the `signature`) against the JSON LD schema. This allows us to obtain a deterministic hash across platforms.

The detailed steps are described in the [verification process](https://github.com/blockchain-certificates/cert-verifier-js#verification-process).


## What should be in a batch?

How a batch is defined can vary, but it should be defined such that it changes infrequently. For example, “2016 MIT grads” would be preferred over “MIT grads” (the latter would have to be updated every year). 

## Prerequisites

Decide which chain (Bitcoin or Ethereum) to issue to and follow the steps. The bitcoin chain is currently best supported by the Blockcerts libraries. Follow the steps for the chosen chain.

### Install cert-issuer

By default, cert-issuer issues to the bloxberg blockchain. Run this setup to issue to the standard chain:

To issue to the ethereum blockchain using the smart contract backend, run the following:
```
python setup.py install experimental --blockchain=ethereum_smart_contract
```

### Create an Ethereum issuing address

Currently Blockcerts just supports issuing to the Bloxberg Ethereum testnet, and the Ethereum mainnet. In Ethereum a public/private key pair is the same accross all test/main networks.

 __These steps involve storing secure information on a USB. Do not plug in this USB when your computer's wifi is on.__
 
 1. Create issuing address on Myetherwallet
    - Go to https://www.myetherwallet.com/.
    - For the best security turn off your connection to the internet when you are on the create wallet page.
 2. Go through the create wallet process
    - Store the private key on the USB stick and unplug it afterwards.
    - Copy the public key to the `issuing_address` value in conf.ini

#### Obtaining testnet coins

- Request some testnet coins by searching for “Testnet Faucet”, and entering your issuing public address. It may take a while for the transaction to be confirmed.
- Important: make sure you follow the guidance of the testnet faucet provider!


## Configuring cert-issuer 

Edit your conf.ini file (the config file for this application). 

```
issuing_address = <issuing-address>

# issuer URL / DID
verification_method = <verification-method>

chain=<bitcoin_regtest|bitcoin_testnet|bitcoin_mainnet|ethereum_bloxberg|ethereum_mainnet|mockchain>
    
usb_name = </Volumes/path-to-usb/>
key_file = <file-you-saved-pk-to>

unsigned_certificates_dir=<path-to-your-unsigned-certificates>
blockchain_certificates_dir=<path-to-your-blockchain-certificates>
work_dir=<path-to-your-workdir>

no_safe_mode

# advanced: uncomment the following line if you're running a bitcoin node
# bitcoind
```

Notes:
  - The `bitcoind` option is technically not required in `regtest` mode. `regtest` mode _only_ works with a local bitcoin node. The quick start in docker brushed over this detail by installing a regtest-configured bitcoin node in the docker container.
  - The Ethereum option does not support a local (test)node currently. The issuer will broadcast the transaction via the Etherscan API.

## Issuing

1. Add your certificates to data/unsigned_certs/

2. If you've installed the package you can issue certificates by running:

```
python cert-issuer -c conf.ini
```

3. Output
  - The Blockchain Certificates will be located in data/blockchain_certificates.
  - If you ran in the mainnet or testnet mode, you can also see your transaction on a live blockchain explorer. 
    - For Bitcoin, Blockr.io has explorers for both [testnet](https://tbtc.blockr.io/) and [mainnet](https://blockr.io/).
    - For Ethereum, Etherscan has explorers for [bloxberg](https://bloxberg.etherscan.io/) and [mainnet](https://etherscan.io/)
    - The transaction id is located in the Blockchain Certificate under `signature.anchors[0].sourceId`


# Unit tests

This project uses tox to validate against several python environments.

1. Ensure you have an python environment. [Recommendations](docs/virtualenv.md)

2. Run tests
    ```
    ./run_tests.sh
    ```
    
# Class design

## Core issuing classes
![](img/issuer_main_classes.png)

The `Issuer` api is quite simple; it relies on `CertificateHandler`s and `Transaction Handler`s to do the work of 
extracting the data to issue on the blockchain, and handling the blockchain transaction, respectively.

`CertificateBatchHandler` manages the certificates to issue on the blockchain. It ensures that all accessors iterate
 certificates in a predictable order. This is critical because the Merkle Proofs must be associated with the correct
 certificate. Python generators are used here to help keep the memory footprint low while reading from files.

- `prepare_batch` 
    - performs the preparatory steps on certificates in the batch, including validation of the schema and forming the 
    data that will go on the blockchain. Certificate-level details are handled by `CertificateHandler`s
    - returns the hex byte array that will go on the blockchain
- `finish_batch` ensures each certificate is updated with the blockchain transaction information (and proof in general)

`CertificateHandler` is responsible for reading from and updating a specific certificate (identified by certificate_metadata). 
It is used exclusively by `CertificateBatchHandler` to handle certificate-level details:
- `validate`: ensure the certificate is well-formed
- `sign`: (currently unused)
- `get_byte_array_to_issue`: return byte array that will be hashed, hex-digested and added to the Merkle Tree
- `add_proof`: associate a a proof with a certificate (in the current implementation, the proof is embedded in the file)

`TransactionHandler` deals with putting the data on the blockchain. Currently only a Bitcoin implementation exists

## Signing and secret management

![](img/signing_classes.png)

Finalizable signer is a convenience class allowing use of python's `with` syntax. E.g.:

```

with FinalizableSigner(secret_manager) as fs:
    fs.sign_message(message_to_sign)

```

SecretManagers ensure the secret key (wif) is loaded into memory for signing. FileSecretManager is the only current
implemenation.

## Merkle tree generator

![](img/merkle_tree_generator.png)

Handles forming the Merkle Tree, returning the data to put on the blockchain, and returning a python generator of the
proofs.

This class structure is intended to be general-purpose to allow other implementations. (Do this carefully if at all.)

# Advanced setup
- [Installing and using a local bitcoin node](docs/bitcoind.md)

# Publishing To Pypi
- Create an account for [pypi](https://pypi.org) & [pypi test](https://test.pypi.org)
- Install [twine](github.com/pypa/twine) - `pip install twine`
- Increment version in `__init__.py`
- Remove current items in dist - `rm -rf dist/*`
- Build cert-issuer - `python setup.py install`
- Build sdist - `python setup.py sdist`
- Run pypi test upload - `twine upload --repository-url https://test.pypi.org/legacy/ dist/*`
- Upload to pypi - `twine upload --repository-url https://upload.pypi.org/legacy/ dist/*`


# Examples

The files in examples/data-testnet contain results of previous runs. 

# FAQs

## Checking transaction status

You can validate your transaction before sending by looking it up by rawtx at blockchain.info. Example:

   ```
   curl 'https://blockchain.info/rawtx/45a9306dfe99820eb346bb17ae0b64173ac11cac2d0e4227c7a7cacbcc0bad31?cors=true'
   ```

For an Ethereum transaction, you'll need to use a different explorer, which might require an API key for raw JSON
output.  To view a transaction in a web browser, you might try something like this:

- Ethereum Mainnet: https://etherscan.io/tx/0xf537d81667c8011e34e1f450e18fd1c5a8a10c770cd0acdc91a79746696f36a3
- Ethereum Bloxberg (testnet): https://bloxberg.etherscan.io/tx/0xf537d81667c8011e34e1f450e18fd1c5a8a10c770cd0acdc91a79746696f36a3

## Mac scrypt problems

If your install on Mac is failing with a message like the following, try the [workaround described in this thread](https://github.com/ethereum/pyethereum/issues/292).

```
fatal error: 'openssl/aes.h'
      file not found
#include <openssl/aes.h>
```

# Contact

Contact us at [the Blockcerts community forum](http://community.blockcerts.org/).


