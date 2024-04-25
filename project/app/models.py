from django.db import models

# Create your models here.



class SendEmail(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    price = models.BigIntegerField()
    mobile_number = models.BigIntegerField()
