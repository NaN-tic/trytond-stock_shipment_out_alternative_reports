# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, If
from trytond.modules.html_report.engine import HTMLReportMixin
from trytond.report import Report


class PartyAlternativeReport(metaclass=PoolMeta):
    __name__ = 'party.alternative_report'

    @classmethod
    def __setup__(cls):
        super(PartyAlternativeReport, cls).__setup__()
        option = ('stock.shipment.out', 'Shipment Out')
        if option not in cls.model_name.selection:
            cls.model_name.selection.append(option)


class Sale(metaclass=PoolMeta):
    __name__ = 'sale.sale'

    def create_shipment(self, shipment_type):
        pool = Pool()
        Shipment = pool.get('stock.shipment.out')

        shipments = super().create_shipment(shipment_type)
        if not shipments:
            return

        if shipment_type != 'out':
            return shipments
        to_save = []
        for shipment in shipments:
            available_reports = shipment.on_change_with_available_reports()
            if available_reports:
                shipment.delivery_note_report = available_reports[0]
                to_save.append(shipment)

        Shipment.save(to_save)
        return shipments


class ShipmentOut(metaclass=PoolMeta):
    __name__ = 'stock.shipment.out'

    available_reports = fields.Function(fields.Many2Many('ir.action.report',
        None, None, 'Available Reports'), 'on_change_with_available_reports')
    delivery_note_report = fields.Many2One('ir.action.report',
        'Report Template', domain=[
            If(Eval('state') == 'draft',
                ('id', 'in', Eval('available_reports', [])),
                ()),
            ],
        states={
            'readonly': ~Eval('state').in_(['draft']),
            })

    @staticmethod
    def default_delivery_note_report():
        Config = Pool().get('stock.configuration')
        config = Config(1)

        return (config and config.delivery_note_action_report
            and config.delivery_note_action_report.id or None)

    @fields.depends('customer', '_parent_customer.alternative_reports')
    def on_change_with_available_reports(self, name=None):
        default_report = self.default_delivery_note_report()
        if not self.customer:
            return [default_report]
        alternative_reports = [ar.report.id for ar in
            self.customer.alternative_reports
            if ar.model_name == 'stock.shipment.out']
        if default_report not in alternative_reports:
            alternative_reports.append(default_report)
        return alternative_reports

    def get_available_reports(self, name=None):
        if not self.customer:
            return []

        alternative_reports = self.alternative_reports
        default_report = self.default_delivery_note_report_report()
        if default_report and default_report not in alternative_reports:
            alternative_reports.append(default_report)
        return alternative_reports

    @fields.depends('delivery_note_report',
        methods=['on_change_with_available_reports', ])
    def on_change_customer(self):
        super().on_change_customer()

        default_report = self.default_delivery_note_report()

        if not self.customer:
            self.delivery_note_report = default_report
            return

        alternative_reports = self.on_change_with_available_reports()
        if default_report in alternative_reports:
            alternative_reports.remove(default_report)
        if alternative_reports and len(alternative_reports) == 1:
            self.delivery_note_report = alternative_reports[0]
        elif alternative_reports and len(alternative_reports) > 1:
            # force the user to choose one
            self.delivery_note_report = None
        elif not self.delivery_note_report:
            self.delivery_note_report = default_report


class DeliveryNote(Report):
    ''' Delivery Note '''
    __name__ = 'stock.shipment.out.delivery'

    @classmethod
    def execute(cls, ids, data):
        pool = Pool()
        Shipment = pool.get('stock.shipment.out')
        Report = pool.get('ir.action.report')
        Config = pool.get('stock.configuration')
        config = Config(1)

        action_report = (config and config.delivery_note_action_report
            and config.delivery_note_action_report.id or None)

        if not action_report:
            raise Exception('Error', 'Report (%s) not find!' % cls.__name__)

        action_report = Report(action_report)

        reports = {}
        for id_ in ids:
            shipment = Shipment(id_)
            report = shipment.delivery_note_report or action_report
            if report not in reports:
                reports[report] = []
            reports[report].append(id_)

        if not reports:
            raise Exception('Error', 'Report (%s) not find!' % cls.__name__)

        documents = []
        for action, x_ids in reports.items():
            new_data = {
                'model': 'stock.shipment.out',
                'id': x_ids[0],
                'ids': x_ids,
                'action_id': action.id
            }
            report_class = pool.get(action.report_name, 'report')
            if action.single:
                for id_ in x_ids:
                    (oext, content, direct_print,
                        filename) = report_class.execute([id_], new_data)
                    documents.append(content)
            else:
                (oext, content, direct_print,
                    filename) = report_class.execute(x_ids, new_data)
                documents += content

        if len(documents) > 1:
            merged = HTMLReportMixin.merge_pdfs(documents)
            documents = [merged]

        return (oext, documents[0], direct_print, filename)
