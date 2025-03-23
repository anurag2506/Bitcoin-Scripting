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


def run_segwit_transaction():
    try:
        print("Part 2: Segwit Address Transactions (P2SH)")
        print("===========================================")

        # Load or create wallet
        create_or_load_wallet("test-wallet")

        # Generate new SegWit (P2SH) addresses
        address_a = get_new_address("p2sh-segwit")
        address_b = get_new_address("p2sh-segwit")
        address_c = get_new_address("p2sh-segwit")

        print(f"SegWit Address A: {address_a}")
        print(f"SegWit Address B: {address_b}")
        print(f"SegWit Address C: {address_c}")

        # Fund address A
        funding_amount = 1.0  # in BTC
        funding_txid = send_to_address(address_a, funding_amount)
        print(f"Funded address A with {funding_amount} BTC. Txid: {funding_txid}")

        # Generate block to confirm transaction
        generate_block()

        # Create raw transaction from address A to address B
        amount_a_to_b = 0.5
        raw_tx_a_to_b = create_raw_transaction(address_a, {address_b: amount_a_to_b})
        print("Raw transaction A to B created")

        # Decode raw transaction
        decoded_tx_a_to_b = decode_raw_transaction(raw_tx_a_to_b)
        print("Locking script (ScriptPubKey) for address B:")

        for output in decoded_tx_a_to_b['vout']:
            if 'address' in output['scriptPubKey'] and output['scriptPubKey']['address'] == address_b:
                print(json.dumps(output['scriptPubKey'], indent=2))
                break

        # Sign the transaction
        signed_tx_a_to_b = sign_raw_transaction_with_wallet(raw_tx_a_to_b)
        print("Transaction signed successfully")

        # Broadcast transaction
        txid_a_to_b = send_raw_transaction(signed_tx_a_to_b['hex'])
        print(f"Transaction A to B broadcasted successfully.\nTxid: {txid_a_to_b}")

        # Generate block to confirm transaction
        generate_block()

        # Create raw transaction from address B to address C
        amount_b_to_c = 0.25
        raw_tx_b_to_c = create_raw_transaction(address_b, {address_c: amount_b_to_c})
        print("Raw transaction B to C created")

        # Decode raw transaction
        decoded_tx_b_to_c = decode_raw_transaction(raw_tx_b_to_c)
        print("Transaction B to C decoded")

        # Sign the transaction
        signed_tx_b_to_c = sign_raw_transaction_with_wallet(raw_tx_b_to_c)
        print("Transaction B to C signed successfully")

        # Decode the signed transaction to view the ScriptSig (unlocking script)
        signed_decoded_tx_b_to_c = decode_raw_transaction(signed_tx_b_to_c['hex'])
        if 'vin' in signed_decoded_tx_b_to_c and len(signed_decoded_tx_b_to_c['vin']) > 0:
            print("Unlocking script (ScriptSig) for input spending from B:")
            print(json.dumps(signed_decoded_tx_b_to_c['vin'][0]['scriptSig'], indent=2))
            print("Signature and public key are in witness data.")

        # Broadcast transaction
        txid_b_to_c = send_raw_transaction(signed_tx_b_to_c['hex'])
        print(f"Transaction B to C broadcasted successfully.\nTxid: {txid_b_to_c}")

        # Generate block to confirm transaction
        generate_block()

        # Save transaction info
        segwit_tx_info = {
            'addressA': address_a,
            'addressB': address_b,
            'addressC': address_c,
            'fundingTxid': funding_txid,
            'txAtoB': {
                'txid': txid_a_to_b,
                'rawHex': signed_tx_a_to_b['hex'],
                'decoded': decoded_tx_a_to_b
            },
            'txBtoC': {
                'txid': txid_b_to_c,
                'rawHex': signed_tx_b_to_c['hex'],
                'decoded': signed_decoded_tx_b_to_c
            }
        }

        # Ensure the data directory exists
        os.makedirs(Config.dataPath, exist_ok=True)

        # Save to JSON file
        with open(os.path.join(Config.dataPath, "segwit-transactions.json"), 'w') as f:
            json.dump(segwit_tx_info, f, indent=2)

        print("Transaction details saved to segwit-transactions.json")

        return segwit_tx_info

    except Exception as error:
        print("Error in Segwit transaction process:", error)
        raise


if __name__ == '__main__':
    try:
        run_segwit_transaction()
        print("Segwit transaction completed successfully")
    except Exception as e:
        print("Error in runSegwitTransaction:", e)
