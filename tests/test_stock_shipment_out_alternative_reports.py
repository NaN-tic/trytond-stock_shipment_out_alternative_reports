# This file is part stock_shipment_out_alternative_reports module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import unittest


from trytond.tests.test_tryton import ModuleTestCase
from trytond.tests.test_tryton import suite as test_suite


class StockShipmentOutAlternativeReportsTestCase(ModuleTestCase):
    'Test Stock Shipment Out Alternative Reports module'
    module = 'stock_shipment_out_alternative_reports'


def suite():
    suite = test_suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
            StockShipmentOutAlternativeReportsTestCase))
    return suite
