from TradingBot import TradingBot
from django.db.models import Q
from .models import Trade, Order
from pybit.unified_trading import HTTP
from typing import Dict, Optional
import os
import time
from dotenv import load_dotenv

load_dotenv()

class Tit4TatTradingBot(TradingBot):
    def __init__(self):
        self.initialize_client()
    
    def initialize_client(self):
        api_key = os.getenv("BYBIT_DEMO_API_KEY")
        api_secret = os.getenv("BYBIT_DEMO_SECRET")
        
        if not api_key or not api_secret:
            raise ValueError("API credentials not found in environment variables")
            
        self.client = HTTP(
            demo=True,
            api_key=api_key,
            api_secret=api_secret,
            log_requests=True
        )
    
    def get_account_balance(self):
        """Get current account balance in USDT"""
        balance = self.client.get_wallet_balance(accountType="UNIFIED", coin="USDT")
        return float(balance['result']['list'][0]['totalEquity'])

    def set_leverage(self, symbol: str, leverage: int) -> bool:
        # to do : error handling and correct return
        self.client.set_leverate(
            category="linear",
            symbol=symbol,
            buyLeverage=str(leverage),
            sellLeverage=str(leverage)
            )
        return True
    
    def analyze_market(self, symbol: str) -> Dict:
        """
        Analyze based on last trade
        Args:
            symbol (str): target currency

        Returns:
            dict:{
                symbol: str
                action: str ("buy" or "sell")
            }
        """
        last_trade =  Trade.get_last_trade()
        
        if not last_trade:
            return {
                'symbol': symbol,
                'action': 'Buy'  # default
            }
        if last_trade['status'] == 'profit':
            return {
                'symbol': symbol,
                'action': last_trade['side']  # Continue with same strategy
            }
        else:
            opposite_side = "Sell" if last_trade['side'] == "Buy" else "Buy"
            return {
                'symbol': symbol,
                'action': opposite_side
            }
    
def execute_trade(self, symbol: str, side: str, quantity: float) -> Dict:
        """
        Execute a trade with the specified parameters
        
        Args:
            action (str): 'long' or 'short'
            quantity (float): Amount to trade
            leverage (float): Leverage to use
        
        Returns:
            dict: {
                    trade_id: int
                    pnl: float 
                    status: str ('profit' or 'loss')
                    }
        """
        try:
            opening_balance = self.get_account_balance()
            ticker = self.client.get_tickers(
                category="linear",
                symbol=symbol
            )
            current_price = float(ticker['result']['list'][0]['lastPrice'])

            

            sl_percentage = 1
            sl_price = current_price * (1 + sl_percentage/100) if side == "short" else current_price * (1 - sl_percentage/100) 

            opening_side = "Buy" if side == "long" else "Sell"
            self.client.place_order(
                category="linear",
                symbol=symbol,
                side=opening_side,
                orderType="Market",
                qty=quantity,
                stopLoss=str(sl_price),
                positionIdx=0
            )
            time.sleep(5)
            position = self.get_last_position(symbol)
            if position:
                opening_order = Order.objects.create(
                    symbol=position['symbol'],
                    side=position['side'],
                    entry_price=position['avgPrice'],
                    quantity=position['size'],
                    leverage=position['leverage']
                )
            else: 
                # to do : error handling here
                pass
            
            time.sleep(3000) # wait for 5 minutes

            if(self.get_last_position(symbol) is None):
                # make better logic, add logger
                return -1 if opening_side == "long" else 1
            else:
                close_side = "Sell" if opening_side == "long" else "Buy"
                self.client.place_order(
                    category="linear",
                    symbol=symbol,
                    side=close_side,
                    orderType="Market",
                    qty=quantity,
                    positionIdx=0,
                    reduceOnly=True
                )
                
                time.sleep(5)
                position = self.get_last_position(symbol)
                if position:
                    closing_order = Order.objects.create(
                        symbol=position['symbol'],
                        side=position['side'],
                        entry_price=position['avgPrice'],
                        quantity=position['size'],
                        leverage=position['leverage']
                    )
                else:
                    # error handling here
                    pass

            closing_balance = self.get_account_balance()

            pnl = closing_balance - opening_balance

            trade = Trade.objects.create(
                 symbol=symbol,
                side=side,
                opening_order=opening_order,
                closing_order=closing_order,
                currency_price_change=opening_order['entry_price'] - closing_order['entry_price'],
                quantity=quantity,
                leverage=position['leverage'] if position['leverage'] else 1,
                pnl=pnl,
                status='profit' if pnl > 0 else 'loss'
            )
            return trade
            
        except Exception as e:
            return None