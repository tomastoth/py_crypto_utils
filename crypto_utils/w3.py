import os
import typing

import eth_typing
from web3 import HTTPProvider, Web3

from crypto_utils import schema
from crypto_utils.config import config

w3_client = Web3(HTTPProvider(config.W3_PROVIDER))


def _load_abi(abi_file_name: str) -> str:
    with open(os.path.join(config.ROOT_DIR, "abis", abi_file_name), "r") as pool_file:
        return [line for line in pool_file][0]


def _load_erc20_abi() -> str:
    return _load_abi("erc20.txt")


def get_erc20_info(address: eth_typing.ChecksumAddress) -> schema.ERC20:
    erc20_abi = _load_erc20_abi()
    erc20_contract = w3_client.eth.contract(address=address, abi=erc20_abi)
    symbol = erc20_contract.functions.symbol().call()
    decimals = erc20_contract.functions.decimals().call()
    return schema.ERC20(symbol=symbol, decimals=decimals, address=address)


def _load_pool_abi() -> str:
    return _load_abi("uni_v3_pool.txt")


def get_uni3_pool_token_addresses(
    pool_address: eth_typing.ChecksumAddress,
) -> typing.Union[eth_typing.ChecksumAddress, eth_typing.ChecksumAddress]:
    pool_abi_text = _load_pool_abi()
    pool_contract = w3_client.eth.contract(address=pool_address, abi=pool_abi_text)
    token0 = pool_contract.functions.token0().call()
    token1 = pool_contract.functions.token1().call()
    return token0, token1


if __name__ == "__main__":
    print(
        get_erc20_info(
            Web3.toChecksumAddress("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
        )
    )
