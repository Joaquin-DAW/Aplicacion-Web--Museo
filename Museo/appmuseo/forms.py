from django import forms
from django.forms import ModelForm
from .models import *
from datetime import date
import datetime


class MuseoModelForm(forms.ModelForm):
    class Meta:
        model = Museo
        fields = ['nombre', 'ubicacion', 'fecha_fundacion', 'descripcion']
        labels = {
            "nombre": "Nombre del Museo",
            "ubicacion": "Ubicación del museo",
            "fecha_fundacion": "Fecha de Fundación",
            "descripcion": "Descripción",
        }
        help_texts = {
            "nombre": "Nombre del museo (máximo 200 caracteres).",
            "ubicacion": "Proporcione la dirección o ubicación del museo.",
            "fecha_fundacion": "Fecha en que se fundó el museo.",
            "descripcion": "Breve descripción del museo.",
        }
        widgets = {
            "fecha_fundacion": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "descripcion": forms.Textarea(attrs={"rows": 3, "placeholder": "Añade una breve descripción del museo."}),
        }
        localized_fields = ["fecha_fundacion"]
        
def clean(self):
 
        #Validamos con el modelo actual
        super().clean()
        
        #Obtenemos los campos 
        nombre = self.cleaned_data.get('nombre')
        ubicacion = self.cleaned_data.get('ubicacion', '')  # Proporcionar valor por defecto si es None
        fecha_fundacion = self.cleaned_data.get('fecha_fundacion')
        descripcion = self.cleaned_data.get('descripcion', '')  # Proporcionar valor por defecto si es None
 
        #Comprobamos que no exista un museo con ese nombre
        museoNombre = Museo.objects.filter(nombre=nombre).first()
        if(not museoNombre is None
           ):
             if(not self.instance is None and museoNombre.id == self.instance.id):
                 pass
             else:
                self.add_error('nombre','Ya existe un museo con ese nombre')
                
        #Comprobamos que el campo ubicacion no tenga menos de 10 caracteres        
        if len(ubicacion) < 10:
            self.add_error('ubicacion','Al menos debes indicar 10 caracteres')
            
        #Comprobamos que la fecha de publicación sea mayor que hoy
        fechaHoy = date.today()
        if fechaHoy > fecha_fundacion :
             self.add_error('fecha_fundacion','La fecha de fundacion debe ser mayor a hoy')

        #Comprobamos que el campo descripción no tenga menos de 10 caracteres        
        if len(descripcion) < 10:
            self.add_error('descripcion','Al menos debes indicar 10 caracteres')
        
        #Siempre devolvemos el conjunto de datos.
        return self.cleaned_data