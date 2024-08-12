from src.order_components import OrderStatus, Order
from src.order_queue import OrderQueue
from src.logger import Logger


class MatchEngine:
    def __init__(self, logger: Logger | None = None) -> None:
        self.logger = logger

    def match_orders(self, order_queue: OrderQueue) -> tuple[int, list[tuple]]:
        matches = []
        num_removed_orders = 0

        while True:
            best_buy: Order = order_queue.get_best_buy_order()
            best_sell: Order = order_queue.get_best_sell_order()

            # Case for stopping matching process
            if (
                not best_buy or not best_sell or
                best_sell.price > best_buy.price
            ):
                break

            buy_order: Order = order_queue.remove_best_buy_order()
            sell_order: Order = order_queue.remove_best_sell_order()

            matched_quantity = min(buy_order.quantity, sell_order.quantity)
            matches.append((buy_order, sell_order, sell_order.price, matched_quantity))

            # Subtract quantity as result of transaction
            buy_order.quantity -= matched_quantity
            sell_order.quantity -= matched_quantity
            # Mark each as partially_filled as preliminary action
            buy_order.status = OrderStatus.PARTIALLY_FILLED
            sell_order.status = OrderStatus.PARTIALLY_FILLED\

            # Update Order according to its remaining quantity
            if buy_order.quantity > 0:
                order_queue.update_orderbooks(buy_order)
            else:
                num_removed_orders += 1
                buy_order.status = OrderStatus.FILLED
                order_queue.filled_orders.append(buy_order)

            if sell_order.quantity > 0:
                order_queue.update_orderbooks(sell_order)
            else:
                num_removed_orders += 1
                sell_order.status = OrderStatus.FILLED
                order_queue.filled_orders.append(sell_order)

            self._log_matched_orders(buy_order, sell_order, matched_quantity, sell_order.price)

        return num_removed_orders, matches

    def _log_matched_orders(self, buy_order, sell_order, quantity, price):
        if self.logger:
            self.logger.info(
                f"-- Matched: Buy {buy_order.order_id} Sell {sell_order.order_id} for {quantity} units at ${price:.2f}"
            )
