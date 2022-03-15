# This file is part stock_shipment_out_alternative_reports module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import shipment
from . import configuration


def register():
    Pool.register(
        configuration.StockConfigurationCompany,
        configuration.StockConfiguration,
        shipment.PartyAlternativeReport,
        shipment.ShipmentOut,
        module='stock_shipment_out_alternative_reports', type_='model')
    Pool.register(
        module='stock_shipment_out_alternative_reports', type_='wizard')
    Pool.register(
        shipment.DeliveryNote,
        module='stock_shipment_out_alternative_reports', type_='report')
