# -*- coding: utf-8 -*-

import abc


class BarcodeDecoder:

    def __init__(self):
        pass

    @staticmethod
    @abc.abstractmethod
    def url(barcode):
        """

        :rtype: String
        """
        raise NotImplementedError('users must define __str__ to use this base class')

    @abc.abstractmethod
    def item(self, barcode):
        """

        :rtype: Item
        """
        raise NotImplementedError('users must define __str__ to use this base class')
