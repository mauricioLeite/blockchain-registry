from django.db import models

class PendingTransactionsORM(models.Model):
    transcation = models.JSONField(blank=False, null=False)

    class Meta:
        managed=False
        db_table='blockchain_pendingtransactions'
 