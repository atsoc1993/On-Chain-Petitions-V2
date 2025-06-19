from clients.PetitionMasterClient import PetitionMasterClient, PetitionMasterFactory
from clients.PetitionMasterClient import SourceMap as PetitionMasterSourceMap
from clients.PetitionClient import PetitionClient, PetitionFactory
from clients.PetitionClient import SourceMap as PetitionSourceMap
from algokit_utils import AlgorandClient, SigningAccount, CommonAppCallParams, SendParams, AlgoAmount
from dotenv import load_dotenv
from pathlib import Path
import json
import os

load_dotenv(dotenv_path='python_implementations/.env')

sk_1 = os.getenv('sk')
pk_1 = os.getenv('pk')

sk_2 = os.getenv('sk_2')
pk_2 = os.getenv('pk_2')


signing_account_1 = SigningAccount(
    private_key=sk_1, 
    address=pk_1
)

signing_account_2 = SigningAccount(
    private_key=sk_2, 
    address=pk_2
)

algorand = AlgorandClient.testnet()

master_petition_factory = PetitionMasterFactory(
    algorand=algorand,
    default_sender=signing_account_1.address,
    default_signer=signing_account_1.signer,
)

petition_factory = PetitionFactory(
    algorand=algorand,
    default_sender=signing_account_1.address,
    default_signer=signing_account_1.signer,
)


master_petition_app_id = None
if os.getenv('master_petition_app_id'):
    master_petition_app_id = int(os.getenv('master_petition_app_id'))

def get_master_petition_app_client(signing_account: SigningAccount):
    assert master_petition_app_id, "Must deploy master app before attempting to fetch an app client instance"
    return algorand.client.get_typed_app_client_by_id(
        typed_client=PetitionMasterClient,
        app_id=master_petition_app_id,
        default_sender=signing_account.address,
        default_signer=signing_account.signer,
        approval_source_map=PetitionMasterSourceMap(json.loads((Path(__file__).parent / 'contract/contract_files/PetitionMaster.approval.puya.map').read_text()))
    )

def get_petition_app_client(signing_account: SigningAccount, petition_app_id: int):
    assert master_petition_app_id, "Must deploy master app before attempting to fetch an app client instance of a petition app"
    return algorand.client.get_typed_app_client_by_id(
        typed_client=PetitionClient,
        app_id=petition_app_id,
        default_sender=signing_account.address,
        default_signer=signing_account.signer,
        approval_source_map=PetitionSourceMap(json.loads((Path(__file__).parent / 'contract/contract_files/Petition.approval.puya.map').read_text()))
    )

default_app_call_params = CommonAppCallParams(
    max_fee=AlgoAmount(micro_algo=100_000),
    validity_window=1000
)

default_send_params = SendParams(
    cover_app_call_inner_transaction_fees=True,
    populate_app_call_resources=True,
    suppress_log=True,
)