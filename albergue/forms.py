from django import forms
from .models import Mascotas, Albergues, PreguntasFormulario

class MascotaForm(forms.ModelForm):
    class Meta:
        model = Mascotas
        exclude = ['id_albergue']  # Excluir este campo porque se rellenará automáticamente
        widgets = {
            'sexo': forms.Select(choices=[('macho', 'Macho'), ('hembra', 'Hembra')]),
            'tamano': forms.Select(choices=[('pequeno', 'Pequeño'), ('mediano', 'Mediano'), ('grande', 'Grande')]),
        }
class AlbergueForm(forms.ModelForm):
    class Meta:
        model = Albergues
        fields = ['nombre', 'telefono', 'direccion', 'departamento', 'distrito']

class PreguntaForm(forms.ModelForm):
    class Meta:
        model = PreguntasFormulario
        fields = ['pregunta']
