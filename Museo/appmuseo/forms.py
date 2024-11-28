from django import forms
from django.forms import ModelForm
from .models import *
from datetime import date
import datetime


class MuseoModelForm(ModelForm):
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
 
        #Comprobamos que no exista un museo con ese nombre y que sea mayor a 200 caracteres
        if len(nombre) > 200:
                self.add_error('nombre', 'El nombre no puede superar los 200 caracteres.')
                
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
            
        #Comprobamos que la fecha de fundación no sea mayor que hoy
        fechaHoy = date.today()
        if fecha_fundacion > fechaHoy:
                self.add_error('fecha_fundacion', 'La fecha de fundación debe ser menor a hoy.')

        #Comprobamos que el campo descripción no tenga menos de 10 caracteres        
        if len(descripcion) < 10:
            self.add_error('descripcion','Al menos debes indicar 10 caracteres')
        
        #Siempre devolvemos el conjunto de datos.
        return self.cleaned_data
    
    
class BusquedaAvanzadaMuseoForm(forms.Form):
    nombre_descripcion = forms.CharField(
        required=False, 
        label="Escriba el nombre o la descripción del museo",
        widget=forms.TextInput(attrs={"placeholder": "Nombre o descripción del museo"})
    )
    ubicacion = forms.CharField(
        required=False, 
        label="Escriba la ubicación del museo",
        widget=forms.TextInput(attrs={"placeholder": "Ubicación del museo"})
    )

    fecha_desde = forms.DateField(
        label="Fecha Desde",
        required=False,
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"})
    )
    fecha_hasta = forms.DateField(
        label="Fecha Hasta",
        required=False,
        widget=forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"})
    )

    def clean(self):
        super().clean()
        nombre_descripcion = self.cleaned_data.get('nombre_descripcion')
        ubicacion = self.cleaned_data.get('ubicacion')
        fecha_desde = self.cleaned_data.get('fecha_desde')
        fecha_hasta = self.cleaned_data.get('fecha_hasta')

        # Validación: al menos un campo debe estar lleno
        if (nombre_descripcion == "" and ubicacion =="" and fecha_desde is None and fecha_hasta is None):
            self.add_error('nombre_descripcion','Debe introducir al menos un valor en un campo del formulario')
            self.add_error('ubicacion','Debe introducir al menos un valor en un campo del formulario')
            self.add_error('fecha_desde','Debe introducir al menos un valor en un campo del formulario')
            self.add_error('fecha_hasta','Debe introducir al menos un valor en un campo del formulario')

        # Validación: fecha_hasta no puede ser menor que fecha_desde
        if(not fecha_desde is None  and not fecha_hasta is None and fecha_hasta < fecha_desde):
            self.add_error('fecha_desde', "La fecha hasta no puede ser menor que la fecha desde.")
            self.add_error('fecha_hasta', "La fecha hasta no puede ser menor que la fecha desde.")

        return self.cleaned_data