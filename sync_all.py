#!/usr/bin/env python
# -*- coding: utf-8 -*-

from FoodScan.BarcodeSync.BarcodeDecoder.cascadingBarcodeDecoder import CascadingBarcodeDecoder
from FoodScan.BarcodeSync.barcodeSync import BarcodeSync
from FoodScan.BarcodeSync.barcodereader import BarcodeReader
from FoodScan.BringSync.bring import Bring
from FoodScan.BringSync.bringSync import BringSync
from FoodScan.ShopSync.Shops.kaufland import Kaufland
from FoodScan.ShopSync.shopSync import ShopSync
from FoodScan.antiCaptcha import AntiCaptcha
from FoodScan.wunderlist import *
from config import *

# Shops:
kl = Kaufland(kaufland_email, kaufland_password, AntiCaptcha(anti_captcha_key))
# ayn = AllYouNeed(all_you_need_email, all_you_need_password)

# List:
l = WuList(wunderlist_client_id, wunderlist_token)

# Syncer:
BringSync(Bring(bring_user_uuid, bring_api_key, bring_authorization, bring_cookie), l, bring_export_list_id)
BarcodeSync(CascadingBarcodeDecoder(), BarcodeReader(barcode_device), l, shopping_wunderlist_list_id)
ShopSync(kl, l, shopping_wunderlist_list_id, "http://flying-stampe.de", 8080, async=False)
