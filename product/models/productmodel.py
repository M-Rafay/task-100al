from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    type = models.CharField(max_length=20)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name