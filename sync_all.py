#!/usr/bin/env python
# -*- coding: utf-8 -*-

from FoodScan.BarcodeSync import *
from FoodScan.BringSync import *
from FoodScan.ShopSync import *
from FoodScan import *
from config import *

# Shops:
kl = Kaufland(kaufland_email, kaufland_password, AntiCaptcha(anti_captcha_key))
# ayn = AllYouNeed(all_you_need_email, all_you_need_password)

# List:
l = WuList(wunderlist_client_id, wunderlist_token)

# Syncer:
BringSync(Bring(bring_sync_config), l, bring_sync_config['export_list_id'])
BarcodeSync(CascadingBarcodeDecoder(), BarcodeReader(barcode_sync_config['barcode_device']), l, barcode_sync_config['wunderlist_list_id'])
ShopSync(kl, l, shopping_wunderlist_list_id, "http://flying-stampe.de", 8080, async=False)
