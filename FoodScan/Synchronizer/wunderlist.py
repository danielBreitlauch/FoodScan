# -*- coding: utf-8 -*-
from FoodScan.item import *
import wunderpy2
from pysimplelog import Logger


class WuList:
    def __init__(self, client_id, token):
        self.logger = Logger('Wunderlist')
        self.client = wunderpy2.WunderApi().get_client(token, client_id)

    def create_web_hook(self, list_id, url, port):
        hooks = self.client.get_webhooks(list_id)
        for hook in hooks:
            self.client.delete_webhook(hook['id'], 0)

        self.client.create_webhook(list_id, url + ":" + str(port), "generic")

    def item_from_task(self, task, with_selects=False):
        notes = self.client.get_task_notes(task['id'])
        if len(notes) > 0:
            notes = notes[0]['content']
        else:
            notes = u""

        sub_filter = []
        if with_selects:
            for sub in self.client.get_task_subtasks(task['id'], completed=True):
                if sub['completed']:
                    sub_filter.append(sub)

        return Item.parse(task['title'], notes, sub_filter)
