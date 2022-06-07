from re import L
from django.db import models

# Create your models here.

class Blocks(models.Model):
    index = models.PositiveBigIntegerField(blank=False, null=False)
    transaction = models.JSONField(blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    previous_hash = models.CharField(blank=False, null=False, max_length=64)
    nonce = models.PositiveIntegerField(blank=False, null=False)
    hash = models.CharField(blank=False, null=False, max_length=64)
    
class PendingTransactions(models.Model):
    transaction = models.JSONField(blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
