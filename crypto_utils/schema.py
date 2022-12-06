from dataclasses import dataclass
from datetime import datetime

import eth_typing


@dataclass
class DecodedLog:
    name: str
    signature: str
    params: list[dict[str, any]]


@dataclass
class LogEvent:
    decoded_logs: list[DecodedLog]


@dataclass
class Transaction:
    from_address: str
    to_address: str
    block_number: int
    block_time: str
    hash: str


@dataclass
class Trade:
    time: datetime
    trader: eth_typing.ChecksumAddress
    bought_token: eth_typing.ChecksumAddress
    sold_token: eth_typing.ChecksumAddress
    bought_amount: float
    sold_amount: float
    usd_value: float


@dataclass
class ERC20:
    symbol: str
    decimals: int
    address: eth_typing.ChecksumAddress
