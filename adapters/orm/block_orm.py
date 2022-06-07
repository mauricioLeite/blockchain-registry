from django.db import models

class BlocksORM(models.Model):
    block = models.JSONField(blank=False, null=False)

    class Meta:
        managed=False
        db_table='blockchain_blocks'