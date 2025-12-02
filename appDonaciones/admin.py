from django.contrib import admin
# Asegúrate de que TipoDeAlimento YA NO esté en esta lista:
from .models import Donaciones, Donante, BajoRecursos, Zoo

# Registra solo los modelos que existen
admin.site.register(Donaciones)
admin.site.register(Donante)
admin.site.register(BajoRecursos)
admin.site.register(Zoo)