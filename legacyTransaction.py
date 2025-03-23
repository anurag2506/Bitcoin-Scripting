import json
import os
from helpers import (
    create_or_load_wallet,
    get_new_address,
    send_to_address,
    generate_block,
    get_unspent_for_address,
    create_raw_transaction,
    decode_raw_transaction,
    sign_raw_transaction_with_wallet,
    send_raw_transaction
)
from config import Config


def run_legacy_transaction():
    try:
        print("Part 1: Legacy Address Transactions (P2PKH)")
        print("===========================================")

        # Load or create wallet
        create_or_load_wallet("test-wallet")

        # Generate new legacy addresses
        address_a = get_new_address("legacy")
        address_b = get_new_address("legacy")
        address_c = get_new_address("legacy")

        print("Addresses created:")
        print("A:", address_a)
        print("B:", address_b)
        print("C:", address_c)

        # Fund address A
        funding_amount = 1.0  # in BTC
        funding_txid = send_to_address(address_a, funding_amount)
        print(f"Funded address A with {funding_amount} BTC. Txid: {funding_txid}")

        # Generate block to confirm transaction
        generate_block()

        # Create raw transaction from A to B
        amount_a_to_b = 0.5
        raw_tx_a_to_b = create_raw_transaction(address_a, {address_b: amount_a_to_b})
        print(f"Raw transaction A to B: {raw_tx_a_to_b}")

        # Decode raw transaction to get locking script
        decode_tx_a_to_b = decode_raw_transaction(raw_tx_a_to_b)
        print("Locking script (ScriptPubKey) for address B:")

        for output in decode_tx_a_to_b['vout']:
            if 'address' in output['scriptPubKey'] and output['scriptPubKey']['address'] == address_b:
                print(json.dumps(output['scriptPubKey'], indent=2))
                break

        # Sign the transaction
        signed_tx_a_to_b = sign_raw_transaction_with_wallet(raw_tx_a_to_b)
        print("Transaction signed successfully")

        # Broadcast the transaction
        txid_a_to_b = send_raw_transaction(signed_tx_a_to_b['hex'])
        print(f"Transaction from A to B broadcasted successfully. Txid: {txid_a_to_b}")

        # Generate block to confirm transaction
        generate_block()

        # Create a raw transaction from B to C
        amount_b_to_c = 0.2
        raw_tx_b_to_c = create_raw_transaction(address_b, {address_c: amount_b_to_c})
        print(f"Raw transaction B to C: {raw_tx_b_to_c}")

        # Decode raw transaction to get locking script
        decode_tx_b_to_c = decode_raw_transaction(raw_tx_b_to_c)
        print("Transaction B to C decoded")

        # Sign the transaction
        signed_tx_b_to_c = sign_raw_transaction_with_wallet(raw_tx_b_to_c)
        print("Transaction B to C signed successfully")

        signed_decoded_tx_b_to_c = decode_raw_transaction(signed_tx_b_to_c['hex'])

        # Find input that spends the UTXO for address B
        if 'vin' in signed_decoded_tx_b_to_c and len(signed_decoded_tx_b_to_c['vin']) > 0:
            print("Unlocking script (ScriptSig) for input spending from B:")
            print(json.dumps(signed_decoded_tx_b_to_c['vin'][0]['scriptSig'], indent=2))

        # Broadcast the transaction
        txid_b_to_c = send_raw_transaction(signed_tx_b_to_c['hex'])
        print(f"Transaction from B to C broadcasted successfully. Txid: {txid_b_to_c}")

        # Generate block to confirm transaction
        generate_block()

        # Save transaction details to file
        legacy_tx_info = {
            'addressA': address_a,
            'addressB': address_b,
            'addressC': address_c,
            'fundingTxid': funding_txid,
            'txidAtoB': {
                'txid': txid_a_to_b,
                'rawHex': signed_tx_a_to_b['hex'],
                'decoded': decode_tx_a_to_b
            },
            'txidBtoC': {
                'txid': txid_b_to_c,
                'rawHex': signed_tx_b_to_c['hex'],
                'decoded': signed_decoded_tx_b_to_c
            }
        }

        # Ensure the data directory exists
        os.makedirs(Config.dataPath, exist_ok=True)

        # Save to JSON file
        with open(os.path.join(Config.dataPath, "legacy-transactions.json"), 'w') as f:
            json.dump(legacy_tx_info, f, indent=2)

        print("Transaction details saved to legacy-transactions.json")

        return legacy_tx_info

    except Exception as error:
        print("Error in legacy transaction process:", error)
        raise


if __name__ == '__main__':
    try:
        run_legacy_transaction()
        print("Legacy transaction completed successfully")
    except Exception as e:
        print("Error in run_legacy_transaction:", e)
