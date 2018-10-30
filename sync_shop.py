#!/usr/bin/env python
# -*- coding: utf-8 -*-
from FoodScan import AntiCaptcha, WuList
from FoodScan.ShopSync import *
from config import *

# Shops:
kl = Kaufland(kaufland_email, kaufland_password, AntiCaptcha(anti_captcha_key))
# ayn = AllYouNeed(all_you_need_email, all_you_need_password)

# Syncer:
#  Polling wunderlist for changes
# ShopSync(kl, shop_sync_config, async=False)

#  Webhook that wunderlist can call when the list changes
ShopSync(kl, WuList(shop_sync_config),
         web_hook_url=web_hook_url,
         web_server_ip=web_server_ip,
         web_server_port=web_server_port,
         async=False)
