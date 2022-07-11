from django.db import models

class PendingTransactionsORM(models.Model):
    transaction = models.JSONField(blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed=False
        db_table='blockchain_pendingtransactions'
 