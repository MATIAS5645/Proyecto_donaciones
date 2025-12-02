from django.contrib import admin
from .models import TipoDeAlimento

# Esto hace que el modelo aparezca en el panel de admin
admin.site.register(TipoDeAlimento)