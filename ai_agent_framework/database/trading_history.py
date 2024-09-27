class TradingHistoryDB:
    def __init__(self):
        self.trades = []
    
    def add_trade(self, trade):
        self.trades.append(trade)
    
    def get_recent_trades(self, n=10):
        return self.trades[-n:]
