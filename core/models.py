from django.db import models


class City(models.Model):
    iata_code = models.CharField(max_length=3)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
