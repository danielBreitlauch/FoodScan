#!/usr/bin/env python
# -*- coding: utf-8 -*-

from FoodScan.Synchronizer.bring import Bring
from FoodScan.Synchronizer.bringSync import BringSync
from FoodScan.BarcodeDescriptors.barcodeDescriptorCombiner import BarcodeDescriptorCombiner
from FoodScan.Shops.kaufland import *
from FoodScan.Synchronizer.barcodeSync import BarcodeSync
from FoodScan.Synchronizer.shopSync import ShopSync
from FoodScan.Synchronizer.wunderlist import *
from FoodScan.antiCaptcha import AntiCaptcha
from FoodScan.barcodereader import BarcodeReader
from config import *


# Shops:
kl = Kaufland(kaufland_email, kaufland_password, AntiCaptcha(anti_captcha_key))
# ayn = AllYouNeed(all_you_need_email, all_you_need_password)

# List:
l = WuList(wunderlist_client_id, wunderlist_token)

# Syncer:
BringSync(Bring(bring_user_uuid, bring_api_key, bring_authorization, bring_cookie), l, bring_export_list_id)
BarcodeSync(BarcodeDescriptorCombiner(), BarcodeReader(barcode_device), l, shopping_wunderlist_list_id, async=False)
ShopSync(kl, l, shopping_wunderlist_list_id, "http://flying-stampe.de", 8080, async=False)
