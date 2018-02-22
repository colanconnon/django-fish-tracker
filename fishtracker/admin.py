from django.contrib import admin

# Register your models here.
from .models import FishCatch, Lake, FriendsFishCatches
# Register your models here.

admin.site.register(FishCatch)
admin.site.register(Lake)
admin.site.register(FriendsFishCatches)
