# Trading System as Proof of Concept
A proof-of-concept trading system that primarily focuses on order matching.

This project simulates a trading environment where orders are created, processed, and matched in a simple order book. It is intended to explore ideas about the design of order processing in a trading system.

## Design


    +--------------------+       +------------------------+       +------------------+
    |  OrderProcessor    | <-->  |       OrderQueue       | <-->  |   MatchEngine    |
    |--------------------|       |------------------------|       |------------------|
    | - Receive Order    |       | - Queue Order          |       | - Match Orders   |
    | - Process Order    |       | - Maintain Order Book  |       | - Execute Trades |
    | - Log Transactions |       | - Cancel Order         |       | - Update Status  |
    +--------------------+       +------------------------+       +------------------+


## Components
### OrderProcessor
The `OrderProcessor` class handles the reception and processing of orders. It interacts with the `OrderQueue` to process orders and updates the match engine for transaction processing.

### OrderQueue
The `OrderQueue` class manages the queue of orders to be processed. It handles adding orders to the queue, updating order books, and managing order cancellations.

### MatchEngine
The `MatchEngine` class is responsible for matching buy and sell orders and executing trades. A trade occurs when the highest bid on the buy side is equal to or greater than the lowest ask on the sell side.

## Features

- Simulate the creation of random buy and sell orders.
- Process and match orders in a simplified order book.
- Log the state of orders and transactions throughout the simulation.
- Track the status of orders, including pending, processing, canceled, partially filled and fully filled.
