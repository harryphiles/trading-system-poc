import unittest
from unittest.mock import Mock, patch
from src.order_components import Order, OrderSide, OrderStatus
from src.order_queue import OrderQueue
from src.match_engine import MatchEngine
from src.logger import Logger, LOGGING_CONFIG
from src.order_processor import OrderProcessor

class TestOrderProcessor(unittest.TestCase):
    def setUp(self):
        self.logger = Logger(
            __name__, LOGGING_CONFIG, "test_order_processor.log"
        ).logger
        self.order_queue = OrderQueue()
        self.match_engine = MatchEngine()
        self.order_processor = OrderProcessor(
            self.order_queue, self.match_engine, self.logger
        )
        Order.reset_id_generator()

    def test_receive_order(self):
        order = self.order_processor.receive_order("user1", OrderSide.BUY, 100.0, 10)

        self.assertIsInstance(order, Order)
        self.assertEqual(order.status, OrderStatus.PENDING)

    def test_cancel_order_success(self):
        order = self.order_processor.receive_order("user1", OrderSide.BUY, 100.0, 10)
        result = self.order_processor.cancel_order(order.order_id)

        self.assertTrue(result)
        self.assertNotIn(order.order_id, self.order_queue.order_map)
        self.assertNotIn(order, self.order_queue.queue)
        self.assertEqual(order.status, OrderStatus.CANCELLED)

    def test_process_single_order(self):
        order1 = self.order_processor.receive_order("user1", OrderSide.BUY, 100.0, 10)
        self.order_processor.process_single_order()
        order2 = self.order_processor.receive_order("user2", OrderSide.SELL, 100.0, 10)
        self.order_processor.process_single_order()
        order3 = self.order_processor.receive_order("user3", OrderSide.BUY, 100.0, 10)
        self.order_processor.process_single_order()
        order4 = self.order_processor.receive_order("user4", OrderSide.SELL, 100.0, 5)
        self.order_processor.process_single_order()

        self.assertEqual(order1.status, order2.status)
        self.assertEqual(order3.status, OrderStatus.PARTIALLY_FILLED)
        self.assertEqual(order3.quantity, 5)
        self.assertEqual(order4.status, OrderStatus.FILLED)

    def test_process_single_order_no_order(self):
        self.order_queue = Mock(spec=OrderQueue)
        self.match_engine = Mock(spec=MatchEngine)
        self.order_queue.get_next_order.return_value = None
        self.order_processor.process_single_order()
        self.match_engine.match_orders.assert_not_called()

    def test_process_orders(self):
        self.order_processor.receive_order("user1", OrderSide.BUY, 100.0, 10)
        self.order_processor.receive_order("user2", OrderSide.SELL, 100.0, 10)
        self.order_processor.receive_order("user3", OrderSide.BUY, 100.0, 10)
        self.order_processor.receive_order("user4", OrderSide.SELL, 100.0, 5)

        self.order_processor.process_orders()

        self.assertEqual(self.order_processor.transactions, 2)
        self.assertEqual(self.order_queue.orderbook_size, 1)

    def test_process_orders_empty_queue(self):
        self.order_queue = Mock(spec=OrderQueue)
        self.match_engine = Mock(spec=MatchEngine)
        self.order_queue.get_next_order.return_value = None
        self.order_processor.process_orders()
        self.match_engine.match_orders.assert_not_called()


if __name__ == "__main__":
    unittest.main()
