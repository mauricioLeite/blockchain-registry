from django.db import models

class PeersORM(models.Model):
    ip_address = models.CharField(blank=False, null=False, max_length=30)

    class Meta:
        managed=False
        db_table='blockchain_peers'