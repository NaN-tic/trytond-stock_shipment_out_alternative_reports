# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta


class StockConfiguration(metaclass=PoolMeta):
    __name__ = 'stock.configuration'

    delivery_note_action_report = fields.MultiValue(fields.Many2One(
            'ir.action.report', 'Report Template', required=True,
            help='Default report used on shipment out'))

    @classmethod
    def multivalue_model(cls, field):
        pool = Pool()
        if field == 'delivery_note_action_report':
            return pool.get('stock.configuration.sequence')
        return super().multivalue_model(field)


class StockConfigurationCompany(metaclass=PoolMeta):
    __name__ = 'stock.configuration.sequence'

    delivery_note_action_report = fields.Many2One(
        'ir.action.report', 'Report Template')
