from django.contrib import admin
from .models import *


class AdoptionRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'cat', 'status']
    list_filter = ['status']
    search_fields = ['user__username', 'cat__name']

admin.site.register(Cat)
admin.site.register(AdoptionRequest, AdoptionRequestAdmin)
