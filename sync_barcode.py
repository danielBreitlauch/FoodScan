#!/usr/bin/env python
# -*- coding: utf-8 -*-
from FoodScan.BarcodeSync import *
from config import *

BarcodeSync(CascadingBarcodeDecoder(), barcode_sync_config, async=False)
