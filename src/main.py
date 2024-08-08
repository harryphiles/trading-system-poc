import random
import time
from src.order_components import OrderSide
from src.order_queue import OrderQueue
from src.order_processor import OrderProcessor
from src.match_engine import MatchEngine
from src.logger import Logger, LOGGING_CONFIG


def create_random_order() -> tuple[str, OrderSide, float, int]:
    side = random.choice([OrderSide.BUY, OrderSide.SELL])
    price = round(random.uniform(90, 110), 2)
    quantity = random.randint(1, 20)
    user_id = f"user{random.randint(1, 100)}"
    return user_id, side, price, quantity


def simulate_trading(op: OrderProcessor, oq: OrderQueue, duration: int):
    end_time = time.time() + duration
    while time.time() < end_time:
        # Simulate order creation
        if random.random() < 0.7:
            op.receive_order(*create_random_order())

        # Process a single order
        op.process_single_order()

        # Simulate time passing
        time.sleep(random.uniform(0.1, 2.0))

    # Log final statistics
    op.logger.info("Simulation completed. Final orderbook state:")
    op.logger.info(f"Total orders processed: {len(op.order_queue.order_map)}")
    op.logger.info(f"Transactions: {op.transactions}")
    op.logger.info(f"Pending orders: {len(op.order_queue.queue)}")

    # Log remaining buy orders
    op.logger.info("Remaining buy orders:")
    for orders in sorted(oq.buy_orders.values()):
        for order in orders:
            op.logger.info(f"{order.__dict__}")

    # Log remaining sell orders
    op.logger.info("Remaining sell orders:")
    for orders in sorted(oq.sell_orders.values()):
        for order in orders:
            op.logger.info(f"{order.__dict__}")

    op.logger.info(f"{oq.queue = }")
    op.logger.info("Filled orders:")
    for order in oq.filled_orders:
        op.logger.info(f"{order.__dict__}")
    op.logger.info("Order maps")
    for order_num, order in oq.order_map.items():
        op.logger.info(f"{order_num}: {order.__dict__}")


def run_matches_from_given_orders(op: OrderProcessor, orders: int):
    # Add orders
    print("Run orders started..")
    t0 = time.time()
    for _ in range(orders):
        op.receive_order(*create_random_order())
    t1 = time.time()
    print(f"Adding {orders} orders took {t1 - t0}")

    op.process_orders()
    t2 = time.time()
    print(f"Matching {orders} orders took {t2 - t1}")


def main():
    logger = Logger(__name__, LOGGING_CONFIG, "test.log").logger

    oq = OrderQueue(logger=logger)
    me = MatchEngine(logger=logger)
    op = OrderProcessor(oq, me, logger=logger)

    # Simulate trading for n seconds
    simulate_trading(op, oq, duration=10)
    # run_matches_from_given_orders(op, 10)
    # run_matches_from_given_orders(op, 100)
    # run_matches_from_given_orders(op, 1_000)
    # run_matches_from_given_orders(op, 10_000)


if __name__ == "__main__":
    main()
