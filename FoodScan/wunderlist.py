# -*- coding: utf-8 -*-
from FoodScan.items import *
import wunderpy2
from pysimplelog import Logger


class WuList:
    def __init__(self, client_id, token, list_id):
        self.logger = Logger('Wunderlist')
        self.client = wunderpy2.WunderApi().get_client(token, client_id)
        self.list_id = list_id

    def create_web_hook(self, url, port):
        hooks = self.client.get_webhooks(self.list_id)
        for hook in hooks:
            self.client.delete_webhook(hook['id'], 0)

        self.client.create_webhook(self.list_id, url + ":" + str(port), "generic")

    def item_from_task(self, task, with_selects=False):
        notes = self.client.get_task_notes(task['id'])
        if len(notes) > 0:
            notes = notes[0]['content']
        else:
            notes = u""

        sub_tasks = []
        if with_selects:
            for sub in self.client.get_task_subtasks(task['id'], completed=True):
                sub_tasks.append(sub)

        return Item.parse(task['title'], notes, sub_tasks)

    def create_item(self, item):
        task = self.client.create_task(self.list_id, title=item.title())
        self.client.create_note(task['id'], item.note())
        for shop_item in item.shop_items:
            self.client.create_subtask(task['id'], unicode(shop_item), completed=shop_item.selected)

