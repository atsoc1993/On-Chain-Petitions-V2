from dotenv import load_dotenv, set_key
from algosdk.account import generate_account

load_dotenv()

sk, pk = generate_account()
set_key(dotenv_path='python_implementations/.env', key_to_set='sk', value_to_set=sk)
set_key(dotenv_path='python_implementations/.env', key_to_set='pk', value_to_set=pk)

sk_2, pk_2 = generate_account()
set_key(dotenv_path='python_implementations/.env', key_to_set='sk_2', value_to_set=sk_2)
set_key(dotenv_path='python_implementations/.env', key_to_set='pk_2', value_to_set=pk_2)

