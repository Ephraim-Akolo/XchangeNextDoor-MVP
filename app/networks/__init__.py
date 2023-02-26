from web3 import Web3

web3 = Web3()

web3.eth.account.enable_unaudited_hdwallet_features()

def from_mnemonic(mnemonic: str, passphrase: str = "", account_type: str='eth', account_number: int = 0, account_index: int = 0):
    if account_type == "trx":
        account_path = f"m/44'/195'/{account_number}'/0/{account_index}"
        key = web3.eth.account.from_mnemonic(mnemonic=mnemonic, passphrase=passphrase, account_path=account_path).key.hex()
        return key[2:] if key[:2].lower() == "0x" else key
    else:
        account_path = f"m/44'/60'/{account_number}'/0/{account_index}"
        return web3.eth.account.from_mnemonic(mnemonic=mnemonic, passphrase=passphrase, account_path=account_path)

def create_with_mnemonic(passphrase: str = "", num_words: int = 12, language: str = "english", account_type: str = "eth"):
    if account_type == "trx":
        account_path = f"m/44'/195'/0'/0/0"
        account, mnemonic = web3.eth.account.create_with_mnemonic(passphrase, num_words, language, account_path)
        key = account.key.hex()
        key = key[2:] if key[:2].lower() == "0x" else key
        return key, mnemonic 
    else:
        account_path = f"m/44'/60'/0'/0/0"
        return web3.eth.account.create_with_mnemonic(passphrase, num_words, language, account_path)
