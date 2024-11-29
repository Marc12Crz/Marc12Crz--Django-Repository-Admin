from django.urls import path
from . import views

urlpatterns = [

        # Solicitudes de adopción
    path('adopciones/', views.lista_solicitudes_adopcion, name='lista_solicitudes_adopcion'),
    path('adopciones/<int:id_adopcion>/', views.detalle_solicitud, name='detalle_solicitud'),

 path('adopciones/aceptar/<int:id_adopcion>/', views.aceptar_solicitud, name='aceptar_solicitud'),
path('adopciones/rechazar/<int:id_adopcion>/', views.rechazar_solicitud, name='rechazar_solicitud'),
path('chat/<int:id_usuario>/', views.chat, name='chat'),
    # Validar y redirigir al albergue o crearlo automáticamente
    path('validar_albergue/', views.validar_albergue, name='validar_albergue'),

    #crear albergue
     path('albergues/crear/', views.crear_albergue, name='crear_albergue'), 

#mascotas 
    path('mascotas/', views.lista_mascotas, name='lista_mascotas'),
    path('mascotas/crear/', views.crear_mascota, name='crear_mascota'),
    path('mascotas/actualizar/<int:id_perro>/', views.actualizar_mascota, name='actualizar_mascota'),
    path('mascotas/eliminar/<int:id_perro>/', views.eliminar_mascota, name='eliminar_mascota'),
#preguntas
    path('preguntas/', views.lista_preguntas, name='lista_preguntas'),
    path('preguntas/crear/', views.crear_pregunta, name='crear_pregunta'),
    path('preguntas/actualizar/<int:id_pregunta>/', views.actualizar_pregunta, name='actualizar_pregunta'),
    path('preguntas/eliminar/<int:id_pregunta>/', views.eliminar_pregunta, name='eliminar_pregunta'),
]