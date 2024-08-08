import unittest
from src.match_engine import MatchEngine
from src.order_components import Order, OrderSide, OrderStatus
from src.logger import Logger, LOGGING_CONFIG


class TestMatchEngine(unittest.TestCase):
    def setUp(self):
        self.logger = Logger(__name__, LOGGING_CONFIG, "test_match_engine.log").logger
        self.match_engine = MatchEngine(self.logger)
        Order.reset_id_generator()

    def test_basic_match(self):
        buy_orders = {100: [Order(1, OrderSide.BUY, 100, 10)]}
        sell_orders = {100: [Order(2, OrderSide.SELL, 100, 10)]}
        filled_orders = []

        num_removed, matches = self.match_engine.match_orders(
            buy_orders, sell_orders, filled_orders
        )

        self.assertEqual(num_removed, 2)
        self.assertEqual(len(matches), 1)
        self.assertEqual(len(filled_orders), 2)
        self.assertEqual(filled_orders[0].status, OrderStatus.FILLED)
        self.assertEqual(filled_orders[1].status, OrderStatus.FILLED)

    def test_partial_match(self):
        buy_orders = {100: [Order(1, OrderSide.BUY, 100, 15)]}
        sell_orders = {100: [Order(2, OrderSide.SELL, 100, 10)]}
        filled_orders = []

        num_removed, matches = self.match_engine.match_orders(
            buy_orders, sell_orders, filled_orders
        )

        self.assertEqual(num_removed, 1)
        self.assertEqual(len(matches[0]), 4)
        self.assertEqual(len(filled_orders), 1)
        self.assertEqual(
            filled_orders[0].order_id, "00000002"
        )
        self.assertEqual(buy_orders[100][0].quantity, 5)
        self.assertEqual(buy_orders[100][0].status, OrderStatus.PARTIALLY_FILLED)

    def test_multiple_matches(self):
        buy_orders = {
            100: [Order(1, OrderSide.BUY, 100, 10), Order(2, OrderSide.BUY, 100, 5)]
        }
        sell_orders = {
            95: [Order(3, OrderSide.SELL, 95, 8)],
            98: [Order(4, OrderSide.SELL, 98, 10)],
        }
        filled_orders = []

        num_removed, matches = self.match_engine.match_orders(
            buy_orders, sell_orders, filled_orders
        )

        self.assertEqual(num_removed, 3)
        self.assertEqual(len(matches), 3)
        self.assertEqual(len(filled_orders), 3)

        if 100 in buy_orders:
            self.assertEqual(buy_orders[100][0].quantity, 10)
            self.assertEqual(buy_orders[100][0].status, OrderStatus.PROCESSING)
        else:
            self.assertTrue(
                any(
                    order.order_id == "00000001" and order.quantity == 0
                    for order in filled_orders
                )
            )
            self.assertTrue(
                any(
                    order.order_id == "00000002" and order.quantity == 0
                    for order in filled_orders
                )
            )

    def test_no_match(self):
        buy_orders = {90: [Order(1, OrderSide.BUY, 90, 10)]}
        sell_orders = {100: [Order(2, OrderSide.SELL, 100, 10)]}
        filled_orders = []

        num_removed, matches = self.match_engine.match_orders(
            buy_orders, sell_orders, filled_orders
        )

        self.assertEqual(num_removed, 0)
        self.assertEqual(len(matches), 0)
        self.assertEqual(len(filled_orders), 0)


if __name__ == "__main__":
    unittest.main()
