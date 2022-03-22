import json
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django_jalali.db import models as jmodel
from django.core.files import File

class Stand (models.Model):
    name = models.CharField(max_length=50)
    sizes = models.TextField()

    def __str__(self):
        return self.name

class Order (models.Model):
    
    objects = jmodel.jManager()
    name = models.CharField(max_length=50)
    price = models.BigIntegerField()
    fee = models.BigIntegerField()
    date = jmodel.jDateField()
    done = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)
    finishdate = jmodel.jDateField(null=True)
    workers = models.ManyToManyField(User)
    daynumber = models.IntegerField(null=True)
    des = models.TextField(null=True)
    perworker = models.TextField(null=True)
    
    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        f = open("data.json","w+")
        jsondata = File(f)
        perWorker = json.loads(jsondata)['perWorker']
        self.fee = int(self.price / 100000 * perWorker ) * 1000
        self.date = datetime.date(datetime.now())
        jsondata.close()

        return super(Order, self).save(*args, **kwargs)