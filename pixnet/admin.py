from pixnet.models import Consumer
from django.contrib import admin

class PIXNETAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,           {'fields': ['version']}),
        ('Consumer key', {'fields': ['key']}),
        ('Consumer secret', {'fields': ['secret']}),
    ]
    list_display = ('version', 'key', 'secret')
    ordering = [ 'version' ]

admin.site.register(Consumer, PIXNETAdmin)

