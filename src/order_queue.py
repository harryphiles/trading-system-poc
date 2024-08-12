from collections import deque
import heapq
from src.order_components import OrderSide, OrderStatus, Order
from src.logger import Logger


class HeapOrder:
    def __init__(self, price: float, order: Order) -> None:
        self.price = price
        self.order = order

    def __lt__(self, other) -> bool:
        if self.order.side == OrderSide.BUY:
            return self.price > other.price
        return self.price < other.price


class OrderQueue:
    def __init__(self, logger: Logger | None = None) -> None:
        self.queue = deque()
        self.order_map: dict[str, Order] = {}
        self.buy_orders: dict[float, list[Order]] = {}
        self.sell_orders: dict[float, list[Order]] = {}
        self.filled_orders: list[Order] = []
        self.orderbook_size = 0
        self.logger = logger

    def add_order(self, order: Order) -> None:
        """Add Order to queue before being processed."""
        self.queue.append(order)
        self.order_map[order.order_id] = order

    def _update_orderbooks(self, order: Order) -> None:
        """Updates orderbooks when Order was popped from the queue"""
        if order.side == OrderSide.BUY:
            if order.price not in self.buy_orders:
                self.buy_orders[order.price] = []
            self.buy_orders[order.price].append(order)
        else:
            if order.price not in self.sell_orders:
                self.sell_orders[order.price] = []
            self.sell_orders[order.price].append(order)
        self.orderbook_size += 1

    def get_next_order(self) -> Order | None:
        """Get the next Order for processing"""
        if self.queue:
            order: Order = self.queue.popleft()
            order.status = OrderStatus.PROCESSING
            self._update_orderbooks(order)
            if self.logger:
                self.logger.info(f"Processing order: {order.order_id}")
            return order
        return None

    def cancel_order(self, order_id: str) -> bool:
        """Cancel order if it's in either PENDING or PROCESSING state"""
        if order_id in self.order_map:
            order = self.order_map[order_id]
            if order.status in [OrderStatus.PENDING, OrderStatus.PROCESSING]:
                if order.status == OrderStatus.PENDING:
                    self.queue.remove(order)
                elif order.status == OrderStatus.PROCESSING:
                    order_book = (
                        self.buy_orders
                        if order.side == OrderSide.BUY
                        else self.sell_orders
                    )
                    if order.price in order_book and order in order_book[order.price]:
                        order_book[order.price].remove(order)
                        if not order_book[order.price]:
                            del order_book[order.price]
                        self.orderbook_size -= 1

                order.status = OrderStatus.CANCELLED
                del self.order_map[order_id]
                if self.logger:
                    self.logger.info(
                        f"Order cancelled: {order_id}, Orders (Total, Pending, Processing) "
                        f"({len(self.order_map)}, {len(self.queue)}, {self.orderbook_size})"
                    )
                return True

        if self.logger:
            self.logger.warning(f"Failed to cancel order: {order_id}")
        return False
