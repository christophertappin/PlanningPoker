from django.db import models


class Vote(models.Model):
    session_id = models.CharField(max_length=100)
    client = models.CharField(max_length=100)
    value = models.DecimalField(decimal_places=1, max_digits=3)
