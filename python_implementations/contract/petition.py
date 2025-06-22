from algopy import ARC4Contract, arc4, subroutine, BoxMap, UInt64, Global, Txn, gtxn, Application, String, itxn, Account, OnCompleteAction, BoxRef, Bytes, op
from algopy.arc4 import abimethod, DynamicBytes, Struct, Address, abi_call, arc4_signature

@subroutine
def get_mbr() -> UInt64:
    return Global.current_application_address.min_balance

@subroutine
def refund_excess(excess: UInt64) -> None:
    itxn.Payment(
        receiver=Txn.sender,
        amount=excess,
    ).submit()

class MasterPetitionDetails(Struct):
    petition_app_id: arc4.UInt64
    petition_title: DynamicBytes
    petition_creator: Address
    creation_time: arc4.UInt64

class ChildPetitionDetails(Struct):
    petition_title: DynamicBytes
    petition_text: DynamicBytes
    
class PetitionMaster(ARC4Contract):
    def __init__(self) -> None:
        self.petition_template_app = Application(0)
        self.petition_uid = arc4.UInt64(0)
        self.petition_details = BoxMap(arc4.UInt64, MasterPetitionDetails, key_prefix='')
        self.template_app_assigned = False
        self.previous_child_petition_app = Application(0)
        self.next_child_petition_app = Application(0)

    @abimethod(allow_actions=['UpdateApplication'])
    def update(self) -> None:
        self.sender_is_creator()

    @abimethod
    def assign_template_app(self, template_app: Application) -> None:
        self.sender_is_creator()
        self.petition_template_app = template_app
        self.template_app_assigned = True

    @abimethod
    def prime_initial_petition(self, mbr_payment: gtxn.PaymentTransaction) -> None:
        self.sender_is_creator()
        self.contract_is_payment_receiver(mbr_payment)

        pre_mbr = get_mbr()
        self.next_child_petition_app = self.create_petition_app()
        post_mbr = get_mbr()

        mbr_cost = post_mbr - pre_mbr
        excess = mbr_payment.amount - mbr_cost
        refund_excess(excess=excess)

    @subroutine
    def sender_is_creator(self) -> None:
        assert Txn.sender == Global.creator_address

    @abimethod
    def create_petition(
        self,
        petition_title: DynamicBytes,
        petition_text: DynamicBytes,
        mbr_payment: gtxn.PaymentTransaction,
    ) -> UInt64:
        self.template_app_is_assigned()
        self.contract_is_payment_receiver(pay_tx=mbr_payment)
        self.will_prime_petition()
        self.increment_petition_uid()

        petition_app = self.next_child_petition_app
        self.previous_child_petition_app = petition_app
        petition_app_id = petition_app.id

        inner_mbr_payment = itxn.Payment(
            receiver=self.previous_child_petition_app.address,
            amount=mbr_payment.amount
        )
    
        mbr_used, txn = abi_call(
            Petition.create_petition,
            petition_title,
            petition_text,
            inner_mbr_payment,
            app_id=self.previous_child_petition_app,
        )

        pre_mbr = get_mbr()
        self.next_child_petition_app = self.create_petition_app()
        self.fund_petition_app_with_account_mbr(petition_app=petition_app)
        self.assign_petition_app_master_and_petition_creator(app_id=petition_app_id)
        petition_info = self.get_petition_info(
            petition_app_id=petition_app_id,
            petition_title=petition_title,
        )
        self.petition_details[self.petition_uid] = petition_info.copy()
        post_mbr = get_mbr()

        mbr_cost = (post_mbr - pre_mbr) + 100_000
        excess = (mbr_payment.amount - mbr_cost) - mbr_used
        refund_excess(excess=excess)
        return petition_app_id

    @abimethod
    def additional_box_characters_option(self, additional_text: Bytes, mbr_payment: gtxn.PaymentTransaction) -> None:
        self.is_creating_petition()
        self.will_prime_petition()
        self.contract_is_payment_receiver(pay_tx=mbr_payment)
        
        inner_mbr_payment = itxn.Payment(
            receiver=self.previous_child_petition_app.address,
            amount=mbr_payment.amount
        )
    
        mbr_used, txn = abi_call(
            Petition.additional_box_characters_option,
            additional_text,
            inner_mbr_payment,
            app_id=self.previous_child_petition_app,
        )

        excess = mbr_payment.amount - mbr_used
        refund_excess(excess=excess)

    @subroutine
    def is_creating_petition(self) -> None:
        assert gtxn.ApplicationCallTransaction(1).app_args(0) == arc4_signature('create_petition(byte[],byte[],pay)uint64')
        assert gtxn.ApplicationCallTransaction(1).app_id == Global.current_application_id

    @subroutine
    def will_prime_petition(self) -> None:
        assert gtxn.ApplicationCallTransaction(Global.group_size - 1).app_args(0) == arc4_signature('prime_petition(application)void')

    @subroutine
    def template_app_is_assigned(self) -> None:
        assert self.template_app_assigned == True

    @subroutine
    def contract_is_payment_receiver(self, pay_tx: gtxn.PaymentTransaction) -> None:
        assert pay_tx.receiver == Global.current_application_address

    @subroutine
    def increment_petition_uid(self) -> None:
        self.petition_uid = arc4.UInt64(self.petition_uid.native + 1)

    @subroutine
    def create_petition_app(self) -> Application:
        return itxn.ApplicationCall(
                    approval_program=self.petition_template_app.approval_program,
                    clear_state_program=self.petition_template_app.clear_state_program,
                    global_num_uint=4,
                    global_num_bytes=2,
                    # extra_program_pages=3,
                ).submit().created_app
        
    
    @subroutine
    def fund_petition_app_with_account_mbr(self, petition_app: Application) -> None:
        itxn.Payment(
            receiver=petition_app.address,
            amount=100_000
        ).submit()

    @subroutine
    def assign_petition_app_master_and_petition_creator(self, app_id: UInt64) -> None:
        result = abi_call(
            Petition.assign_master_and_petition_creator,
            Global.current_application_id,
            Txn.sender,
            app_id=app_id
        )

    @subroutine
    def get_petition_info(self, petition_app_id: UInt64, petition_title: DynamicBytes) -> MasterPetitionDetails:
        return MasterPetitionDetails(
            petition_app_id=arc4.UInt64(petition_app_id),
            petition_title=petition_title.copy(),
            petition_creator=Address(Txn.sender),
            creation_time=arc4.UInt64(Global.latest_timestamp)
        )
    
    @abimethod
    def prime_petition(self, petition_app_id: Application) -> None:
        self.is_creating_petition()
        result = abi_call(
            Petition.prime_petition,
            app_id=petition_app_id
        )

    @abimethod
    def sign_petition(
        self,
        petition_app: Application,
        mbr_payment: gtxn.PaymentTransaction,
    ) -> None:
        self.contract_is_payment_receiver(pay_tx=mbr_payment)
        self.is_child_app(petition_app)

        inner_mbr_payment = itxn.Payment(
            receiver=petition_app.address,
            amount=mbr_payment.amount
        )
    
        mbr_used, txn = abi_call(
            Petition.sign_petition,
            Txn.sender,
            inner_mbr_payment,
            app_id=petition_app,
        )

        excess = mbr_payment.amount - mbr_used
        refund_excess(excess=excess)

    @subroutine
    def is_child_app(self, app_id: Application) -> None:
        assert app_id.creator == Global.current_application_address

class Signee(Struct):
    address: arc4.Address

class TimeSigned(Struct):
    time_signed: arc4.UInt64

class Comment(Struct):
    address: Address
    time: arc4.UInt64
    comment: DynamicBytes

class Petition(ARC4Contract):
    def __init__(self) -> None:
        self.signees = UInt64(0)
        self.creation_time = UInt64(0)
        self.petition_master = Application(0)
        self.petition_creator = Account()
        self.petition_details = BoxMap(String, ChildPetitionDetails, key_prefix='')
        self.signatures = BoxMap(Signee, TimeSigned, key_prefix='')
        self.comment_counter = arc4.UInt64(0)
        self.comments = BoxMap(arc4.UInt64, Comment, key_prefix='')
        self.petition_primed = False

    @abimethod(allow_actions=['UpdateApplication'])
    def update(self) -> None:
        self.is_creator_or_master_creator()

    @abimethod
    def assign_master_and_petition_creator(self, petition_master: Application, petition_creator: Account) -> None:
        self.is_creator_or_master_creator()
        self.petition_master = petition_master
        self.petition_creator = petition_creator

    @abimethod
    def create_petition(
        self,
        petition_title: DynamicBytes,
        petition_text: DynamicBytes,
        mbr_payment: gtxn.PaymentTransaction,
    ) -> UInt64:
        self.is_creator_or_master_creator()
        self.petition_is_not_primed()

        pre_mbr = get_mbr()
        petition_info = self.get_petition_info(
            petition_title=petition_title,
            petition_text=petition_text
        )
        self.petition_details[String(' ')] = petition_info.copy()
        self.creation_time = Global.latest_timestamp
        post_mbr = get_mbr()

        mbr_cost = post_mbr - pre_mbr
        excess = mbr_payment.amount - mbr_cost
        refund_excess(excess=excess)
        return mbr_cost
    
    @subroutine
    def get_petition_info(self, petition_title: DynamicBytes, petition_text: DynamicBytes) -> ChildPetitionDetails:
        return ChildPetitionDetails(
            petition_title=petition_title.copy(),
            petition_text=petition_text.copy(),
        )
    
    @abimethod
    def additional_box_characters_option(self, additional_text: Bytes, mbr_payment: gtxn.PaymentTransaction) -> UInt64:
        self.is_creator_or_master_creator()
        self.petition_is_not_primed()

        additional_box_details = BoxRef(key=b'a')
        box_length, box_exists = op.Box.length(additional_box_details.key)

        pre_mbr = get_mbr()
        if not box_exists:
            additional_box_details.put(additional_text)
        else:
            additional_box_details.resize(box_length + additional_text.length)
            additional_box_details.replace(box_length, additional_text)
        post_mbr = get_mbr()
        
        mbr_cost = post_mbr - pre_mbr
        excess = mbr_payment.amount - mbr_cost
        refund_excess(excess=excess)
        return mbr_cost
    

    @abimethod
    def prime_petition(self) -> None:
        self.is_creator_or_master_creator()
        self.petition_is_not_primed()
        self.petition_primed = True

    @subroutine
    def is_creator_or_master_creator(self) -> None:
        assert self.is_creator() or self.is_master_creator()

    @subroutine
    def is_creator(self) -> bool:
        return Txn.sender == Global.creator_address

    @subroutine
    def is_master_creator(self) -> bool:
        return Txn.sender == self.petition_master.creator
    
    @subroutine
    def petition_is_primed(self) -> None:
        assert self.petition_primed

    @subroutine
    def petition_is_not_primed(self) -> None:
        assert not self.petition_primed

    @abimethod
    def sign_petition(self, signer: Address, mbr_payment: gtxn.PaymentTransaction) -> UInt64:
        self.petition_is_primed()
        self.is_creator_or_master_creator()

        signee, time_signed = self.get_signer_info(signer)

        self.user_has_not_signed(signee=signee)

        pre_mbr = get_mbr()
        self.signatures[signee] = time_signed.copy()
        post_mbr = get_mbr()

        self.increment_signees()

        mbr_cost = post_mbr - pre_mbr
        excess_mbr = mbr_payment.amount - mbr_cost
        refund_excess(excess=excess_mbr)
        return mbr_cost

    @subroutine
    def user_has_not_signed(self, signee: Signee) -> None:
        assert signee not in self.signatures

    @subroutine
    def get_signer_info(self, signer: Address) -> tuple[Signee, TimeSigned]:
        return (
            Signee(
                address=signer,
            ), 
            TimeSigned(
                time_signed=arc4.UInt64(Global.latest_timestamp)
            )
        )
    
    @subroutine
    def increment_signees(self) -> None:
        self.signees += 1

    @abimethod
    def add_comment(self, text: DynamicBytes, mbr_payment: gtxn.PaymentTransaction) -> None:
        self.petition_is_primed()
        pre_mbr = get_mbr()
        self.comments[self.comment_counter] = Comment(
            address=Address(Txn.sender), 
            time=arc4.UInt64(Global.latest_timestamp),                   
            comment=text.copy()
        )
        post_mbr = get_mbr()

        mbr_cost = post_mbr - pre_mbr
        excess = mbr_payment.amount - mbr_cost
        refund_excess(excess=excess)
        self.increment_comment_counter()

    @subroutine
    def increment_comment_counter(self) -> None:
        self.comment_counter = arc4.UInt64(self.comment_counter.native + 1)


