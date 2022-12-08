import enums


def get_blockchain_token_symbol(blockchain: enums.Blockchain) -> str:
    match blockchain:
        case enums.Blockchain.ETHEREUM:
            return "ETH"
