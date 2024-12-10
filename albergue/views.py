from django.http import JsonResponse
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from cloudinary.uploader import upload
import cloudinary
import cloudinary.uploader
cloudinary.config( 
  cloud_name = 'do738mxyr', 
  api_key = '116257429418361', 
  api_secret = 'jP_P06j4MDE4SKLFy3i9KmgEZZk' 
)

from .models import (
    RespuestasFormulario, Mascotas, Albergues, Usuarios, 
    PreguntasFormulario, Adopciones, Donaciones, Imagenes
)
from .forms import MascotaForm, PreguntaForm, AlbergueForm


@csrf_exempt
@transaction.atomic  # Asegura que se ejecuta dentro de una transacción
@require_http_methods(["POST"])
def aceptar_solicitud(request, id_adopcion):
    try:
        # Bloque dentro de la transacción
        adopcion = Adopciones.objects.select_for_update().get(id_adopcion=id_adopcion)
        adopcion.estado_solicitud = 'aprobada'
        adopcion.fecha_resolucion = timezone.now()
        adopcion.save()
        return JsonResponse({"mensaje": "Solicitud aceptada", "id_adopcion": id_adopcion}, status=200)
    except Adopciones.DoesNotExist:
        return JsonResponse({"error": "Adopción no encontrada"}, status=404)


@csrf_exempt
def rechazar_solicitud(request, id_adopcion):
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)
    adopcion = get_object_or_404(Adopciones, id_adopcion=id_adopcion)
    adopcion.estado_solicitud = 'rechazada'
    adopcion.fecha_resolucion = timezone.now()
    adopcion.save()
    return JsonResponse({"mensaje": "Solicitud rechazada", "id_adopcion": id_adopcion}, status=200)


def detalle_solicitud(request, id_adopcion):
    correo_usuario = request.GET.get('correo')
    if not correo_usuario:
        return JsonResponse({"error": "No se proporcionó el correo del usuario."}, status=400)

    adopcion = get_object_or_404(Adopciones, id_adopcion=id_adopcion)
    respuestas = RespuestasFormulario.objects.filter(id_adopcion=adopcion).values(
        "id_respuesta", "id_pregunta__pregunta", "respuesta"
    )

    adopcion_data = {
        "id_adopcion": adopcion.id_adopcion,
        "estado_solicitud": adopcion.estado_solicitud,
        "fecha_solicitud": adopcion.fecha_solicitud,
        "fecha_resolucion": adopcion.fecha_resolucion,
        "id_perro": adopcion.id_perro.id_perro if adopcion.id_perro else None,
        "id_usuario": adopcion.id_usuario.id if adopcion.id_usuario else None,
        "respuestas": list(respuestas)
    }
    return JsonResponse(adopcion_data, status=200)


def lista_solicitudes_adopcion(request):
    correo_usuario = request.GET.get('correo')
    if not correo_usuario:
        return JsonResponse({"error": "No se proporcionó el correo del usuario."}, status=400)

    albergue = Albergues.objects.filter(id_usuario__correo=correo_usuario).first()
    if not albergue:
        return JsonResponse({"error": "No se encontró un albergue asociado a este correo."}, status=404)

    solicitudes = Adopciones.objects.filter(id_perro__id_albergue=albergue).values(
        "id_adopcion",
        "id_usuario__nombre",
        "id_perro__nombre",
        "fecha_solicitud",
        "estado_solicitud"
    )

    solicitudes_data = []
    for solicitud in solicitudes:
        respuestas = RespuestasFormulario.objects.filter(id_adopcion=solicitud['id_adopcion']).values(
            "id_pregunta__pregunta", "respuesta"
        )
        solicitudes_data.append({
            "id_adopcion": solicitud["id_adopcion"],
            "adoptante": solicitud["id_usuario__nombre"],
            "mascota": solicitud["id_perro__nombre"],
            "fecha": solicitud["fecha_solicitud"],
            "estado": solicitud["estado_solicitud"],
            "respuestas": list(respuestas)
        })

    return JsonResponse(solicitudes_data, safe=False, status=200)


@csrf_exempt
def validar_albergue(request):
    correo = request.GET.get('correo')
    if not correo:
        return JsonResponse({"error": "Correo no proporcionado."}, status=400)

    usuario = Usuarios.objects.filter(correo=correo).first()
    if not usuario:
        return JsonResponse({"error": "Usuario no encontrado."}, status=404)

    albergue = Albergues.objects.filter(id_usuario=usuario).first()
    if albergue:
        return JsonResponse({"mensaje": "Albergue ya existente", "id_albergue": albergue.id_albergue}, status=200)
    else:
        nuevo_albergue = Albergues.objects.create(
            id_usuario=usuario,
            nombre=f"Albergue de {usuario.nombre}",
            correo=usuario.correo,
        )
        return JsonResponse({"mensaje": "Albergue creado", "id_albergue": nuevo_albergue.id_albergue}, status=201)


def lista_mascotas(request):
    correo_usuario = request.GET.get('correo')
    if not correo_usuario:
        return JsonResponse({"error": "No se proporcionó el correo del usuario."}, status=400)

    albergue = Albergues.objects.filter(id_usuario__correo=correo_usuario).first()
    if not albergue:
        return JsonResponse({"error": "No se encontró el albergue del usuario."}, status=404)

    # Prefetch related 'imagenes_relacion' para optimizar consultas
    mascotas = Mascotas.objects.filter(id_albergue=albergue.id_albergue).prefetch_related('imagenes_relacion')

    data = []
    for mascota in mascotas:
        imagenes = []
        for img in mascota.imagenes_relacion.all():
            # Verificar y convertir campos de imagen si es necesario
            descripcion = img.descripcion.decode('utf-8') if isinstance(img.descripcion, bytes) else img.descripcion
            url = img.url.decode('utf-8') if isinstance(img.url, bytes) else img.url

            imagenes.append({
                "id_imagen": img.id_imagen,
                "descripcion": descripcion,
                "url": url
            })

        # Función auxiliar para convertir bytes a booleano
        def bytes_a_bool(valor):
            if isinstance(valor, bytes):
                return valor == b'\x01'
            return valor

        # Convertir 'vacunas_completas' y 'esterilizado' de bytes a bool
        vacunas_completas_bool = bytes_a_bool(mascota.vacunas_completas)
        esterilizado_bool = bytes_a_bool(mascota.esterilizado)

        data.append({
            "id_perro": mascota.id_perro,
            "nombre": mascota.nombre,
            "edad": mascota.edad,
            "raza": mascota.raza,
            "tamano": mascota.tamano,
            "sexo": mascota.sexo,
            "vacunas_completas": vacunas_completas_bool,
            "esterilizado": esterilizado_bool,
            "descripcion": mascota.descripcion,
            "imagenes": imagenes
        })

    # Imprimir el resultado final para depuración
    print("Data final:", data)

    return JsonResponse(data, safe=False, status=200)



@csrf_exempt
@require_http_methods(["POST"])
def crear_mascota(request):
    correo_usuario = request.GET.get('correo')
    if not correo_usuario:
        return JsonResponse({"error": "No se proporcionó el correo del usuario."}, status=400)

    albergue = Albergues.objects.filter(id_usuario__correo=correo_usuario).first()
    if not albergue:
        return JsonResponse({"error": "No se encontró el albergue del usuario."}, status=404)

    try:
        nombre = request.POST.get('nombre')
        edad = request.POST.get('edad')
        raza = request.POST.get('raza')
        tamano = request.POST.get('tamano')
        sexo = request.POST.get('sexo')
        vacunas_completas = request.POST.get('vacunas_completas', False)
        esterilizado = request.POST.get('esterilizado', False)
        descripcion = request.POST.get('descripcion', '')

        mascota = Mascotas.objects.create(
            nombre=nombre,
            edad=int(edad),
            raza=raza,
            tamano=tamano,
            sexo=sexo,
            vacunas_completas=bool(vacunas_completas),
            esterilizado=bool(esterilizado),
            descripcion=descripcion,
            id_albergue=albergue
        )

        imagenes = request.FILES.getlist('imagenes')
        
        # 🔥 Subir cada imagen a Cloudinary
        for imagen in imagenes:
            upload_result = cloudinary.uploader.upload(imagen)
            Imagenes.objects.create(
                id_perro=mascota, 
                url=upload_result['secure_url'], 
                descripcion=f"Imagen de {mascota.nombre}"
            )

        return JsonResponse({"mensaje": "Mascota creada exitosamente", "id_perro": mascota.id_perro}, status=201)
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        return JsonResponse({"error": f"Error inesperado: {str(e)}"}, status=500)


@csrf_exempt
def actualizar_mascota(request, id_perro):
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)

    # Validar el correo del usuario
    correo_usuario = request.GET.get('correo')
    if not correo_usuario:
        return JsonResponse({"error": "No se proporcionó el correo del usuario."}, status=400)

    # Obtener la mascota y validar si pertenece al albergue del usuario
    mascota = get_object_or_404(Mascotas, id_perro=id_perro)
    albergue = Albergues.objects.filter(id_usuario__correo=correo_usuario).first()
    if not albergue:
        return JsonResponse({"error": "No tiene un albergue asociado."}, status=404)

    if mascota.id_albergue.id_albergue != albergue.id_albergue:
        return JsonResponse({"error": "No tiene permiso para editar esta mascota."}, status=403)

    # Validar y guardar los datos del formulario
    form = MascotaForm(request.POST, request.FILES, instance=mascota)
    if form.is_valid():
        form.save()
        return JsonResponse({"mensaje": "Mascota actualizada exitosamente"}, status=200)

    # Si el formulario no es válido, devolver errores detallados
    return JsonResponse({"error": form.errors}, status=400)


@csrf_exempt
@transaction.atomic  # Asegura que todas las operaciones ocurren dentro de una transacción
def eliminar_mascota(request, id_perro):
    try:
        # Validar el correo del usuario
        correo_usuario = request.GET.get('correo')
        if not correo_usuario:
            return JsonResponse({"error": "No se proporcionó el correo del usuario."}, status=400)

        # Obtener la mascota que se va a eliminar
        mascota = get_object_or_404(Mascotas, id_perro=id_perro)

        # 1. Eliminar respuestas relacionadas en RespuestasFormulario
        RespuestasFormulario.objects.filter(id_adopcion__id_perro=mascota).delete()

        # 2. Eliminar adopciones relacionadas en Adopciones
        Adopciones.objects.filter(id_perro=mascota).delete()

        # 3. Eliminar imágenes relacionadas si existe relación con una tabla de imágenes
        mascota.imagenes_relacion.all().delete()

        # 4. Finalmente, eliminar la mascota
        mascota.delete()

        return JsonResponse({"mensaje": "Mascota eliminada con éxito"}, status=200)

    except Mascotas.DoesNotExist:
        return JsonResponse({"error": "La mascota no existe."}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"Error inesperado: {str(e)}"}, status=500)

def lista_preguntas(request):
    correo_usuario = request.GET.get('correo')
    if not correo_usuario:
        return JsonResponse({"error": "Por favor, proporcione el correo del usuario."}, status=400)

    albergue = Albergues.objects.filter(id_usuario__correo=correo_usuario).first()
    if not albergue:
        return JsonResponse({"error": "No se encontró un albergue asociado a este correo."}, status=404)

    preguntas = PreguntasFormulario.objects.filter(id_albergue=albergue.id_albergue).values("id_pregunta", "pregunta")
    return JsonResponse(list(preguntas), safe=False, status=200)



@csrf_exempt
def crear_pregunta(request):
    if request.method == 'POST':
        correo_usuario = request.GET.get('correo')
        if not correo_usuario:
            return JsonResponse({"error": "No se proporcionó el correo del usuario."}, status=400)

        albergue = Albergues.objects.filter(id_usuario__correo=correo_usuario).first()
        if not albergue:
            return JsonResponse({"error": "No se encontró el albergue del usuario."}, status=404)

        try:
            data = json.loads(request.body.decode('utf-8'))
            nueva_pregunta = data.get('pregunta')
            if not nueva_pregunta or nueva_pregunta.strip() == "":
                return JsonResponse({"error": "La pregunta no puede estar vacía."}, status=400)

            pregunta = PreguntasFormulario.objects.create(
                pregunta=nueva_pregunta.strip(),
                id_albergue=albergue
            )
            return JsonResponse({"mensaje": "Pregunta creada", "id_pregunta": pregunta.id_pregunta}, status=201)
        except Exception as e:
            return JsonResponse({"error": f"Error inesperado: {str(e)}"}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def actualizar_pregunta(request, id_pregunta):
    pregunta = get_object_or_404(PreguntasFormulario, id_pregunta=id_pregunta)

    if request.method == 'POST':
        correo_usuario = request.GET.get('correo')
        if not correo_usuario:
            return JsonResponse({"error": "No se proporcionó el correo del usuario."}, status=400)

        try:
            data = json.loads(request.body.decode('utf-8'))
            nueva_pregunta = data.get('pregunta')
            if not nueva_pregunta or nueva_pregunta.strip() == "":
                return JsonResponse({"error": "La pregunta no puede estar vacía."}, status=400)

            pregunta.pregunta = nueva_pregunta.strip()
            pregunta.save()
            return JsonResponse({"mensaje": "Pregunta actualizada", "id_pregunta": pregunta.id_pregunta}, status=200)
        except Exception as e:
            return JsonResponse({"error": f"Error inesperado: {str(e)}"}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)



@csrf_exempt
def eliminar_pregunta(request, id_pregunta):
    """
    Elimina una pregunta y todas las respuestas asociadas.
    """
    pregunta = get_object_or_404(PreguntasFormulario, id_pregunta=id_pregunta)

    if request.method in ['DELETE', 'POST']:
        try:
            
            pregunta.respuestasformulario_set.all().delete()

            
            pregunta.delete()

            return JsonResponse({"mensaje": "Pregunta y sus respuestas asociadas eliminadas con éxito"}, status=200)
        except Exception as e:
            return JsonResponse({"error": f"Error inesperado: {str(e)}"}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def crear_albergue(request):
    correo = request.GET.get('correo')
    if not correo:
        return JsonResponse({"error": "Correo no proporcionado."}, status=400)

    usuario = Usuarios.objects.filter(correo=correo).first()
    if not usuario:
        return JsonResponse({"error": "Usuario no encontrado."}, status=404)

    if request.method == 'POST':
        form = AlbergueForm(request.POST)
        if form.is_valid():
            albergue = form.save(commit=False)
            albergue.id_usuario = usuario
            albergue.correo = correo
            albergue.save()
            return JsonResponse({"mensaje": "Albergue creado", "id_albergue": albergue.id_albergue}, status=201)
        else:
            return JsonResponse({"error": form.errors}, status=400)
    else:
        return JsonResponse({"error": "Método no permitido"}, status=405)


def lista_donaciones(request):
    correo_usuario = request.GET.get('correo')
    if not correo_usuario:
        return JsonResponse({"error": "No se proporcionó el correo del usuario."}, status=400)

    albergue = Albergues.objects.filter(id_usuario__correo=correo_usuario).first()
    if not albergue:
        return JsonResponse({"error": "No se encontró el albergue del usuario."}, status=404)

    donaciones = Donaciones.objects.filter(id_albergue=albergue.id_albergue).values(
        "id_donacion", "monto_total", "fecha_donacion", 
        "id_usuario__nombre", "id_usuario__correo"
    )
    return JsonResponse(list(donaciones), safe=False, status=200)


def ver_perfil(request):
    correo_usuario = request.GET.get('correo')
    if not correo_usuario:
        return JsonResponse({"error": "No se proporcionó el correo del usuario."}, status=400)

    usuario = Usuarios.objects.filter(correo=correo_usuario).first()
    if not usuario:
        return JsonResponse({"error": "Usuario no encontrado."}, status=404)

    perfil_data = {
        "id_usuario": usuario.id,  # Ajustado a usuario.id
        "nombre": usuario.nombre,
        "correo": usuario.correo,
        "tipo_usuario": usuario.tipo_usuario,
        "departamento": usuario.departamento,
        "direccion": usuario.direccion,
        "distrito": usuario.distrito,
        "telefono": usuario.telefono,
        "imagen": usuario.imagen  # Incluye la URL de la imagen
    }
    return JsonResponse(perfil_data, status=200)



@csrf_exempt
def editar_perfil(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido."}, status=405)

    correo_usuario = request.GET.get('correo')
    if not correo_usuario:
        return JsonResponse({"error": "No se proporcionó el correo del usuario."}, status=400)

    usuario = Usuarios.objects.filter(correo=correo_usuario).first()
    if not usuario:
        return JsonResponse({"error": "Usuario no encontrado."}, status=404)

    try:
        # Procesar datos enviados en el cuerpo de la solicitud
        data = json.loads(request.POST.get('data', '{}'))
        imagen = request.FILES.get('imagen')  # Subir imagen

        if imagen:
            resultado = upload(imagen)  # Subir la imagen a Cloudinary
            usuario.imagen = resultado['secure_url']  # Guardar la URL segura de Cloudinary

        # Actualizar otros campos del perfil si se proporcionan
        campos_permitidos = ["nombre", "departamento", "direccion", "distrito", "telefono"]
        for campo in campos_permitidos:
            if campo in data:
                setattr(usuario, campo, data[campo])

        usuario.save()
        return JsonResponse({"mensaje": "Perfil actualizado con éxito"}, status=200)
    except Exception as e:
        return JsonResponse({"error": f"Error inesperado: {str(e)}"}, status=500)



@csrf_exempt
def editar_albergue(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido."}, status=405)

    correo_usuario = request.GET.get('correo')
    if not correo_usuario:
        return JsonResponse({"error": "No se proporcionó el correo del usuario."}, status=400)

    albergue = Albergues.objects.filter(id_usuario__correo=correo_usuario).first()
    if not albergue:
        return JsonResponse({"error": "No se encontró un albergue asociado a este usuario."}, status=404)

    try:
        # Manejar datos enviados como multipart/form-data
        nombre = request.POST.get("name")
        description = request.POST.get("description")
        departamento = request.POST.get("departamento")
        direccion = request.POST.get("direccion")
        distrito = request.POST.get("distrito")

        if nombre:
            albergue.nombre = nombre
        if description:
            albergue.descripcion = description
        if departamento:
            albergue.departamento = departamento
        if direccion:
            albergue.direccion = direccion
        if distrito:
            albergue.distrito = distrito

        # Manejar imagen si se envía
        if 'imagen' in request.FILES:
            imagen = request.FILES['imagen']
            upload_result = cloudinary.uploader.upload(imagen)
            albergue.imagen = upload_result['secure_url']  # Asegúrate de que `imagen` sea un campo en el modelo Albergues

        albergue.save()
        return JsonResponse({"mensaje": "Albergue actualizado con éxito"}, status=200)
    except Exception as e:
        return JsonResponse({"error": f"Error inesperado: {str(e)}"}, status=500)


def detalle_albergue(request):
    # Obtener el correo del usuario que está autenticado
    correo_usuario = request.GET.get('correo')
    if not correo_usuario:
        return JsonResponse({"error": "No se proporcionó el correo del usuario."}, status=400)

    # Buscar el albergue relacionado con el usuario
    albergue = Albergues.objects.filter(id_usuario__correo=correo_usuario).first()
    if not albergue:
        return JsonResponse({"error": "No se encontró un albergue asociado a este usuario."}, status=404)

    # Preparar los datos del albergue para enviarlos en el JSON
    albergue_data = {
        "id_albergue": albergue.id_albergue,
        "nombre": albergue.nombre,
        "correo": albergue.correo,
        "departamento": albergue.departamento,
        "direccion": albergue.direccion,
        "distrito": albergue.distrito,
        "telefono": albergue.telefono,
        "descripcion": albergue.descripcion,
        "imagen": albergue.imagen,  # Aquí se incluye la URL de la imagen
    }

    return JsonResponse(albergue_data, status=200)