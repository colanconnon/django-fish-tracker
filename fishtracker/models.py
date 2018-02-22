import sys
import uuid

from django.conf import settings
from django.contrib.auth.models import User
from django.db import connection, models
from django.db.models.signals import post_save, pre_migrate
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
import logging
from typing import Dict


logger = logging.getLogger('django')


class FishCatch(models.Model):
    description = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lake = models.ForeignKey(
        'Lake', related_name='fish_catches', on_delete=models.CASCADE)


class Lake(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class FriendsFishCatches(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fish_catch = models.ForeignKey(FishCatch, related_name='friends_fish_catches', on_delete=models.CASCADE)



@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
