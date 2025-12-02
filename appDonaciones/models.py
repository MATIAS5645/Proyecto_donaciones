# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.db.models import Sum # Importar Sum para las estadísticas





class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class BajoRecursos(models.Model):
    id_bajo = models.AutoField(primary_key=True)
    ciudad = models.CharField(max_length=50)
    donacion = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'bajo_recursos'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Donaciones(models.Model):
    id_donacion = models.AutoField(primary_key=True)
    donante = models.CharField(db_column='Donante', max_length=255)  # Field name made lowercase.
    cantidad = models.IntegerField()
    fecha_llegada = models.DateField()
    tipo_alimento = models.CharField(max_length=50)
    destino = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'donaciones'


class Donante(models.Model):
    id_donante = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, blank=True, null=True)
    tipo_donante = models.CharField(max_length=12, blank=True, null=True)
    ciudad = models.CharField(max_length=255)
    direccion = models.TextField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    fecha_registro = models.DateField(blank=True, null=True)
    estado = models.CharField(max_length=10, blank=True, null=True)
    notas = models.TextField(blank=True, null=True)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'donante'


class TipoDeAlimento(models.Model):
    id_tipo = models.AutoField(primary_key=True, db_comment='Identificador único autoincremental del tipo de alimento')
    perecible = models.CharField(max_length=50, db_comment='Indica si el alimento es perecible (1=Sí, 0=No)')
    no_perecibles = models.CharField(max_length=50, db_comment='Indica si el alimento es no perecible (1=Sí, 0=No)')
    estado = models.CharField(max_length=50, db_comment='Estado del alimento (1=Bueno, 2=Regular, 3=Malo)')
    fecha_caducidad = models.DateField(db_comment='Fecha de caducidad representada como entero')

    class Meta:
        managed = False
        db_table = 'tipo_de_alimento'
        db_table_comment = 'Tabla para almacenar tipos de alimentos con información sobre perecibilidad y estado'


class Zoo(models.Model):
    id_zoo = models.AutoField(primary_key=True)
    animales = models.CharField(max_length=255)
    trabajadores = models.CharField(max_length=255)
    tipo_animal = models.CharField(max_length=50)
    donacion = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'zoo'