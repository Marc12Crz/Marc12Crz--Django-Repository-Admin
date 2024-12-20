# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Adopciones(models.Model):
    id_adopcion = models.BigAutoField(primary_key=True)
    condiciones_hogar = models.TextField(blank=True, null=True)
    estado_solicitud = models.CharField(max_length=9)
    experiencia_con_perros = models.TextField(blank=True, null=True)  # This field type is a guess.
    fecha_solicitud = models.DateField(blank=True, null=True)
    motivo_adopcion = models.TextField(blank=True, null=True)
    otros_animales = models.TextField(blank=True, null=True)  # This field type is a guess.
    responsable_financiero = models.TextField(blank=True, null=True)  # This field type is a guess.
    id_perro = models.ForeignKey('Mascotas', models.DO_NOTHING, db_column='id_perro')
    id_usuario = models.ForeignKey('Usuarios', models.DO_NOTHING, db_column='id_usuario')
    razon = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'adopciones'


class Albergues(models.Model):
    id_albergue = models.BigAutoField(primary_key=True)
    correo = models.CharField(max_length=255, blank=True, null=True)
    departamento = models.CharField(max_length=255, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    distrito = models.CharField(max_length=255, blank=True, null=True)
    nombre = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=255, blank=True, null=True)
    id_usuario = models.ForeignKey('Usuarios', models.DO_NOTHING, db_column='id_usuario')
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    imagen = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'albergues'


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


class Chat(models.Model):
    id_mensaje = models.AutoField(primary_key=True)
    emisor = models.CharField(max_length=8, blank=True, null=True)
    fecha_envio = models.DateTimeField()
    mensaje = models.TextField(blank=True, null=True)
    id_albergue = models.ForeignKey(Albergues, models.DO_NOTHING, db_column='id_albergue')
    id_usuario = models.ForeignKey('Usuarios', models.DO_NOTHING, db_column='id_usuario')

    class Meta:
        managed = False
        db_table = 'chat'


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
    cantidad = models.IntegerField(blank=True, null=True)
    fecha_donacion = models.DateTimeField(blank=True, null=True)
    monto_total = models.FloatField(blank=True, null=True)
    id_albergue = models.ForeignKey(Albergues, models.DO_NOTHING, db_column='id_albergue')
    id_producto = models.ForeignKey('Productos', models.DO_NOTHING, db_column='id_producto')
    id_usuario = models.ForeignKey('Usuarios', models.DO_NOTHING, db_column='id_usuario')

    class Meta:
        managed = False
        db_table = 'donaciones'


class Empresas(models.Model):
    id_empresa = models.AutoField(primary_key=True)
    correo = models.CharField(max_length=255, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    nombre = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=255, blank=True, null=True)
    tipo_producto = models.CharField(max_length=7, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'empresas'


class Imagenes(models.Model):
    id_imagen = models.AutoField(primary_key=True)
    descripcion = models.TextField(blank=True, null=True)
    url = models.CharField(max_length=255)
    id_perro = models.ForeignKey('Mascotas', models.DO_NOTHING, db_column='id_perro')

    class Meta:
        managed = False
        db_table = 'imagenes'


class Mascotas(models.Model):
    id_perro = models.AutoField(primary_key=True)
    descripcion = models.TextField(blank=True, null=True)
    edad = models.IntegerField()
    esterilizado = models.TextField()  # This field type is a guess.
    imagen = models.CharField(max_length=255, blank=True, null=True)
    nombre = models.CharField(max_length=255)
    raza = models.CharField(max_length=255)
    sexo = models.CharField(max_length=6)
    tama±o = models.CharField(max_length=7)
    vacunas_completas = models.TextField()  # This field type is a guess.
    id_albergue = models.ForeignKey(Albergues, models.DO_NOTHING, db_column='id_albergue')
    tamano = models.CharField(max_length=7)

    class Meta:
        managed = False
        db_table = 'mascotas'


class PreguntasFormulario(models.Model):
    id_pregunta = models.AutoField(primary_key=True)
    pregunta = models.CharField(max_length=255, blank=True, null=True)
    id_albergue = models.ForeignKey(Albergues, models.DO_NOTHING, db_column='id_albergue')

    class Meta:
        managed = False
        db_table = 'preguntas_formulario'


class Productos(models.Model):
    id_producto = models.AutoField(primary_key=True)
    descripcion_producto = models.CharField(max_length=255, blank=True, null=True)
    nombre_producto = models.CharField(max_length=100, blank=True, null=True)
    precio = models.FloatField(blank=True, null=True)
    id_empresa = models.ForeignKey(Empresas, models.DO_NOTHING, db_column='id_empresa')
    imagen = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'productos'


class RespuestasFormulario(models.Model):
    id_respuesta = models.AutoField(primary_key=True)
    respuesta = models.TextField(blank=True, null=True)
    id_adopcion = models.ForeignKey(Adopciones, models.DO_NOTHING, db_column='id_adopcion')
    id_pregunta = models.ForeignKey(PreguntasFormulario, models.DO_NOTHING, db_column='id_pregunta')

    class Meta:
        managed = False
        db_table = 'respuestas_formulario'


class Transacciones(models.Model):
    id_transaccion = models.AutoField(primary_key=True)
    estado_transaccion = models.CharField(max_length=10, blank=True, null=True)
    fecha_entrega = models.DateField(blank=True, null=True)
    id_donacion = models.ForeignKey(Donaciones, models.DO_NOTHING, db_column='id_donacion')
    id_empresa = models.ForeignKey(Empresas, models.DO_NOTHING, db_column='id_empresa')

    class Meta:
        managed = False
        db_table = 'transacciones'


class Usuarios(models.Model):
    id = models.BigAutoField(primary_key=True)
    contrase±a = models.CharField(max_length=255, blank=True, null=True)
    correo = models.CharField(max_length=255, blank=True, null=True)
    departamento = models.CharField(max_length=255, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    distrito = models.CharField(max_length=255, blank=True, null=True)
    nombre = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=255, blank=True, null=True)
    tipo_usuario = models.CharField(max_length=255, blank=True, null=True)
    imagen = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'usuarios'
