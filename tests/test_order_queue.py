import unittest
from src.order_queue import OrderQueue
from src.order_components import Order, OrderSide, OrderStatus
from src.logger import Logger, LOGGING_CONFIG


class TestOrderQueue(unittest.TestCase):
    def setUp(self):
        self.logger = Logger(__name__, LOGGING_CONFIG, "test_order_queue.log").logger
        self.order_queue = OrderQueue(self.logger)
        Order.reset_id_generator()

    def test_add_order(self):
        order = Order(100, OrderSide.BUY, 10, 5)
        self.order_queue.add_order(order)
        self.assertEqual(len(self.order_queue.queue), 1)
        self.assertEqual(self.order_queue.order_map[order.order_id], order)

    def test_get_next_order(self):
        order1 = Order(1, OrderSide.BUY, 100, 5)
        order2 = Order(2, OrderSide.SELL, 101, 3)
        self.order_queue.add_order(order1)
        self.order_queue.add_order(order2)

        next_order = self.order_queue.get_next_order()
        self.assertEqual(next_order, order1)
        self.assertEqual(next_order.status, OrderStatus.PROCESSING)
        self.assertEqual(len(self.order_queue.queue), 1)
        self.assertEqual(self.order_queue.orderbook_size, 1)
        self.assertIn(100, self.order_queue.buy_orders)

    def test_cancel_pending_order(self):
        order = Order(100, OrderSide.BUY, 10, 5)
        self.order_queue.add_order(order)
        result = self.order_queue.cancel_order(order.order_id)
        self.assertTrue(result)
        self.assertEqual(len(self.order_queue.queue), 0)
        self.assertNotIn(order.order_id, self.order_queue.order_map)

    def test_cancel_processing_order(self):
        order = Order(100, OrderSide.BUY, 10, 5)
        self.order_queue.add_order(order)
        self.order_queue.get_next_order()
        result = self.order_queue.cancel_order(order.order_id)
        self.assertTrue(result)
        self.assertEqual(self.order_queue.orderbook_size, 0)
        self.assertNotIn(100, self.order_queue.buy_orders)
        self.assertNotIn(order.order_id, self.order_queue.order_map)

    def test_cancel_nonexistent_order(self):
        result = self.order_queue.cancel_order("nonexistent_id")
        self.assertFalse(result)

    def test_order_books_update(self):
        buy_order = Order(1, OrderSide.BUY, 100, 5)
        sell_order = Order(2, OrderSide.SELL, 101, 3)
        self.order_queue.add_order(buy_order)
        self.order_queue.add_order(sell_order)

        self.order_queue.get_next_order()
        self.order_queue.get_next_order()

        self.assertIn(100, self.order_queue.buy_orders)
        self.assertIn(101, self.order_queue.sell_orders)
        self.assertEqual(self.order_queue.orderbook_size, 2)

    def test_empty_queue(self):
        self.assertIsNone(self.order_queue.get_next_order())

    def test_cancel_last_order_at_price(self):
        order = Order(100, OrderSide.BUY, 10, 5)
        self.order_queue.add_order(order)
        self.order_queue.get_next_order()
        self.order_queue.cancel_order(order.order_id)
        self.assertNotIn(100, self.order_queue.buy_orders)


if __name__ == "__main__":
    unittest.main()
