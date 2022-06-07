from django.db import models

# Create your models here.

class Blocks(models.Model):
    block = models.JSONField(blank=False, null=False)

class PendingTransactions(models.Model):
    transcation = models.JSONField(blank=False, null=False)
