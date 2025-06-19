from constants import master_petition_app_id, algorand
from algosdk.abi import ABIType

all_master_boxes = algorand.app.get_box_names(app_id=master_petition_app_id)

master_box_name_coder = ABIType.from_string('uint64')
master_box_value_coder = ABIType.from_string('(uint64,byte[],byte[])')

signature_box_name_coder = ABIType.from_string('address')
signature_box_value_coder = ABIType.from_string('uint64')

comment_box_name_coder = ABIType.from_string('uint64')
comment_box_value_coder = ABIType.from_string('(address,uint64,byte[])')

for master_box in all_master_boxes:
    master_box_name_raw = master_box.name_raw
    if master_box_name_raw[:1] != b'a':
        petition_id = master_box_name_coder.decode(master_box_name_raw)
        petition_app_id, petition_title_bytes, petition_text_ints = algorand.app.get_box_value_from_abi_type(app_id=master_petition_app_id, box_name=master_box_name_raw, abi_type=master_box_value_coder)
        petition_title_text = bytes(petition_title_bytes).decode()
        petition_text = bytes(petition_text_ints).decode()
        print(f'Petition App ID: {petition_app_id}, Petition ID: {petition_id}, Petition Title: {petition_title_text} Petition Text: {petition_text[:15]}')
        try:
            additional_text = bytes(algorand.app.get_box_value(app_id=master_petition_app_id, box_name=b'a' + master_box_name_raw)[:15]).decode() + ' . . . '
            # print(f'Additional Text: {len(additional_text)} characters, {additional_text}')
            print(f'Had additional text: {additional_text}')
        except:
            print(f"No additional text for petition # {petition_id}")

        petition_boxes = algorand.app.get_box_names(app_id=petition_app_id)
        for petition_box in petition_boxes:
            petition_box_name_raw = petition_box.name_raw
            if len(petition_box_name_raw) == 32:
                signee = signature_box_name_coder.decode(petition_box_name_raw)
                time_of_signature= algorand.app.get_box_value_from_abi_type(
                    app_id=petition_app_id, 
                    box_name=petition_box_name_raw, 
                    abi_type=signature_box_value_coder
                )
                print(f'Found Signature for Petition # {petition_id}: {signee} Signed at {time_of_signature}')

            else:
                comment_id = comment_box_name_coder.decode(petition_box_name_raw)
                commenter, time_of_comment, comment_bytes = algorand.app.get_box_value_from_abi_type(
                    app_id=petition_app_id, 
                    box_name=petition_box_name_raw, 
                    abi_type=comment_box_value_coder
                )
                comment = bytes(comment_bytes)
                print(f' Commentor: {commenter} \n Comment Time: {time_of_comment} \n Comment: {comment.decode()}')