from typing import Dict
from typing import List
import dataclasses
import tinvest


@dataclasses.dataclass
class PortfolioPosition:
    common_info: tinvest.PortfolioPosition
    operations: List[tinvest.Operation]


class Portfolio:
    positions: Dict[str, PortfolioPosition] = {}  # ключ - figi
