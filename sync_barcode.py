#!/usr/bin/env python
# -*- coding: utf-8 -*-
#from FoodScan.BarcodeSync import *
from FoodScan.BarcodeSync import BarcodeSync, CascadingBarcodeDecoder
from FoodScan.ShopList import Paprika3List
from config import *

# shopList = WuList(barcode_sync_config)
# shopList = BringList(bring_config)
shopList = Paprika3List(paprika3_config)

BarcodeSync(CascadingBarcodeDecoder(), barcode_config, shopList, asynchron=False)
