from django.contrib import admin
from.models import *
# Base model for automatic timest
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Worker)
# admin.site.register(User)