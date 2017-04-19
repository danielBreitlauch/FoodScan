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

# Syncer:
BringSync(bring_sync_config)
BarcodeSync(CascadingBarcodeDecoder(), barcode_sync_config)
ShopSync(kl, shop_sync_config,
         web_hook_url=web_hook_url,
         web_server_ip=web_server_ip,
         web_server_port=web_server_port,
         async=False)
