## FoodScan ##
Automate grocery shopping


About
--------

FoodScan allows you to use a barcode scanner to put items into a wunderlist grocery shopping list.
After that the script syncs the list items with the shopping cart.
The list items get enhanced with information from the grocery shop.
If the grocery shop provides multiple results these results can be selected from sub-tasks.

Features
--------

* Barcode scanner to import shopping items
* Automatic search in grocery online stores
* Automatic syncing of the shopping list and the store cart
* Wunderlist shopping list gets annotated with shopping information
* Reusable sub-components:
    * Anti Captcha
    * Barcode reader
    * Codecheck.info
    * shop.Kaufland.de
    * allyouneedfresh.de
    * parts of a Bring mobile app export
    * Wunderlist syncing
    
Installation
--------

FoodScan is compatible with Python 2.7.  
There will be a pip package in the future.  
Until then... 
```
python ./setup.py install
```

Run
--------

Generally:
1. Edit config.py
2. import the config
3. Create a WuList instance to connect to Wunderlist
```
from config import *
wl = WuList(wunderlist_client_id, wunderlist_token)
```

###Barcode scanner import to wunderlist:###
```
reader = BarcodeReader(barcode_sync_config['barcode_device'])
BarcodeSync(CascadingBarcodeDecoder(), reader, wl, barcode_sync_config['wunderlist_list_id'], async=False)
```

###Wunderlist export to the Bring App:###
```
BringSync(Bring(bring_sync_config), wl, bring_sync_config["export_list_id"])
```

###Wunderlist sync with a Kaufland or AllYouNeed shopping cart:###
1. You can chose a shop implementation. Some shops need a Captcha solving service account.

```
kl = Kaufland(kaufland_email, kaufland_password, AntiCaptcha(anti_captcha_key))
# or 
ayn = AllYouNeed(all_you_need_email, all_you_need_password)
```

2. Chose a sync method:
    1. Polling wunderlist for changes
    2. If your host is reachable from the internet you can use Wunderlist webhooks.
     In that case wunderlist is calling this app in case of list changes.

```
ShopSync(kl, wl, shopping_wunderlist_list_id, async=False)
# or 
ShopSync(kl, wl, shopping_wunderlist_list_id,
         web_hook_url=web_hook_url,
         web_server_ip=web_server_ip,
         web_server_port=web_server_port,
         async=False)
```

###All three parts in one app:###
```
python sync_all.py
```

