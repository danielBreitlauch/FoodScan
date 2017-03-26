# -*- coding: utf-8 -*-
from thread import start_new_thread
from pysimplelog import Logger
import traceback


class BarcodeSync:
    def __init__(self, barcode_descriptor, barcode_reader, wu_list, shop_list_id, async=True):
        self.logger = Logger('BarcodeSync')
        self.barcode_descriptor = barcode_descriptor
        self.barcode_reader = barcode_reader
        self.wu_list = wu_list
        self.shop_list_id = shop_list_id
        if async:
            start_new_thread(self.listen, ())
        else:
            self.listen()

    def listen(self):
        while True:
            try:
                barcode = self.barcode_reader.scan()
                item = self.barcode_descriptor.item(barcode)
                if item:
                    self.add_barcode(item)

            except Exception:
                traceback.print_exc()

    def add_barcode(self, item):
        tasks = self.wu_list.client.get_tasks(self.shop_list_id)

        for task in tasks:
            if item.name in task['title']:
                existing = self.wu_list.item_from_task(task)
                existing.inc_amount()
                self.wu_list.client.update_task(task['id'], task['revision'], title=existing.title())
                return

        for task in tasks:
            existing = self.wu_list.item_from_task(task, with_selects=True)
            if existing.synced() and item.name in existing.selected_shop_item().name:
                existing.inc_amount()
                self.wu_list.client.update_task(task['id'], task['revision'], title=existing.title())
                return

        task = self.wu_list.client.create_task(self.shop_list_id, title=item.title())
        self.wu_list.client.create_note(task['id'], item.note())
