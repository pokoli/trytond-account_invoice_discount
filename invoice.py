from decimal import Decimal
from trytond.model import fields
from trytond.pool import PoolMeta
from trytond.pyson import Eval

__all__ = ['InvoiceLine']
__metaclass__ = PoolMeta

STATES = {
    'invisible': Eval('type') != 'line',
    'required': Eval('type') == 'line',
    }


class InvoiceLine:
    __name__ = 'account.invoice.line'

    gross_unit_price = fields.Numeric('Gross Price', digits=(16, 4),
        states=STATES, on_change=['gross_unit_price', 'discount'])
    discount = fields.Numeric('Discount', digits=(16, 4), states=STATES,
        on_change=['gross_unit_price', 'discount'])

    @classmethod
    def __setup__(cls):
        super(InvoiceLine, cls).__setup__()
        cls.unit_price.states['readonly'] = True
        cls.unit_price.digits = (20, 8)
        if not 'discount' in cls.product.on_change:
            cls.product.on_change.append('discount')
        if not 'discount' in cls.amount.on_change_with:
            cls.amount.on_change_with.append('discount')
        if not 'gross_unit_price' in cls.amount.on_change_with:
            cls.amount.on_change_with.append('gross_unit_price')

    @staticmethod
    def default_discount():
        return Decimal(0)

    def update_prices(self):
        unit_price = None
        gross_unit_price = self.gross_unit_price
        if self.gross_unit_price is not None and self.discount is not None:
            unit_price = self.gross_unit_price * (1-self.discount)
            digits = self.__class__.unit_price.digits[1]
            unit_price = unit_price.quantize(Decimal(str(10.0 ** -digits)))

            gross_unit_price = unit_price / (1-self.discount)
            digits = self.__class__.gross_unit_price.digits[1]
            gross_unit_price = gross_unit_price.quantize(
                Decimal(str(10.0 ** -digits)))
        return {
            'gross_unit_price': gross_unit_price,
            'unit_price': unit_price,
            }

    def on_change_gross_unit_price(self):
        return self.update_prices()

    def on_change_discount(self):
        return self.update_prices()

    def on_change_product(self):
        res = super(InvoiceLine, self).on_change_product()
        if 'unit_price' in res:
            self.gross_unit_price = res['unit_price']
            self.discount
            res.update(self.update_prices())
        return res
