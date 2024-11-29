from django import forms
from .models import Albergues

class AlbergueForm(forms.ModelForm):
    class Meta:
        model = Albergues
        fields = ['nombre', 'direccion', 'departamento', 'distrito', 'telefono']
