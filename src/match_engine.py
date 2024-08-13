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
            if not best_buy or not best_sell or best_sell.price > best_buy.price:
                break

            matched_quantity = min(best_buy.quantity, best_sell.quantity)
            matches.append((best_buy, best_sell, best_sell.price, matched_quantity))

            # Subtract quantity as result of transaction
            best_buy.quantity -= matched_quantity
            best_sell.quantity -= matched_quantity
            # Mark each as partially_filled as preliminary action
            best_buy.status = OrderStatus.PARTIALLY_FILLED
            best_sell.status = OrderStatus.PARTIALLY_FILLED

            # Remove buy or sell order when their quantities reach zero
            if best_buy.quantity == 0:
                num_removed_orders += 1
                best_buy.status = OrderStatus.FILLED
                order_queue.remove_best_buy_order()
                order_queue.filled_orders.append(best_buy)
            if best_sell.quantity == 0:
                num_removed_orders += 1
                best_sell.status = OrderStatus.FILLED
                order_queue.remove_best_sell_order()
                order_queue.filled_orders.append(best_sell)

            self._log_matched_orders(
                best_buy, best_sell, matched_quantity, best_sell.price
            )

        return num_removed_orders, matches

    def _log_matched_orders(self, buy_order, sell_order, quantity, price):
        if self.logger:
            self.logger.info(
                f"-- Matched: Buy {buy_order.order_id} Sell {sell_order.order_id} for {quantity} units at ${price:.2f}"
            )
