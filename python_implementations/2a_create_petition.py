from clients.PetitionMasterClient import CreatePetitionArgs
from algokit_utils import PaymentParams, AlgoAmount
from constants import signing_account_1, get_master_petition_app_client, algorand, default_app_call_params, default_send_params

master_petition_app_client = get_master_petition_app_client(signing_account=signing_account_1)

petition_title = b'A Test Petition Title'
petition_text = b'This is a test petition; it must be in bytes format and will be under 2048 characters (the max collective app arg length)!'

print(f'Creating Test Petition with text: \n {petition_text} \n . . .')
mbr_payment_tx = algorand.create_transaction.payment(
    PaymentParams(
        sender=signing_account_1.address,
        signer=signing_account_1.signer,
        amount=AlgoAmount(algo=1),
        receiver=master_petition_app_client.app_address,
        validity_window=1000,
    )
)

txn_response = master_petition_app_client.send.create_petition(
    args=CreatePetitionArgs(
        petition_title=petition_title,
        petition_text=petition_text,
        mbr_payment=mbr_payment_tx
    ),
    params=default_app_call_params,
    send_params=default_send_params
)

print(f'Created Petition, App ID for new petition is: {txn_response.abi_return} \n Txn ID: {txn_response.tx_id}')
