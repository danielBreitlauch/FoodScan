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

    def item_from_task(self, task, with_selects=True, unmark=False):
        notes = self.client.get_task_notes(task['id'])
        if len(notes) > 0:
            notes = notes[0]['content']
        else:
            notes = u""

        sub_tasks = []
        if with_selects:
            sub_tasks = self.client.get_task_subtasks(task['id'])

        item = Item.parse(task['title'], notes, sub_tasks)
        self.split_items(item, sub_tasks, unmark)
        return item

    def create_item(self, item):
        task = self.client.create_task(self.list_id, title=item.title())
        self.client.create_note(task['id'], item.note())
        for shop_item in item.shop_items:
            self.client.create_subtask(task['id'], unicode(shop_item), completed=shop_item.selected)

    def split_items(self, item, sub_tasks, unmark):
        selected_shop_items = []
        for shop_item in item.shop_items:
            if shop_item.selected:
                selected_shop_items.append(shop_item)

        if len(selected_shop_items) > 0:
            while len(selected_shop_items) > 1:
                shop_item = selected_shop_items.pop()
                new_item = Item(name=shop_item.name, price=shop_item.price, url=shop_item.link)
                new_item.select_shop_item(shop_item)
                self.create_item(new_item)
                shop_item.selected = False
                if unmark:
                    for sub in sub_tasks:
                        if shop_item == ShopItem.parse(sub['title']):
                            self.client.update_subtask(sub['id'], sub['revision'], completed=False)
            item.select_shop_item(selected_shop_items.pop())
