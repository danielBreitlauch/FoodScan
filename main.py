#!/usr/bin/env python
# -*- coding: utf-8 -*-

from allyouneed import *
from bring import Bring
from codecheck import *
from barcode import *
from wunderlist import *
from config import *
import time


b = Bring(bring_user_uuid, bring_api_key, bring_authorization, bring_cookie)
cc = CodeCheck()

ayn = AllYouNeed()
ayn.load_session_or_log_in('session_cookies', all_you_need_email, all_you_need_password)

l = WuList(ayn, cc, b, wunderlist_client_id, wunderlist_token, ayn_wunderlist_list_id, bring_export_list_id)
# bc = Barcode(barcode_device, l.add_barcode)
while True:
    l.check_action()
    time.sleep(10)
