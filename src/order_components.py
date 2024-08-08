from enum import Enum
from datetime import datetime, timezone


class OrderSide(Enum):
    BUY = 1
    SELL = 2


class OrderStatus(Enum):
    CANCELLED = 0
    PENDING = 1
    PROCESSING = 2
    PARTIALLY_FILLED = 3
    FILLED = 4


class OrderIdGenerator:
    def __init__(self) -> None:
        self.reset()

    def generate_id(self) -> str:
        order_id = f"{self._next_id:08d}"
        self._next_id += 1
        return order_id

    def reset(self):
        self._next_id = 1


class Order:
    id_generator = OrderIdGenerator()

    def __init__(
        self, user_id: str, side: OrderSide, price: float, quantity: int
    ) -> None:
        self.order_id = self.id_generator.generate_id()
        self.user_id = user_id
        self.side = side
        self.price = price
        self.quantity = quantity
        self.status = OrderStatus.PENDING
        self.timestamp = datetime.now(tz=timezone.utc)

    @classmethod
    def reset_id_generator(cls) -> None:
        cls.id_generator.reset()
