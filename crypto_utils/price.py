import time
import typing
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

import eth_typing
import gql
from gql.transport import requests as requests_transport

from crypto_utils import enums, exceptions, http_utils


class TransactionValueUsdProvider(ABC):
    @abstractmethod
    def get_usd_value_of_transaction(
        self,
        transaction_hash: eth_typing.ChecksumAddress,
        blockchain: enums.Blockchain = enums.Blockchain.ETHEREUM,
    ) -> float:
        pass


class PriceProvider(ABC):
    @abstractmethod
    def get_price_of_contract_in_usd(
        self,
        contract_address: eth_typing.ChecksumAddress,
        at_time: int,
        blockchain: enums.Blockchain = enums.Blockchain.ETHEREUM,
    ) -> float | None:
        pass


class UniswapV3PriceProvider(TransactionValueUsdProvider):
    UNISWAP_SUBGRAPH_URL = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3"
    QUERY = gql.gql(
        """
        query priceQuery($transaction_hash: String){

                      swaps(where: {transaction: $transaction_hash}){
                        amountUSD
                        transaction{
                          id
                        }
                      }
        }

        """
    )

    def __init__(self) -> None:
        self._transport = requests_transport.RequestsHTTPTransport(
            url=self.UNISWAP_SUBGRAPH_URL
        )
        self._client = gql.Client(
            transport=self._transport, fetch_schema_from_transport=True
        )

    def _get_price_from_subgraph(
        self, request_variables: dict[str, typing.Any]
    ) -> float:
        json_result = self._client.execute(
            self.QUERY, variable_values=request_variables
        )
        if "swaps" not in json_result:
            raise exceptions.MissingDataError()
        swaps = json_result["swaps"]
        only_swap = swaps[0]
        price = float(only_swap["amountUSD"])
        return price

    def get_usd_value_of_transaction(
        self,
        transaction_hash: eth_typing.ChecksumAddress,
        blockchain: enums.Blockchain = enums.Blockchain.ETHEREUM,
    ) -> float:
        request_variables = {"transaction_hash": transaction_hash}
        try:
            return self._get_price_from_subgraph(request_variables)
        except Exception as exception:
            raise exceptions.CantExtractUsdValueError(str(exception))


class CoingeckoPriceProvider(PriceProvider):
    COINGECKO_URL = "https://api.coingecko.com/api/v3"

    def _request_price_json(self, contract_address, url) -> typing.Any:
        while True:
            try:
                return http_utils.request(url)
            except exceptions.RequestError as request_error:
                if request_error.status_code == 429:
                    time.sleep(3)
                    continue
                raise exceptions.CantFindTokenPriceError(
                    f"Can't find price for token address {contract_address}, req_code {request_error.status_code}"
                )

    def _get_blockchain_id(self, blockchain: enums.Blockchain) -> str:
        match blockchain:
            case blockchain.ETHEREUM:
                return "ethereum"

    def get_price_of_contract_in_usd(
        self,
        contract_address: eth_typing.ChecksumAddress,
        at_time: int,
        blockchain: enums.Blockchain = enums.Blockchain.ETHEREUM,
    ) -> float | None:
        blockchain_id = self._get_blockchain_id(blockchain)
        at_time_datetime = datetime.fromtimestamp(at_time)
        start_datetime = at_time_datetime - timedelta(days=1)
        start_timestamp = int(start_datetime.timestamp())
        url = (
            f"{self.COINGECKO_URL}/coins/{blockchain_id}/contract/{contract_address}/market_chart/range?vs_currency=usd"
            f"&from={start_timestamp}&to={int(at_time)}"
        )
        price_response_json = self._request_price_json(contract_address, url)
        prices = price_response_json["prices"]
        if not prices:
            raise exceptions.MissingDataError()
        last_price_array = prices[-1]
        price_time = last_price_array[0] / 1000.0  # ts is in ms
        time_diff = datetime.fromtimestamp(price_time) - datetime.fromtimestamp(at_time)
        if time_diff > timedelta(hours=1):
            print(f"Coingecko price time delta is {time_diff}")
        return last_price_array[1]  # price at 1st index
