#!/usr/bin/env python
# -*- coding: utf-8 -*-

from FoodScan.Shops.kaufland import *
from FoodScan.Synchronizer.shopSync import ShopSync
from FoodScan.Synchronizer.wunderlist import *
from FoodScan.antiCaptcha import AntiCaptcha
from config import *


# Shops:
kl = Kaufland(kaufland_email, kaufland_password, AntiCaptcha(anti_captcha_key))
# ayn = AllYouNeed(all_you_need_email, all_you_need_password)

# List:
wl = WuList(wunderlist_client_id, wunderlist_token)

# Syncer:
#  Polling wunderlist for changes
# ShopSync(kl, wl, shopping_wunderlist_list_id, async=False)

#  Webhook that wunderlist can call when the list changes
ShopSync(kl, wl, shopping_wunderlist_list_id,
         web_hook_url=web_hook_url,
         web_server_ip=web_server_ip,
         web_server_port=web_server_port,
         async=False)
