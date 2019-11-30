from __future__ import unicode_literals

from django.db import models

class Paciente (models.Model):
#    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30)
    id_name=models.CharField(max_length=40)
    gender=models.CharField(max_length=30,default='empty')
    birthday= models.DateField()
    smoker=models.BooleanField()
    year_diag=models.IntegerField(default='1')
    other_disorder=models.CharField(max_length=250, default='empty')
    educational_level=models.IntegerField(default='0')
#    weight=models.CharField(max_digits=3, decimal_places=2)
    weight=models.CharField(max_length=50)
    height=models.IntegerField(default='0')
    session_count=models.IntegerField(default='0')
    def __str__(self):
        return self.session_count
    def __str__(self):
        return self.id_name

# Create your models here.

class Medicine (models.Model):

    medicinename=models.CharField(max_length=40)
    dose=models.IntegerField(default='2')
    intaketime=models.IntegerField(default='0')
    id_name=models.CharField(max_length=40)


class Results (models.Model):

    id_name=models.CharField(max_length=40,default='0')
    WER=models.CharField(max_length=40)
