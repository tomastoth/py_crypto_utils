class RequestError(Exception):
    def __init__(self, status_code: int):
        self.status_code = status_code


class MissingDataError(Exception):
    pass


class CantFindTokenPriceError(Exception):
    pass


class CantExtractUsdValueError(Exception):
    pass

class UnknownSymbolError(Exception):
    pass
