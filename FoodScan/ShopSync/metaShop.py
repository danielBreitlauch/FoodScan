# -*- coding: utf-8 -*-
from pysimplelog import Logger

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
            if self.wu_list.is_meta_item(new_task):
                if self.iid != new_task['id'] or self.revision != new_task['revision']:
                    self.iid = new_task['id']
                    self.revision = new_task['revision']
                    return True
                return False

        self.iid = self.wu_list.create_item(self.item)
        self.revision = 0
        return True

    def sync(self):
        for sub_task in self.wu_list.task_sub_tasks(self.iid):
            for action in self.item.actions:
                if sub_task['title'] == action.title():
                    if sub_task['completed']:
                        for a in self.item.actions:
                            a.notes = None
                        action.action(self)
                        self.revision = self.wu_list.update_item({'id': self.iid}, self.item, rebuild_notes=True)
                    break

    def set_price(self, price):
        if price != self.item.price:
            self.item.price = price
            self.revision = self.wu_list.update_item({'id': self.iid, 'title': ""}, self.item)


class MetaShopItem(ListItem):

    prefix = "Total: "

    def __init__(self, price=0):
        ListItem.__init__(self)
        self.price = price
        self.actions = [ClearAction(), CheckCartAction()]

    def sub_items(self):
        return self.actions

    def title(self):
        return MetaShopItem.prefix + str(self.price / 100.0) + '€'

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
        self.logger = Logger('CheckCartAction')
        self.notes = None

    # noinspection SpellCheckingInspection
    def title(self):
        return "Einkaufswagen und Liste vergleichen"

    def selected(self):
        return False

    def action(self, meta_shop):
        cart_items = meta_shop.shop_sync.shop.cart()
        shop_items = []

        msg0 = ""
        msg1 = ""
        for task, item in meta_shop.wu_list.list_items():
            shop_item = item.selected_shop_item()
            if shop_item:
                shop_items.append(shop_item)
                if shop_item in cart_items:
                    for c in cart_items:
                        if c.name == shop_item.name:
                            if shop_item.amount != c.amount:
                                self.logger.warn(
                                    "Task item and shop item amounts differ: " + shop_item.name.encode('utf-8'))
                                msg0 += shop_item.name.encode('utf-8') + ": " + str(shop_item.amount) + " vs. " + str(
                                    c.amount) + "\n"
                            break
                else:
                    self.logger.warn("Task item without shop item: " + shop_item.name.encode('utf-8'))
                    msg1 += " - " + shop_item.name.encode('utf-8') + "\n"

        msg2 = ""
        for cart_item in cart_items:
            if cart_item not in shop_items:
                self.logger.warn("Cart item without task: " + cart_item.name.encode('utf-8'))
                msg2 += " + " + cart_item.name.encode('utf-8') + "\n"

        msg = ""
        if msg0:
            msg += "Mengenunterschiede: Liste vs. Einkaufswagen\n" + msg0

        if msg1:
            msg += "\nNicht im Einkaufswagen gefunden:\n" + msg1

        if msg2:
            msg += "\nNicht auf der Liste gefunden:\n" + msg2

        self.notes = msg

    def note(self):
        return self.notes

    @classmethod
    def parse(cls, string):
        pass


class ClearAction(SubItem):

    def __init__(self):
        SubItem.__init__(self)
        self.logger = Logger('ClearAction')

    # noinspection SpellCheckingInspection
    def title(self):
        return "Liste leeren"

    def selected(self):
        return False

    def action(self, meta_shop):
        for task, item in meta_shop.wu_list.list_items():
            meta_shop.wu_list.delete_item(task)

    def note(self):
        return None

    @classmethod
    def parse(cls, string):
        pass
