# -*- coding: utf-8 -*-
from FoodScan.items import ListItem, SubItem


class MetaShop:

    def __init__(self, shop_sync, wu_list, total_price=0):
        self.wu_list = wu_list
        self.shop_sync = shop_sync
        self.item = MetaShopItem(total_price)
        self.iid = None
        self.revision = 0

    def detect_changes(self, new_tasks):
        for new_task in new_tasks:
            if MetaShopItem.is_meta_item(new_task):
                if self.iid != new_task['id'] or self.revision != new_task['revision']:
                    self.iid = new_task['id']
                    self.revision = new_task['revision']
                    return True
                return False

        self.iid = self.wu_list.create_item(self.item)
        self.revision = 0
        return True

    def sync(self):
        for sub_task in self.wu_list.client.get_task_subtasks(self.iid):
            for action in self.item.actions:
                if sub_task['title'] == action.title():
                    if sub_task['completed']:
                        for a in self.item.actions:
                            a.notes = None
                        action.action(self)
                    break

    def set_price(self, price):
        if price != self.item.price:
            self.item.price = price
            self.revision = self.wu_list.update_item({'id': self.iid, 'title': ""}, self.item)

    def update(self):
        self.revision = self.wu_list.update_item({'id': self.iid}, self.item, rebuild_subs=True, rebuild_notes=True)


class MetaShopItem(ListItem):

    prefix = "Total: "

    def __init__(self, price=0):
        ListItem.__init__(self)
        self.price = price
        self.actions = [CheckCartAction()]

    def sub_items(self):
        return self.actions

    def title(self):
        return MetaShopItem.prefix + str(self.price / 100.0) + u'€'

    def position(self):
        return -1

    def note(self):
        for action in self.actions:
            if action.note():
                return action.note()
        return None

    @classmethod
    def is_meta_item(cls, task):
        return task['title'][:len(MetaShopItem.prefix)] == MetaShopItem.prefix

    @classmethod
    def parse(cls, title, notes, sub_tasks):
        price = title[len(MetaShopItem.prefix):]
        return MetaShopItem(int(float(price) * 100))


class CheckCartAction(SubItem):

    def __init__(self):
        SubItem.__init__(self)
        self.notes = None

    # noinspection SpellCheckingInspection
    def title(self):
        return "Einkaufswagen und Liste vergleichen"

    def selected(self):
        return False

    def action(self, meta_shop):
        self.notes = meta_shop.shop_sync.detect_cart_list_differences()
        meta_shop.update()
        # meta_shop.revision = meta_shop.wu_list.update_item({'id': meta_shop.iid}, meta_shop.item, rebuild_notes=True)

    def note(self):
        return self.notes

    @classmethod
    def parse(cls, string):
        pass
