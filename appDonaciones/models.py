from django.db import models
from django.db.models import Sum

# NOTA: He eliminado los modelos 'Auth...' y 'Django...' porque Django ya los maneja internamente.
# Solo dejamos tus modelos personalizados para evitar conflictos.

class BajoRecursos(models.Model):
    id_bajo = models.AutoField(primary_key=True)
    ciudad = models.CharField(max_length=50)
    donacion = models.CharField(max_length=50)

    class Meta:
        managed = True  # <--- CAMBIO IMPORTANTE: True para que se cree en Render
        db_table = 'bajo_recursos'
    
    def __str__(self):
        return self.ciudad

class Donaciones(models.Model):
    id_donacion = models.AutoField(primary_key=True)
    donante = models.CharField(db_column='Donante', max_length=255)
    cantidad = models.IntegerField()
    fecha_llegada = models.DateField()
    tipo_alimento = models.CharField(max_length=50)
    destino = models.CharField(max_length=50)

    class Meta:
        managed = True  # <--- CAMBIO IMPORTANTE
        db_table = 'donaciones'

    def __str__(self):
        return f"Donación #{self.id_donacion} de {self.donante}"

class Donante(models.Model):
    TIPO_DONANTE_CHOICES = [
        ('individual', 'Individual'),
        ('empresa', 'Empresa'),
        ('organizacion', 'Organización'),
        ('institucion', 'Institución'),
    ]
    
    ESTADO_DONANTE_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('suspendido', 'Suspendido'),
    ]

    id_donante = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, blank=True, null=True)
    
    tipo_donante = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        choices=TIPO_DONANTE_CHOICES
    )
    
    ciudad = models.CharField(max_length=255)
    direccion = models.TextField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    fecha_registro = models.DateField(blank=True, null=True)
    
    estado = models.CharField(
        max_length=10, 
        blank=True, 
        null=True,
        choices=ESTADO_DONANTE_CHOICES
    )
    notas = models.TextField(blank=True, null=True)
    
    # Campos para el mapa (opcionales por si los agregaste antes)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        managed = True  # <--- CAMBIO IMPORTANTE
        db_table = 'donante'

    def __str__(self):
        return self.nombre or self.ciudad

    def total_donaciones(self):
        return Donaciones.objects.filter(donante=self.ciudad).count()

    def cantidad_total_donada(self):
        total = Donaciones.objects.filter(donante=self.ciudad).aggregate(Sum('cantidad'))
        return total['cantidad__sum'] or 0

class Zoo(models.Model):
    id_zoo = models.AutoField(primary_key=True)
    animales = models.CharField(max_length=255)
    trabajadores = models.CharField(max_length=255)
    tipo_animal = models.CharField(max_length=50)
    donacion = models.CharField(max_length=50)

    class Meta:
        managed = True  # <--- CAMBIO IMPORTANTE
        db_table = 'zoo'
        
    def __str__(self):
        return f"Zoo: {self.animales}"