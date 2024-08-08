import unittest
from unittest.mock import Mock, patch
from src.order_components import Order, OrderSide
from src.order_queue import OrderQueue
from src.match_engine import MatchEngine
from src.logger import Logger, LOGGING_CONFIG
from src.order_processor import OrderProcessor


class TestOrderProcessor(unittest.TestCase):
    def setUp(self):
        self.logger = Logger(
            __name__, LOGGING_CONFIG, "test_order_processor.log"
        ).logger
        self.order_queue = Mock(spec=OrderQueue)
        self.order_queue.order_map = {}
        self.order_queue.queue = []
        self.order_queue.orderbook_size = 0
        self.order_queue.buy_orders = {}
        self.order_queue.sell_orders = {}
        self.order_queue.filled_orders = []
        self.match_engine = Mock(spec=MatchEngine)
        self.order_processor = OrderProcessor(
            self.order_queue, self.match_engine, self.logger
        )
        Order.reset_id_generator()

    def test_receive_order(self):
        order = self.order_processor.receive_order("user1", OrderSide.BUY, 100.0, 10)
        self.assertIsInstance(order, Order)
        self.order_queue.add_order.assert_called_once_with(order)

    def test_cancel_order(self):
        self.order_queue.cancel_order.return_value = True
        result = self.order_processor.cancel_order("order1")
        self.assertTrue(result)
        self.order_queue.cancel_order.assert_called_once_with("order1")

    def test_process_single_order(self):
        mock_order = Mock(spec=Order)
        self.order_queue.get_next_order.return_value = mock_order
        self.match_engine.match_orders.return_value = (1, [("match1", "match2")])

        self.order_processor.process_single_order()

        self.order_queue.get_next_order.assert_called_once()
        self.match_engine.match_orders.assert_called_once()
        self.assertEqual(self.order_processor.transactions, 1)

    def test_process_single_order_no_order(self):
        self.order_queue.get_next_order.return_value = None
        self.order_processor.process_single_order()
        self.match_engine.match_orders.assert_not_called()

    def test_process_orders(self):
        mock_orders = [Mock(spec=Order) for _ in range(3)]
        self.order_queue.get_next_order.side_effect = mock_orders + [None]
        self.match_engine.match_orders.side_effect = [
            (1, [("match1", "match2")]),
            (0, []),
            (2, [("match3", "match4"), ("match5", "match6")]),
        ]

        self.order_processor.process_orders()

        self.assertEqual(self.order_queue.get_next_order.call_count, 4)
        self.assertEqual(self.match_engine.match_orders.call_count, 3)
        self.assertEqual(self.order_processor.transactions, 3)

    def test_process_orders_empty_queue(self):
        self.order_queue.get_next_order.return_value = None
        self.order_processor.process_orders()
        self.match_engine.match_orders.assert_not_called()

    @patch("src.order_processor.Order")
    def test_receive_order_creates_correct_order(self, mock_order):
        mock_order.return_value = Mock(spec=Order, order_id="test_id")
        order = self.order_processor.receive_order("user1", OrderSide.BUY, 100.0, 10)
        mock_order.assert_called_once_with("user1", OrderSide.BUY, 100.0, 10)
        self.order_queue.add_order.assert_called_once_with(mock_order.return_value)


if __name__ == "__main__":
    unittest.main()
