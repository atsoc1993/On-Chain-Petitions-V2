from clients.PetitionMasterClient import SignPetitionArgs
from algokit_utils import PaymentParams, AlgoAmount
from constants import get_master_petition_app_client, algorand, default_app_call_params, default_send_params
#from constants import signing_account_1 as signing_account
from constants import signing_account_2 as signing_account
master_petition_app_client = get_master_petition_app_client(signing_account=signing_account)

petition_app_id = 741492548

print(f'Signing Petition: {petition_app_id}')

mbr_payment_tx = algorand.create_transaction.payment(
    PaymentParams(
        sender=signing_account.address,
        signer=signing_account.signer,
        amount=AlgoAmount(algo=1),
        receiver=master_petition_app_client.app_address,
        validity_window=1000,
    )
)

txn_response = master_petition_app_client.send.sign_petition(
    args=SignPetitionArgs(
        petition_app=petition_app_id,
        mbr_payment=mbr_payment_tx,
    ),
    params=default_app_call_params,
    send_params=default_send_params
)

print(f'Signed Petition, Txn ID: {txn_response.tx_id}')
