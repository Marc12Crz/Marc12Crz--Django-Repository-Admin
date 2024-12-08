from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

from .models import (
    RespuestasFormulario, Mascotas, Albergues, Usuarios, 
    PreguntasFormulario, Adopciones, Donaciones
)
from .forms import MascotaForm, PreguntaForm, AlbergueForm


@csrf_exempt
def aceptar_solicitud(request, id_adopcion):
    if request.method != 'POST':
        return JsonResponse({"error": "Método no permitido"}, status=405)
    adopcion = get_object_or_404(Adopciones, id_adopcion=id_adopcion)
    adopcion.estado_solicitud = 'aprobada'
    adopcion.fecha_resolucion = timezone.now()
    adopcion.save()
    return JsonResponse({"mensaje": "Solicitud aceptada", "id_adopcion": id_adopcion}, status=200)


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
        return JsonResponse({"error": "No se encontró el albergue del usuario."}, status=404)

    solicitudes = Adopciones.objects.filter(id_perro__id_albergue=albergue).values(
        "id_adopcion", "estado_solicitud", "fecha_solicitud", "fecha_resolucion", 
        "id_perro__nombre", "id_usuario__nombre"
    )

    return JsonResponse(list(solicitudes), safe=False, status=200)


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

    mascotas = Mascotas.objects.filter(id_albergue=albergue.id_albergue).values("id_perro", "nombre", "edad", "raza")
    return JsonResponse(list(mascotas), safe=False, status=200)


@csrf_exempt
def crear_mascota(request):
    correo_usuario = request.GET.get('correo')
    if not correo_usuario:
        return JsonResponse({"error": "No se proporcionó el correo del usuario."}, status=400)

    albergue = Albergues.objects.filter(id_usuario__correo=correo_usuario).first()
    if not albergue:
        return JsonResponse({"error": "No se encontró el albergue del usuario."}, status=404)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Parseas el JSON
        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON inválido."}, status=400)

        # Como MascotaForm espera un diccionario similar a un POST, puedes pasar data directo:
        form = MascotaForm(data)
        if form.is_valid():
            mascota = form.save(commit=False)
            mascota.id_albergue = albergue
            mascota.save()
            return JsonResponse({
                "mensaje": "Mascota creada exitosamente",
                "id_perro": mascota.id_perro
            }, status=201)
        else:
            return JsonResponse({"error": form.errors}, status=400)
    else:
        return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def actualizar_mascota(request, id_perro):
    mascota = get_object_or_404(Mascotas, id_perro=id_perro)
    correo_usuario = request.GET.get('correo')
    if not correo_usuario:
        return JsonResponse({"error": "No se proporcionó el correo del usuario."}, status=400)

    albergue = Albergues.objects.filter(id_usuario__correo=correo_usuario).first()
    if not albergue:
        return JsonResponse({"error": "No tiene un albergue asociado."}, status=404)

    if mascota.id_albergue.id_albergue != albergue.id_albergue:
        return JsonResponse({"error": "No tiene permiso para editar esta mascota."}, status=403)

    if request.method == 'POST':
        form = MascotaForm(request.POST, request.FILES, instance=mascota)
        if form.is_valid():
            form.save()
            return JsonResponse({"mensaje": "Mascota actualizada"}, status=200)
        else:
            return JsonResponse({"error": form.errors}, status=400)
    else:
        return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def eliminar_mascota(request, id_perro):
    correo_usuario = request.GET.get('correo')
    if not correo_usuario:
        return JsonResponse({"error": "No se proporcionó el correo del usuario."}, status=400)

    mascota = get_object_or_404(Mascotas, id_perro=id_perro)
    albergue = Albergues.objects.filter(id_usuario__correo=correo_usuario).first()
    if not albergue or mascota.id_albergue.id_albergue != albergue.id_albergue:
        return JsonResponse({"error": "No tiene permiso para eliminar esta mascota."}, status=403)

    if request.method in ['DELETE', 'POST']:
        mascota.delete()
        return JsonResponse({"mensaje": "Mascota eliminada con éxito"}, status=200)
    else:
        return JsonResponse({"error": "Método no permitido"}, status=405)


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
    correo_usuario = request.GET.get('correo')
    if not correo_usuario:
        return JsonResponse({"error": "No se proporcionó el correo del usuario."}, status=400)

    albergue = Albergues.objects.filter(id_usuario__correo=correo_usuario).first()
    if not albergue:
        return JsonResponse({"error": "No se encontró el albergue del usuario."}, status=404)

    if request.method == 'POST':
        form = PreguntaForm(request.POST)
        if form.is_valid():
            pregunta = form.save(commit=False)
            pregunta.id_albergue = albergue
            pregunta.save()
            return JsonResponse({"mensaje": "Pregunta creada", "id_pregunta": pregunta.id_pregunta}, status=201)
        else:
            return JsonResponse({"error": form.errors}, status=400)
    else:
        return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def actualizar_pregunta(request, id_pregunta):
    pregunta = get_object_or_404(PreguntasFormulario, id_pregunta=id_pregunta)
    correo_usuario = request.GET.get('correo')
    if not correo_usuario:
        return JsonResponse({"error": "No se proporcionó el correo del usuario."}, status=400)

    if request.method == 'POST':
        form = PreguntaForm(request.POST, instance=pregunta)
        if form.is_valid():
            form.save()
            return JsonResponse({"mensaje": "Pregunta actualizada"}, status=200)
        else:
            return JsonResponse({"error": form.errors}, status=400)
    else:
        return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def eliminar_pregunta(request, id_pregunta):
    pregunta = get_object_or_404(PreguntasFormulario, id_pregunta=id_pregunta)
    correo_usuario = request.GET.get('correo')
    if not correo_usuario:
        return JsonResponse({"error": "No se proporcionó el correo del usuario."}, status=400)

    if request.method in ['DELETE', 'POST']:
        pregunta.delete()
        return JsonResponse({"mensaje": "Pregunta eliminada con éxito"}, status=200)
    else:
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
        "tipo_usuario": usuario.tipo_usuario
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
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido."}, status=400)

    nuevo_nombre = data.get("nombre")
    if nuevo_nombre:
        usuario.nombre = nuevo_nombre

    usuario.save()
    return JsonResponse({"mensaje": "Perfil actualizado con éxito"}, status=200)


def detalle_albergue(request):
    correo_usuario = request.GET.get('correo')
    if not correo_usuario:
        return JsonResponse({"error": "No se proporcionó el correo del usuario."}, status=400)

    albergue = Albergues.objects.filter(id_usuario__correo=correo_usuario).first()
    if not albergue:
        return JsonResponse({"error": "No se encontró un albergue asociado a este usuario."}, status=404)

    albergue_data = {
        "id_albergue": albergue.id_albergue,
        "nombre": albergue.nombre,
        "correo": albergue.correo,
    }
    return JsonResponse(albergue_data, status=200)


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
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "JSON inválido."}, status=400)

    nuevo_nombre = data.get("nombre")
    if nuevo_nombre:
        albergue.nombre = nuevo_nombre

    albergue.save()
    return JsonResponse({"mensaje": "Albergue actualizado con éxito"}, status=200)
