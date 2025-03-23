import json
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

class RpcAgent:
    def __init__(self, config):
        self.rpc_url = f"http://{config['rpc']['user']}:{config['rpc']['pass']}@{config['rpc']['host']}:{config['rpc']['port']}"
        self.agent = AuthServiceProxy(self.rpc_url)

    def load_wallet(self, wallet_name):
        return self.agent.loadwallet(wallet_name)

    def create_wallet(self, wallet_name):
        return self.agent.createwallet(wallet_name)

    def get_new_address(self, address_type):
        return self.agent.getnewaddress('', address_type)

    def send_to_address(self, address, amount):
        return self.agent.sendtoaddress(address, amount)

    def generate_to_address(self, num_blocks, address):
        return self.agent.generatetoaddress(num_blocks, address)

    def list_unspent(self, min_conf, max_conf, addresses):
        return self.agent.listunspent(min_conf, max_conf, addresses)

    def create_raw_transaction(self, tx_inputs, tx_outputs):
        return self.agent.createrawtransaction(tx_inputs, tx_outputs)

    def decode_raw_transaction(self, hex_string):
        return self.agent.decoderawtransaction(hex_string)

    def sign_raw_transaction_with_wallet(self, hex_string):
        return self.agent.signrawtransactionwithwallet(hex_string)

    def send_raw_transaction(self, hex_string):
        return self.agent.sendrawtransaction(hex_string)


def create_or_load_wallet(agent, wallet_name):
    try:
        wallet_info = agent.load_wallet(wallet_name)
        return wallet_info
    except JSONRPCException as e:
        if e.error['code'] == -18:
            wallet_info = agent.create_wallet(wallet_name)
            return wallet_info
        raise e


def get_new_address(agent, address_type):
    try:
        address = agent.get_new_address(address_type)
        return address
    except JSONRPCException as e:
        print(f"Error in get_new_address: {e}")
        raise e


def send_to_address(agent, address, amount):
    try:
        txid = agent.send_to_address(address, amount)
        return txid
    except JSONRPCException as e:
        print(f"Error in send_to_address: {e}")
        raise e


def generate_block(agent):
    try:
        address = get_new_address(agent, 'legacy')
        block = agent.generate_to_address(1, address)
        return block
    except JSONRPCException as e:
        print(f"Error in generate_block: {e}")
        raise e


def get_unspent_for_address(agent, address):
    try:
        utxos = agent.list_unspent(1, 9999999, [address])
        return utxos
    except JSONRPCException as e:
        print(f"Error in get_unspent_for_address: {e}")
        raise e


def create_raw_transaction(agent, address_a, tx_outputs):
    utxos_a = get_unspent_for_address(agent, address_a)
    if not utxos_a:
        raise Exception(f"No UTXOs found for address {address_a}")

    # Fee calculation
    tx_fee = 0.0001
    tx_inputs = [{'txid': utxo['txid'], 'vout': utxo['vout']} for utxo in utxos_a]

    total_input_amount = sum(utxo['amount'] for utxo in utxos_a)
    total_output_amount = sum(tx_outputs.values())
    change_amount = total_input_amount - total_output_amount - tx_fee

    if change_amount > 0.00001:
        tx_outputs[address_a] = change_amount

    try:
        raw_tx = agent.create_raw_transaction(tx_inputs, tx_outputs)
        return raw_tx
    except JSONRPCException as e:
        print(f"Error in create_raw_transaction: {e}")
        raise e


def decode_raw_transaction(agent, hex_string):
    try:
        decoded = agent.decode_raw_transaction(hex_string)
        return decoded
    except JSONRPCException as e:
        print(f"Error in decode_raw_transaction: {e}")
        raise e


def sign_raw_transaction_with_wallet(agent, hex_string):
    try:
        signed = agent.sign_raw_transaction_with_wallet(hex_string)
        return signed
    except JSONRPCException as e:
        print(f"Error in sign_raw_transaction_with_wallet: {e}")
        raise e


def send_raw_transaction(agent, hex_string):
    try:
        txid = agent.send_raw_transaction(hex_string)
        return txid
    except JSONRPCException as e:
        print(f"Error in send_raw_transaction: {e}")
        raise e
