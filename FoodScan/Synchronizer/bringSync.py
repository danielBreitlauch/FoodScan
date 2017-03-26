# -*- coding: utf-8 -*-
from pysimplelog import Logger


class BringSync:
    def __init__(self, bring, wu_list, bring_export_list_id):
        self.logger = Logger('BringSync')
        self.wu_list = wu_list
        self.bring = bring
        self.bring_export_list_id = bring_export_list_id

    def transfer_bring_list_action(self):
        tasks = self.wu_list.client.get_tasks(self.bring_export_list_id)
        if len(tasks) > 0:
            items = []
            for task in tasks:
                items.append(self.wu_list.item_from_task(task))
            self.bring.upload(items)
            for task in tasks:
                self.wu_list.client.delete_task(task['id'], task['revision'])
