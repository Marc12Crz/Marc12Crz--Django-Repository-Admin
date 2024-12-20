# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

from cloudinary.models import CloudinaryField
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
        
        db_table = 'adopciones'


class Albergues(models.Model):
    id_albergue = models.BigAutoField(primary_key=True)
    correo = models.CharField(max_length=255, blank=True, null=True)
    departamento = models.CharField(max_length=255, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    distrito = models.CharField(max_length=255, blank=True, null=True)
    nombre = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=255, blank=True, null=True)
    id_usuario = models.ForeignKey('Usuarios', on_delete=models.CASCADE, db_column='id_usuario')
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    imagen = models.URLField(blank=True, null=True)

    class Meta:
        db_table = 'albergues'









class Donaciones(models.Model):
    id_donacion = models.AutoField(primary_key=True)
    cantidad = models.IntegerField(blank=True, null=True)
    fecha_donacion = models.DateTimeField(blank=True, null=True)
    monto_total = models.FloatField(blank=True, null=True)
    id_albergue = models.ForeignKey(Albergues, models.DO_NOTHING, db_column='id_albergue')
    id_producto = models.ForeignKey('Productos', models.DO_NOTHING, db_column='id_producto')
    id_usuario = models.ForeignKey('Usuarios', models.DO_NOTHING, db_column='id_usuario')

    class Meta:
        
        db_table = 'donaciones'


class Empresas(models.Model):
    id_empresa = models.AutoField(primary_key=True)
    correo = models.CharField(max_length=255, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    nombre = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=255, blank=True, null=True)
    tipo_producto = models.CharField(max_length=7, blank=True, null=True)

    class Meta:
        
        db_table = 'empresas'


class Mascotas(models.Model):
    id_perro = models.AutoField(primary_key=True)
    descripcion = models.TextField(blank=True, null=True)
    edad = models.IntegerField()
    esterilizado = models.BooleanField(default=False)
    nombre = models.CharField(max_length=255)
    raza = models.CharField(max_length=255)
    sexo = models.CharField(max_length=6, choices=[('macho', 'Macho'), ('hembra', 'Hembra')])
    tamano = models.CharField(max_length=7, choices=[('pequeño', 'Pequeño'), ('mediano', 'Mediano'), ('grande', 'Grande')])
    vacunas_completas = models.BooleanField(default=False)
    id_albergue = models.ForeignKey('Albergues', on_delete=models.CASCADE, db_column='id_albergue')

    class Meta:
        db_table = 'mascotas'



class Imagenes(models.Model):
    id_imagen = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=255, blank=True, null=True)
    url = models.CharField(max_length=255)
    id_perro = models.ForeignKey(Mascotas, on_delete=models.CASCADE, related_name='imagenes_relacion', db_column='id_perro')

    class Meta:
        db_table = 'imagenes'




class PreguntasFormulario(models.Model):
    id_pregunta = models.AutoField(primary_key=True)
    pregunta = models.CharField(max_length=255, blank=False, null=False)
    id_albergue = models.ForeignKey(Albergues, models.DO_NOTHING, db_column='id_albergue')

    class Meta:
        
        db_table = 'preguntas_formulario'


class Productos(models.Model):
    id_producto = models.AutoField(primary_key=True)
    descripcion_producto = models.CharField(max_length=255, blank=True, null=True)
    nombre_producto = models.CharField(max_length=100, blank=True, null=True)
    precio = models.FloatField(blank=True, null=True)
    id_empresa = models.ForeignKey(Empresas, models.DO_NOTHING, db_column='id_empresa')
    imagen = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
       
        db_table = 'productos'


class RespuestasFormulario(models.Model):
    id_respuesta = models.AutoField(primary_key=True)
    respuesta = models.TextField(blank=True, null=True)
    id_adopcion = models.ForeignKey(Adopciones, models.DO_NOTHING, db_column='id_adopcion')
    id_pregunta = models.ForeignKey(PreguntasFormulario, models.DO_NOTHING, db_column='id_pregunta')

    class Meta:
        
        db_table = 'respuestas_formulario'


class Transacciones(models.Model):
    id_transaccion = models.AutoField(primary_key=True)
    estado_transaccion = models.CharField(max_length=10, blank=True, null=True)
    fecha_entrega = models.DateField(blank=True, null=True)
    id_donacion = models.ForeignKey(Donaciones, models.DO_NOTHING, db_column='id_donacion')
    id_empresa = models.ForeignKey(Empresas, models.DO_NOTHING, db_column='id_empresa')

    class Meta:
        
        db_table = 'transacciones'


class Usuarios(models.Model):
    id = models.BigAutoField(primary_key=True)
    contraseña = models.CharField(max_length=255, blank=True, null=True)
    correo = models.CharField(max_length=255, blank=True, null=True)
    departamento = models.CharField(max_length=255, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)
    distrito = models.CharField(max_length=255, blank=True, null=True)
    nombre = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=255, blank=True, null=True)
    tipo_usuario = models.CharField(max_length=255, blank=True, null=True)
    imagen = models.URLField('imagen', blank=True, null=True)  # Imagen de perfil

    class Meta:
        db_table = 'usuarios'
