from django.db import models
from django.utils.translation import ugettext as _


# Create your models here.

class Org(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)

    class Meta:
        verbose_name_plural = _('Organizations')
        verbose_name = _('Organization')


class Employee(models.Model):
    date = models.DateField(auto_now_add=True)
    org = models.ForeignKey(Org, related_name='employees')
    firstname = models.CharField(max_length=50, blank=False, null=False)
    lastname = models.CharField(max_length=50, blank=False, null=False)

    class Meta:
        verbose_name_plural = _('Employees')
        verbose_name = _('Employee')
