from django.shortcuts import render, get_object_or_404, redirect
from .models import RespuestasFormulario, Mascotas, Albergues, Usuarios,Chat, PreguntasFormulario, Adopciones
from .forms import MascotaForm, PreguntaForm, AlbergueForm 
from django.urls import reverse
from django.utils import timezone

def aceptar_solicitud(request, id_adopcion):
    adopcion = get_object_or_404(Adopciones, id_adopcion=id_adopcion)
    adopcion.estado_solicitud = 'ACEPTADA'
    adopcion.fecha_resolucion = timezone.now()
    adopcion.save()
    return redirect(f"{reverse('lista_solicitudes_adopcion')}?correo={request.GET.get('correo')}")

def rechazar_solicitud(request, id_adopcion):
    adopcion = get_object_or_404(Adopciones, id_adopcion=id_adopcion)
    adopcion.estado_solicitud = 'RECHAZADA'
    adopcion.fecha_resolucion = timezone.now()
    adopcion.save()
    return redirect(f"{reverse('lista_solicitudes_adopcion')}?correo={request.GET.get('correo')}")



def chat(request, id_usuario):
    correo_usuario = request.GET.get('correo')
    albergue = Albergues.objects.filter(id_usuario__correo=correo_usuario).first()
    if not albergue:
        return render(request, 'albergue/error.html', {'mensaje': 'No se encontró el albergue del usuario.'})

    usuario = get_object_or_404(Usuarios, id=id_usuario)
    mensajes = Chat.objects.filter(id_albergue=albergue, id_usuario=usuario).order_by('fecha_envio')

    if request.method == 'POST':
        mensaje = request.POST.get('mensaje')
        if mensaje:
            Chat.objects.create(
                emisor='albergue',
                mensaje=mensaje,
                fecha_envio=timezone.now(),
                id_albergue=albergue,
                id_usuario=usuario
            )
        return redirect(f"{reverse('chat', args=[id_usuario])}?correo={correo_usuario}")

    return render(request, 'albergue/chat/chat.html', {
        'mensajes': mensajes,
        'correo': correo_usuario,
        'usuario': usuario,
    })

from django.utils import timezone

def detalle_solicitud(request, id_adopcion):
    correo_usuario = request.GET.get('correo')
    adopcion = get_object_or_404(Adopciones, id_adopcion=id_adopcion)

    if request.method == 'POST':
        if 'aceptar' in request.POST:
            adopcion.estado_solicitud = 'ACEPTADA'
        elif 'rechazar' in request.POST:
            adopcion.estado_solicitud = 'RECHAZADA'
        adopcion.save()
        return redirect(f"{reverse('lista_solicitudes_adopcion')}?correo={correo_usuario}")

    respuestas = RespuestasFormulario.objects.filter(id_adopcion=adopcion)

    return render(request, 'albergue/adopciones/detalle_solicitud.html', {
        'adopcion': adopcion,
        'respuestas': respuestas,
        'correo': correo_usuario
    })



def lista_solicitudes_adopcion(request):
    correo_usuario = request.GET.get('correo')
    if not correo_usuario:
        return render(request, 'albergue/error.html', {'mensaje': 'No se proporcionó el correo del usuario.'})

    albergue = Albergues.objects.filter(id_usuario__correo=correo_usuario).first()
    if not albergue:
        return render(request, 'albergue/error.html', {'mensaje': 'No se encontró el albergue del usuario.'})

    solicitudes = Adopciones.objects.filter(id_perro__id_albergue=albergue)

    return render(request, 'albergue/adopciones/lista_solicitudes.html', {
        'solicitudes': solicitudes,
        'correo': correo_usuario
    })


def validar_albergue(request):
    correo = request.GET.get('correo')
    if not correo:
        return render(request, 'albergue/error.html', {'mensaje': 'Correo no proporcionado.'})

    # Buscar el usuario por correo
    usuario = Usuarios.objects.filter(correo=correo).first()
    if not usuario:
        return render(request, 'albergue/error.html', {'mensaje': 'Usuario no encontrado.'})

    # Verificar si ya tiene un albergue
    albergue = Albergues.objects.filter(id_usuario=usuario).first()
    if albergue:
        # Redirigir a la lista de mascotas si ya tiene un albergue
        return redirect(f"{reverse('lista_mascotas')}?correo={correo}")

    # Crear automáticamente un albergue para el usuario
    Albergues.objects.create(
        id_usuario=usuario,
        nombre=f"Albergue de {usuario.nombre}",
        correo=usuario.correo,
    )
    # Redirigir a la lista de mascotas después de crear el albergue
    return redirect(f"{reverse('lista_mascotas')}?correo={correo}")


def lista_mascotas(request):
    correo_usuario = request.GET.get('correo')
    if not correo_usuario:
        return render(request, 'albergue/error.html', {'mensaje': 'No se proporcionó el correo del usuario.'})

    # Verificar si el usuario tiene un albergue asociado
    albergue = Albergues.objects.filter(id_usuario__correo=correo_usuario).first()
    if not albergue:
        return redirect(f"{reverse('crear_albergue')}?correo={correo_usuario}")

    # Obtener las mascotas asociadas al albergue
    mascotas = Mascotas.objects.filter(id_albergue=albergue.id_albergue)
    return render(request, 'albergue/mascotas/lista_mascotas.html', {
        'mascotas': mascotas,
        'correo': correo_usuario,
    })


def crear_mascota(request):
    correo_usuario = request.GET.get('correo')
    albergue = Albergues.objects.filter(id_usuario__correo=correo_usuario).first()

    if not albergue:
        return render(request, 'albergue/error.html', {'mensaje': 'No se encontró el albergue del usuario.'})

    if request.method == 'POST':
        form = MascotaForm(request.POST, request.FILES)
        if form.is_valid():
            mascota = form.save(commit=False)
            mascota.id_albergue = albergue  # Asignar el albergue automáticamente
            mascota.save()
            return redirect(f"{reverse('lista_mascotas')}?correo={correo_usuario}")
    else:
        form = MascotaForm()

    return render(request, 'albergue/mascotas/crear_mascota.html', {'form': form})

def actualizar_mascota(request, id_perro):
    mascota = get_object_or_404(Mascotas, id_perro=id_perro)


    correo_usuario = request.GET.get('correo')
    if not correo_usuario:
        return render(request, 'albergue/error.html', {'mensaje': 'No se proporcionó el correo del usuario.'})


    albergue = Albergues.objects.filter(id_usuario__correo=correo_usuario).first()
    if not albergue:
        return render(request, 'albergue/error.html', {'mensaje': 'No tiene un albergue asociado.'})

 
    if mascota.id_albergue.id_albergue != albergue.id_albergue:
        return render(request, 'albergue/error.html', {'mensaje': 'No tiene permiso para editar esta mascota.'})


    if request.method == 'POST':
        form = MascotaForm(request.POST, request.FILES, instance=mascota)
        if form.is_valid():
            form.save()
            return redirect(f"{reverse('lista_mascotas')}?correo={correo_usuario}")
    else:
        form = MascotaForm(instance=mascota)

    return render(request, 'albergue/mascotas/actualizar_mascota.html', {'form': form})
def eliminar_mascota(request, id_perro):
    # Obtener la mascota por ID
    mascota = get_object_or_404(Mascotas, id_perro=id_perro)

    # Eliminar la mascota
    mascota.delete()

    # Redirigir a la lista de mascotas
    return redirect(f"{reverse('lista_mascotas')}?correo={request.GET.get('correo')}")


def lista_preguntas(request):
    correo_usuario = request.GET.get('correo')
    if not correo_usuario:
        return render(request, 'albergue/error.html', {
            'mensaje': 'Por favor, proporcione el correo del usuario o inicie sesión.'
        })

    # Obtener el albergue asociado al correo del usuario
    albergue = Albergues.objects.filter(id_usuario__correo=correo_usuario).first()
    if not albergue:
        return render(request, 'albergue/error.html', {
            'mensaje': 'No se encontró un albergue asociado a este correo.'
        })

    # Obtener las preguntas asociadas al albergue
    preguntas = PreguntasFormulario.objects.filter(id_albergue=albergue.id_albergue)
    return render(request, 'albergue/preguntas/lista_preguntas.html', {
        'preguntas': preguntas,
        'correo': correo_usuario,
    })



def crear_pregunta(request):
    correo_usuario = request.GET.get('correo')
    if not correo_usuario:
        return render(request, 'albergue/error.html', {'mensaje': 'No se proporcionó el correo del usuario.'})

    
    albergue = Albergues.objects.filter(id_usuario__correo=correo_usuario).first()
    if not albergue:
        return render(request, 'albergue/error.html', {'mensaje': 'No se encontró el albergue del usuario.'})

    if request.method == 'POST':
        form = PreguntaForm(request.POST)
        if form.is_valid():
            pregunta = form.save(commit=False)
            pregunta.id_albergue = albergue  
            pregunta.save()
            return redirect(f"{reverse('lista_preguntas')}?correo={correo_usuario}")
    else:
        form = PreguntaForm()

    return render(request, 'albergue/preguntas/crear_pregunta.html', {'form': form, 'correo': correo_usuario})


def actualizar_pregunta(request, id_pregunta):
    pregunta = get_object_or_404(PreguntasFormulario, id_pregunta=id_pregunta)
    correo_usuario = request.GET.get('correo')

    if request.method == 'POST':
        form = PreguntaForm(request.POST, instance=pregunta)
        if form.is_valid():
            form.save()
            return redirect(f"{reverse('lista_preguntas')}?correo={correo_usuario}")
    else:
        form = PreguntaForm(instance=pregunta)

    return render(request, 'albergue/preguntas/actualizar_pregunta.html', {'form': form, 'correo': correo_usuario})


def eliminar_pregunta(request, id_pregunta):
    pregunta = get_object_or_404(PreguntasFormulario, id_pregunta=id_pregunta)
    correo_usuario = request.GET.get('correo')

    if request.method == 'POST':
        pregunta.delete()
        return redirect(f"{reverse('lista_preguntas')}?correo={correo_usuario}")

    return render(request, 'albergue/preguntas/eliminar_pregunta.html', {'pregunta': pregunta, 'correo': correo_usuario})

def crear_albergue(request):
    correo = request.GET.get('correo')
    if not correo:
        return render(request, 'albergue/error.html', {'mensaje': 'Correo no proporcionado.'})

    usuario = Usuarios.objects.filter(correo=correo).first()
    if not usuario:
        return render(request, 'albergue/error.html', {'mensaje': 'Usuario no encontrado.'})

    if request.method == 'POST':
        form = AlbergueForm(request.POST)
        if form.is_valid():
            albergue = form.save(commit=False)
            albergue.id_usuario = usuario  
            albergue.correo = correo
            albergue.save()
            return redirect(f"{reverse('lista_mascotas')}?correo={correo}")
    else:
        form = AlbergueForm()

    return render(request, 'albergue/albergues/crear_albergue.html', {'form': form, 'correo': correo})