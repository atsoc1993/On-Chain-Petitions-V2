from clients.PetitionClient import AddCommentArgs
from algokit_utils import PaymentParams, AlgoAmount, CommonAppCallParams
from constants import signing_account_1, get_petition_app_client, algorand, default_app_call_params, default_send_params


petition_app_id = 741490703 # <=================== PUT IN A PETITION APP ID
petition_app_client = get_petition_app_client(signing_account=signing_account_1, petition_app_id=petition_app_id)


petition_comment_text = b'This is a test comment, it must be less than 2000 bytes'


print(f'Creating Test Petition with text: \n {petition_comment_text} \n . . .')
mbr_payment_tx = algorand.create_transaction.payment(
    PaymentParams(
        sender=signing_account_1.address,
        signer=signing_account_1.signer,
        amount=AlgoAmount(algo=1.5),
        receiver=petition_app_client.app_address,
        validity_window=1000,
    )
)


txn_response = petition_app_client.send.add_comment(
    args=AddCommentArgs(
        text=petition_comment_text,
        mbr_payment=mbr_payment_tx,
    ),
    params=default_app_call_params,
    send_params=default_send_params
)



print(f'Petition created with large amounts of text— Txn ID: {txn_response.tx_ids[0]}')
