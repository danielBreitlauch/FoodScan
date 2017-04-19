# -*- coding: utf-8 -*-
from pysimplelog import Logger

from FoodScan import WuList
from FoodScan.BringSync import Bring


class BringSync:
    def __init__(self, config):
        self.logger = Logger('BringSync')
        self.wu_list = WuList(config)
        self.bring = Bring(config)

    def transfer_bring_list_action(self):
        tasks = self.wu_list.list_items()
        if len(tasks) > 0:
            items = []
            for task in tasks:
                items.append(self.wu_list.item_from_task(task))
            self.bring.upload(items)
            for task in tasks:
                self.wu_list.delete_item(task)
