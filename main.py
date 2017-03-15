#!/usr/bin/env python
# -*- coding: utf-8 -*-

from FoodScan.Shops.kaufland import *
from FoodScan.antiCaptcha import AntiCaptcha
from FoodScan.barcode import Barcode
from FoodScan.bring import Bring
from FoodScan.codecheck import *
from FoodScan.wunderlist import *

from config import *

b = Bring(bring_user_uuid, bring_api_key, bring_authorization, bring_cookie)
cc = CodeCheck()
kl = Kaufland(kaufland_email, kaufland_password, AntiCaptcha(captcha_client_key))
# ayn = AllYouNeed(all_you_need_email, all_you_need_password)

l = WuList(kl, cc, b, wunderlist_client_id, wunderlist_token, ayn_wunderlist_list_id, bring_export_list_id)
bc = Barcode(barcode_device, l.add_barcode)
while True:
    l.check_action()
    time.sleep(10)
