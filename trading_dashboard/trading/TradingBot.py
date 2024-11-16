from abc import ABC, abstractmethod
from typing import Dict

class TradingBot(ABC):
    @abstractmethod
    def get_account_balance(self, symbol: str) -> Dict:
        pass
    
    @abstractmethod
    def set_leverage(self, symbol: str, leverage: int) -> bool:
        pass
    
    @abstractmethod
    def execute_trade(self, symbol: str, side: str, quantity: float) -> Dict:
        pass
    
    @abstractmethod
    def analyze_market(self, symbol: str) -> Dict:
        pass
    
