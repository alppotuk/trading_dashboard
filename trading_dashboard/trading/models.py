from django.db import models

class Order(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    symbol = models.CharField(max_length=20)
    side = models.CharField(max_length=10)  # Buy or Sell
    entry_price = models.DecimalField(max_digits=20, decimal_places=8)
    quantity = models.DecimalField(max_digits=20, decimal_places=8)
    leverage = models.IntegerField(default=1)
    
    class Meta:
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['symbol']),
        ]

class Trade(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    symbol = models.CharField(max_length=20)
    side = models.CharField(max_length=10)  # long or short
    opening_order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='opening_trades')
    closing_order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='closing_trades')
    currency_price_change = models.DecimalField(max_digits=20, decimal_places=8)
    quantity = models.DecimalField(max_digits=20, decimal_places=8)
    leverage = models.IntegerField(default=1)
    pnl = models.DecimalField(max_digits=20, decimal_places=8)
    status = models.CharField(max_length=20)  # profit or loss
    
    class Meta:
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['status']),
        ]
        
    @classmethod
    def get_last_trade(cls):
        return cls.objects.order_by('-timestamp').first()