from src.order_components import OrderSide, Order
from src.order_queue import OrderQueue
from src.match_engine import MatchEngine
from src.logger import Logger


class OrderProcessor:
    def __init__(
        self,
        order_queue: OrderQueue,
        match_engine: MatchEngine,
        logger: Logger | None = None,
    ) -> None:
        self.order_queue = order_queue
        self.match_engine = match_engine
        self.transactions = 0
        self.logger = logger

    def receive_order(
        self, user_id: str, side: OrderSide, price: float, quantity: int
    ) -> Order:
        order = Order(user_id, side, price, quantity)
        self.order_queue.add_order(order)
        self._log_order_received(order)
        return order

    def cancel_order(self, order_id: str) -> bool:
        return self.order_queue.cancel_order(order_id)

    def process_single_order(self) -> None:
        order = self.order_queue.get_next_order()
        if order:
            num_removed_orders, matches = self.match_engine.match_orders(
                buy_orders=self.order_queue.buy_orders,
                sell_orders=self.order_queue.sell_orders,
                filled_orders=self.order_queue.filled_orders,
            )
            self.transactions += len(matches)
            self.order_queue.orderbook_size -= num_removed_orders

            self._log_order_processing_summary()

    def process_orders(self) -> None:
        """Use of this function is limited to gauge performance of the match engine when given large amount of orders."""
        while True:
            order = self.order_queue.get_next_order()
            if not order:
                break

            self._log_before_matching()

            num_removed_orders, matches = self.match_engine.match_orders(
                buy_orders=self.order_queue.buy_orders,
                sell_orders=self.order_queue.sell_orders,
                filled_orders=self.order_queue.filled_orders,
            )
            self.transactions += len(matches)
            self.order_queue.orderbook_size -= num_removed_orders

            self._log_order_processing_summary()

    def _log_order_received(self, order: Order) -> None:
        if self.logger:
            self.logger.info(
                f"Order received: {order.order_id}, Orders (Total, Pending) ({len(self.order_queue.order_map)}, {len(self.order_queue.queue)})"
            )

    def _log_before_matching(self) -> None:
        if self.logger:
            self.logger.info(
                f"-- Before matching - Orders (Total, Remaining): ({len(self.order_queue.order_map)}, {self.order_queue.orderbook_size})"
            )

    def _log_order_processing_summary(self) -> None:
        if self.logger:
            self.logger.info(
                f"-- Orders (Total, Remaining, Filled, Transactions): ({len(self.order_queue.order_map)}, {self.order_queue.orderbook_size}, {len(self.order_queue.filled_orders)}, {self.transactions})"
            )
