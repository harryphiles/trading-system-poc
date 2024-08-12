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
        self.buy_orders: list[HeapOrder] = []  # max heap
        self.sell_orders: list[HeapOrder] = []  # min heap
        self.filled_orders: list[Order] = []
        self.orderbook_size = 0
        self.logger = logger

    def add_order(self, order: Order) -> None:
        """Add Order to queue before being processed."""
        self.queue.append(order)
        self.order_map[order.order_id] = order

    def update_orderbooks(self, order: Order) -> None:
        """Updates orderbooks when Order was popped from the queue"""
        heap_order = HeapOrder(
            price=-order.price if order.side == OrderSide.BUY else order.price,
            order=order,
        )
        if order.side == OrderSide.BUY:
            heapq.heappush(self.buy_orders, heap_order)
        else:
            heapq.heappush(self.sell_orders, heap_order)
        self.orderbook_size += 1

    def get_next_order(self) -> Order | None:
        """Get the next Order for processing"""
        if self.queue:
            order: Order = self.queue.popleft()
            order.status = OrderStatus.PROCESSING
            self.update_orderbooks(order)
            if self.logger:
                self.logger.info(f"Processing order: {order.order_id}")
            return order
        return None

    def cancel_order(self, order_id: str) -> bool:
        """Cancel order if it's in either PENDING or PROCESSING state"""
        if order_id in self.order_map:
            order: Order = self.order_map[order_id]
            if order.status in [OrderStatus.PENDING, OrderStatus.PROCESSING]:
                if order.status == OrderStatus.PENDING:
                    self.queue.remove(order)
                elif order.status == OrderStatus.PROCESSING:
                    # Remove from the appropriate order book
                    order_book: list[HeapOrder] = (
                        self.buy_orders
                        if order.side == OrderSide.BUY
                        else self.sell_orders
                    )
                    order_book: list[HeapOrder] = [
                        ho for ho in order_book if ho.order.order_id != order_id
                    ]
                    heapq.heapify(order_book)
                    if order.side == OrderSide.BUY:
                        self.buy_orders = order_book
                    else:
                        self.sell_orders = order_book
                    self.orderbook_size -= 1

                order.status = OrderStatus.CANCELLED
                del self.order_map[order_id]
                if self.logger:
                    self.logger.info(f"Order cancelled: {order_id}")
                return True
        if self.logger:
            self.logger.warning(f"Failed to cancel order: {order_id}")
        return False

    def get_best_buy_order(self) -> Order | None:
        return self.buy_orders[0].order if self.buy_orders else None

    def get_best_sell_order(self) -> Order | None:
        return self.sell_orders[0].order if self.sell_orders else None

    def remove_best_buy_order(self) -> Order | None:
        if self.buy_orders:
            heap_order = heapq.heappop(self.buy_orders)
            self.orderbook_size -= 1
            return heap_order.order
        return None

    def remove_best_sell_order(self) -> Order | None:
        if self.sell_orders:
            heap_order = heapq.heappop(self.sell_orders)
            self.orderbook_size -= 1
            return heap_order.order
        return None
