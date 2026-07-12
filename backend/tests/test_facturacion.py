import unittest
from datetime import date, timedelta
from decimal import Decimal
from types import SimpleNamespace

from app.routers.facturacion import calcular_totales, estado_presentacion, TRANSICIONES


class FacturacionTests(unittest.TestCase):
    def test_totales_se_calculan_con_decimal(self):
        lineas = [
            SimpleNamespace(cantidad=Decimal("2"), valor_unitario=Decimal("100000.55")),
            SimpleNamespace(cantidad=Decimal("1"), valor_unitario=Decimal("50000.10")),
        ]
        subtotal, impuesto, total = calcular_totales(lineas, Decimal("19"))
        self.assertEqual(subtotal, Decimal("250001.20"))
        self.assertEqual(impuesto, Decimal("47500.23"))
        self.assertEqual(total, Decimal("297501.43"))

    def test_emitida_vencida_se_presenta_como_vencida(self):
        factura = SimpleNamespace(estado="EMITIDA", fecha_vencimiento=date.today() - timedelta(days=1))
        self.assertEqual(estado_presentacion(factura), "VENCIDA")

    def test_transiciones_contables_son_cerradas(self):
        self.assertEqual(TRANSICIONES["BORRADOR"], {"EMITIDA", "ANULADA"})
        self.assertEqual(TRANSICIONES["EMITIDA"], {"PAGADA", "ANULADA"})
        self.assertEqual(TRANSICIONES["PAGADA"], set())


if __name__ == "__main__":
    unittest.main()
