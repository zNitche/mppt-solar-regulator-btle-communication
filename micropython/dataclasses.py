class RequestItem:
    def __init__(self,
                 dec_address: str,
                 description: str,
                 multiplier: int,
                 unit: str,
                 skip: bool = False):
        self.dec_address = dec_address
        self.description = description
        self.multiplier = multiplier
        self.unit = unit
        self.skip = skip


class ResponseItem:
    def __init__(self,
                 description: str,
                 value: float,
                 unit: str):
        self.description = description
        self.value = value
        self.unit = unit
