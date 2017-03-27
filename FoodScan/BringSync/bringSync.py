# -*- coding: utf-8 -*-
from pysimplelog import Logger


class BringSync:
    def __init__(self, bring, wu_list):
        self.logger = Logger('BringSync')
        self.wu_list = wu_list
        self.bring = bring

    def transfer_bring_list_action(self):
        tasks = self.wu_list.client.get_tasks(self.wu_list.list_id)
        if len(tasks) > 0:
            items = []
            for task in tasks:
                items.append(self.wu_list.item_from_task(task))
            self.bring.upload(items)
            for task in tasks:
                self.wu_list.client.delete_task(task['id'], task['revision'])
