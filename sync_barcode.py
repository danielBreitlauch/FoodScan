#!/usr/bin/env python
# -*- coding: utf-8 -*-
from FoodScan.BarcodeSync import *
from FoodScan.BringList import BringList
from config import *

# shopList = WuList(barcode_sync_config)
shopList = BringList(bring_config)

BarcodeSync(CascadingBarcodeDecoder(), barcode_config, shopList, async=False)
