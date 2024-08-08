from src.order_components import OrderStatus
from src.logger import Logger


class MatchEngine:
    def __init__(self, logger: Logger | None = None) -> None:
        self.logger = logger

    def match_orders(
        self, buy_orders, sell_orders, filled_orders
    ) -> tuple[int, list[tuple]]:
        matches = []
        num_removed_orders = 0

        while buy_orders and sell_orders:
            buy_high = max(buy_orders.keys())
            sell_low = min(sell_orders.keys())

            if buy_high >= sell_low:
                buy_single_order = buy_orders[buy_high][0]
                sell_single_order = sell_orders[sell_low][0]

                matched_quantity = min(
                    buy_single_order.quantity, sell_single_order.quantity
                )
                matches.append(
                    (buy_single_order, sell_single_order, sell_low, matched_quantity)
                )

                buy_single_order.quantity -= matched_quantity
                sell_single_order.quantity -= matched_quantity
                buy_single_order.status = OrderStatus.PARTIALLY_FILLED
                sell_single_order.status = OrderStatus.PARTIALLY_FILLED

                if buy_single_order.quantity == 0:
                    mark_filled = buy_orders[buy_high].pop(0)
                    num_removed_orders += 1
                    mark_filled.status = OrderStatus.FILLED
                    filled_orders.append(mark_filled)
                    if not buy_orders[buy_high]:
                        del buy_orders[buy_high]

                if sell_single_order.quantity == 0:
                    mark_filled = sell_orders[sell_low].pop(0)
                    num_removed_orders += 1
                    mark_filled.status = OrderStatus.FILLED
                    filled_orders.append(mark_filled)
                    if not sell_orders[sell_low]:
                        del sell_orders[sell_low]

                self._log_matched_orders(
                    buy_single_order, sell_single_order, matched_quantity, sell_low
                )
            else:
                break

        return num_removed_orders, matches

    def _log_matched_orders(self, buy_order, sell_order, quantity, price):
        if self.logger:
            self.logger.info(
                f"-- Matched: Buy {buy_order.order_id} Sell {sell_order.order_id} for {quantity} units at ${price:.2f}"
            )
