from constants import master_petition_app_id, algorand
from algosdk.abi import ABIType

all_master_boxes = algorand.app.get_box_names(app_id=master_petition_app_id)

master_box_name_coder = ABIType.from_string('uint64')
master_box_value_coder = ABIType.from_string('(uint64,byte[],address,uint64)')

petition_box_value_coder = ABIType.from_string('(byte[],byte[])')

signature_box_name_coder = ABIType.from_string('address')
signature_box_value_coder = ABIType.from_string('uint64')

comment_box_name_coder = ABIType.from_string('uint64')
comment_box_value_coder = ABIType.from_string('(address,uint64,byte[])')

for master_box in all_master_boxes:
    master_box_name_raw = master_box.name_raw
    petition_id = master_box_name_coder.decode(master_box_name_raw)
    petition_app_id, petition_title_bytes, petition_creator, creation_time = algorand.app.get_box_value_from_abi_type(app_id=master_petition_app_id, box_name=master_box_name_raw, abi_type=master_box_value_coder)
    petition_title_text = bytes(petition_title_bytes).decode()
    print(f'(Master Box) Petition App ID: {petition_app_id}, Petition ID: {petition_id}, Petition Title: {petition_title_text}, Petition Creator: {petition_creator}, Creation Time: {creation_time}')

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
            print(f'(Petition Box) Found Signature for Petition # {petition_id}: {signee} Signed at {time_of_signature}')
        elif petition_box_name_raw == b' ':
            petition_title_bytes, petition_text_bytes = algorand.app.get_box_value_from_abi_type(
                app_id=petition_app_id, 
                box_name=petition_box_name_raw, 
                abi_type=petition_box_value_coder
            )
            petition_title_text = bytes(petition_title_bytes).decode()
            petition_body_text = bytes(petition_text_bytes).decode()
            print(f'(Petition Box) Text for this petition: {petition_body_text}')
            try:
                additional_text = bytes(algorand.app.get_box_value(app_id=petition_app_id, box_name=b'a')[:15]).decode() + ' . . . '
                # print(f'Additional Text: {len(additional_text)} characters, {additional_text}')
                print(f'(Petition Box) Had additional text: {additional_text}')
            except:
                print(f"(Petition Box) No additional text for petition # {petition_id}")

        elif petition_box_name_raw != b'a':
            print(petition_box_name_raw)
            comment_id = comment_box_name_coder.decode(petition_box_name_raw)
            commenter, time_of_comment, comment_bytes = algorand.app.get_box_value_from_abi_type(
                app_id=petition_app_id, 
                box_name=petition_box_name_raw, 
                abi_type=comment_box_value_coder
            )
            comment = bytes(comment_bytes)
            print(f'(Petition Box) \n Commentor: {commenter} \n Comment Time: {time_of_comment} \n Comment: {comment.decode()}')