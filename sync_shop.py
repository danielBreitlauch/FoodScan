#!/usr/bin/env python
# -*- coding: utf-8 -*-
from FoodScan import *
from FoodScan.ShopSync import *
from config import *

# Shops:
kl = Kaufland(kaufland_email, kaufland_password, AntiCaptcha(anti_captcha_key))
# ayn = AllYouNeed(all_you_need_email, all_you_need_password)

# List:
wl = WuList(wunderlist_client_id, wunderlist_token, shopping_wunderlist_list_id)

# Syncer:
#  Polling wunderlist for changes
# ShopSync(kl, wl, async=False)

#  Webhook that wunderlist can call when the list changes
ShopSync(kl, wl,
         web_hook_url=web_hook_url,
         web_server_ip=web_server_ip,
         web_server_port=web_server_port,
         async=False)
