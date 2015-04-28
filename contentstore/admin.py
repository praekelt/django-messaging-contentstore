from django.contrib import admin

from .models import Schedule, MessageSet, Message

admin.site.register(Schedule)
admin.site.register(MessageSet)
admin.site.register(Message)
