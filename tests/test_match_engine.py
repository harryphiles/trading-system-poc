import unittest
from src.match_engine import MatchEngine
from src.order_queue import OrderQueue
from src.order_components import Order, OrderSide, OrderStatus
from src.logger import Logger, LOGGING_CONFIG


class TestMatchEngine(unittest.TestCase):
    def setUp(self):
        self.logger = Logger(__name__, LOGGING_CONFIG, "test_match_engine.log").logger
        self.match_engine = MatchEngine(self.logger)
        self.order_queue = OrderQueue()
        Order.reset_id_generator()

    def test_basic_match(self):
        orders = [
            Order(1, OrderSide.BUY, 100, 10),
            Order(2, OrderSide.SELL, 100, 10),
        ]
        for order in orders:
            self.order_queue.add_order(order)
            self.order_queue.get_next_order()

        num_removed, matches = self.match_engine.match_orders(self.order_queue)
        matched_buy_order, matched_sell_order, *_ = matches[0]

        self.assertEqual(num_removed, 2)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matched_buy_order.status, OrderStatus.FILLED)
        self.assertEqual(matched_sell_order.status, OrderStatus.FILLED)

    def test_partial_match(self):
        orders = [
            Order(1, OrderSide.BUY, 100, 15),
            Order(2, OrderSide.SELL, 100, 10),
        ]
        for order in orders:
            self.order_queue.add_order(order)
            self.order_queue.get_next_order()

        num_removed, matches = self.match_engine.match_orders(self.order_queue)
        matched_buy_order, matched_sell_order, *_ = matches[0]


        self.assertEqual(num_removed, 1)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matched_buy_order.quantity, 5)
        self.assertEqual(matched_buy_order.status, OrderStatus.PARTIALLY_FILLED)
        self.assertEqual(matched_sell_order.status, OrderStatus.FILLED)

    def test_multiple_matches(self):
        orders = [
            Order(1, OrderSide.BUY, 100, 10),
            Order(2, OrderSide.BUY, 100, 5),
            Order(3, OrderSide.SELL, 95, 8),
            Order(4, OrderSide.SELL, 98, 10)
        ]
        tracked_return = []
        for order in orders:
            self.order_queue.add_order(order)
            self.order_queue.get_next_order()
            num_removed, matches = self.match_engine.match_orders(self.order_queue)
            tracked_return.append((num_removed, matches))
        
        # Check match orders after 3rd order is added
        num_removed, matches = tracked_return[2]
        matched_buy_order, matched_sell_order, *_ = matches[0]
        self.assertEqual(matched_buy_order.order_id, "00000001")
        self.assertEqual(matched_sell_order.order_id, "00000003")

        # Check match orders after 4th order is added
        num_removed, matches = tracked_return[3]
        matched_buy_order, matched_sell_order, *_ = matches[0]
        self.assertEqual(matched_buy_order.order_id, "00000001")
        self.assertEqual(matched_sell_order.order_id, "00000004")
        matched_buy_order, matched_sell_order, *_ = matches[1]
        self.assertEqual(matched_buy_order.order_id, "00000002")
        self.assertEqual(matched_sell_order.order_id, "00000004")

        self.assertEqual(len(self.order_queue.buy_orders), 0)
        self.assertEqual(len(self.order_queue.sell_orders), 1)
        self.assertEqual(self.order_queue.sell_orders[0].order.quantity, 3)
        self.assertEqual(len(self.order_queue.filled_orders), 3)

    def test_no_match(self):
        orders = [
            Order(1, OrderSide.BUY, 90, 10),
            Order(2, OrderSide.SELL, 100, 10),
        ]
        for order in orders:
            self.order_queue.add_order(order)
            self.order_queue.get_next_order()

        num_removed, matches = self.match_engine.match_orders(self.order_queue)

        self.assertEqual(num_removed, 0)
        self.assertEqual(len(matches), 0)
        self.assertEqual(len(self.order_queue.filled_orders), 0)


if __name__ == "__main__":
    unittest.main()
