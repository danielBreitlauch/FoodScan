# -*- coding: utf-8 -*-
import pickle
from _thread import start_new_thread
from pysimplelog import Logger
import traceback
import json
import requests
from FoodScan.BarcodeSync import BarcodeReader


class BarcodeSync:
    def __init__(self, barcode_descriptor, config, shopList, asynchron=True):
        self.logger = Logger('BarcodeSync')
        self.barcode_descriptor = barcode_descriptor
        self.barcode_reader = BarcodeReader(config['barcode_device_name'])
        self.shop_list = shopList
        self.file_name = "barcode.db"
        self.matches = self.load()
        if 'notification_homeassistant_bearer_token' in config:
            self.notification_url = config['notification_homeassistant_url']
            self.bearer_token = config['notification_homeassistant_bearer_token']

        self.notify("Booted")
        if asynchron:
            start_new_thread(self.listen, ())
        else:
            self.listen()

    def save(self):
        with open(self.file_name, 'wb') as f:
            pickle.dump(self.matches, f)

    def load(self):
        try:
            with open(self.file_name, 'rb') as f:
                return pickle.load(f)
        except IOError:
            return {}

    def remember_choice(self, barcode, item):
        self.matches[barcode] = item
        self.save()

    def match(self, barcode):
        if barcode in self.matches:
            self.logger.info("Use old match for: " + barcode)
            return self.matches[barcode]
        else:
            return None

    def listen(self):
        while True:
            try:
                barcode = self.barcode_reader.q.get()
                self.logger.info("Work on: " + barcode)
                item = self.match(barcode)
                if not item:
                    item = self.barcode_descriptor.item(barcode)
                    if item:
                        self.remember_choice(barcode, item)
                if item:
                    self.logger.info("Detected: " + item.name)
                    self.add_barcode(item)
                else:
                    self.logger.info("Could not id: " + barcode)
            except Exception:
                traceback.print_exc()

    def add_barcode(self, item):
        self.notify(item.name)

        for task, existing in self.shop_list.list_items():
            # self.logger.info("Existing item: " + existing.selected_shop_item().name)
            if existing.synced() and item.name.lower() in existing.selected_shop_item().name.lower():
                existing.inc_amount()
                self.shop_list.update_item(task, existing)
                self.logger.info("Updated existing item: " + existing.selected_shop_item().name)
                return

        self.shop_list.create_item(item)

    def notify(self, message):
        if not self.bearer_token:
            self.logger.debug("no notification credentials provided")
            return

        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.bearer_token,
        }

        data = {
            "title": "Barcode scan",
            "message": message,
            "data": {
                "group": "barcode_scan",
                "push": {
                    "interruption-level": "passive",
                    "sound": "none"
                }
            }
        }

        response = requests.request("POST", self.notification_url, headers=headers, data=json.dumps(data))
        self.logger.info("Notification " + message + "sent. Response: " + str(response.status_code))
        self.logger.info("Create new item")
