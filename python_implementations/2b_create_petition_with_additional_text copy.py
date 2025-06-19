from clients.PetitionMasterClient import CreatePetitionArgs, AdditionalBoxCharactersOptionArgs
from algokit_utils import PaymentParams, AlgoAmount, CommonAppCallParams
from constants import signing_account_1, get_master_petition_app_client, algorand, default_app_call_params, default_send_params

master_petition_app_client = get_master_petition_app_client(signing_account=signing_account_1)

petition_title = b'A Test Petition Title'
petition_text = b'This is a test petition; it must be in bytes format and will be over 10,000 characters!' + b'A' * 10_000

main_app_call_text = petition_text[:2000]
subsequent_additional_texts = [petition_text[i: i + 2000] for i in range(2000, len(petition_text), 2000)]


print(f'Creating Test Petition with text: \n {petition_text} \n . . .')
mbr_payment_tx = algorand.create_transaction.payment(
    PaymentParams(
        sender=signing_account_1.address,
        signer=signing_account_1.signer,
        amount=AlgoAmount(algo=1.5),
        receiver=master_petition_app_client.app_address,
        validity_window=1000,
    )
)


new_group = master_petition_app_client.new_group()

new_group.create_petition(
    args=CreatePetitionArgs(
        petition_title=petition_title,
        petition_text=main_app_call_text,
        mbr_payment=mbr_payment_tx,
    ),
    params=default_app_call_params,
)

for i in range(len(subsequent_additional_texts)):

    mbr_payment_tx = algorand.create_transaction.payment(
        PaymentParams(
            sender=signing_account_1.address,
            signer=signing_account_1.signer,
            amount=AlgoAmount(algo=1),
            receiver=master_petition_app_client.app_address,
            validity_window=1000,
            note=f'{i}'
        )
    )

    new_group.additional_box_characters_option(
        args=AdditionalBoxCharactersOptionArgs(
            additional_text=subsequent_additional_texts[i],
            mbr_payment=mbr_payment_tx
        ),
        params=CommonAppCallParams(
            max_fee=AlgoAmount(micro_algo=100_000),
            note=f'{i}'
        )
    )
    

txn_response = new_group.send(
    send_params=default_send_params,
)
print(f'Petition created with large amounts of text— Txn ID: {txn_response.tx_ids[0]}')
