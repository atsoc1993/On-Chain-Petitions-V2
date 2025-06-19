from algokit_utils import PaymentParams, AlgoAmount
from constants import master_petition_factory, petition_factory, algorand, signing_account_1
from clients.PetitionMasterClient import AssignTemplateAppArgs
from dotenv import load_dotenv, set_key

load_dotenv('python_implementations/.env')

print(f'Deploying Master Petition App . . .')

master_petition_app_client, txn_response = master_petition_factory.send.create.bare()
set_key(
    dotenv_path='python_implementations/.env', 
    key_to_set='master_petition_app_id', 
    value_to_set=str(master_petition_app_client.app_id)
)

print(f'Deployed Master Petition App; Wrote App ID ({master_petition_app_client.app_id}) to .env')

print(f'Deploying Petition Template App . . .')

petition_app_client, txn_response = petition_factory.send.create.bare()
set_key(
    dotenv_path='python_implementations/.env', 
    key_to_set='petition_template_app_id', 
    value_to_set=str(petition_app_client.app_id)
)

print(f'Deployed Petition Template App; Wrote App ID ({petition_app_client.app_id}) to .env')

print(f'Designating Petition Template App ID @ Master & Funding Master Petition App with Account MBR of 0.1 Algo . . .')


new_group = master_petition_app_client.new_group()


new_group.assign_template_app(
    args=AssignTemplateAppArgs(
        template_app=petition_app_client.app_id
    )
)

fund_master_app_with_account_mbr = algorand.create_transaction.payment(
    params=PaymentParams(
        sender=signing_account_1.address,
        signer=signing_account_1.signer,
        amount=AlgoAmount(micro_algo=100_000),
        receiver=master_petition_app_client.app_address,
        validity_window=1000,
    )
)

new_group.add_transaction(
    txn=fund_master_app_with_account_mbr, 
    signer=signing_account_1.signer
)

new_group.send()
print(f'Master Petition App Client Account MBR Funded')

