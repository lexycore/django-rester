from django.contrib import admin

from .models import (
    Org,
    Employee,
)

# Register new models
admin.site.register(Org)
admin.site.register(Employee)
