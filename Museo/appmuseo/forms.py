from django import forms
from django.forms import ModelForm
from .models import *
from datetime import date
import datetime

# Formulario para museo
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
        ubicacion = self.cleaned_data.get('ubicacion', '')
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
        if ubicacion and len(ubicacion) < 10:
            self.add_error('ubicacion','Al menos debes indicar 10 caracteres')
            
        #Comprobamos que la fecha de fundación no sea mayor que hoy
        fechaHoy = date.today()
        if not fecha_fundacion:
            self.add_error('fecha_fundacion', 'Debes introducir una fecha de fundación')
        elif fecha_fundacion > fechaHoy:
                self.add_error('fecha_fundacion', 'La fecha de fundación debe ser menor a hoy.')

        #Comprobamos que el campo descripción no tenga menos de 10 caracteres        
        if descripcion and len(descripcion) < 10:
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
    

# Formulario para exposición
class ExposicionModelForm(forms.ModelForm):
    class Meta:
        model = Exposicion
        fields = ['titulo', 'fecha_inicio', 'fecha_fin', 'descripcion', 'capacidad', 'museo']
        labels = {
            "titulo": "Título de la Exposición",
            "fecha_inicio": "Fecha de Inicio",
            "fecha_fin": "Fecha de Fin",
            "descripcion": "Descripción",
            "capacidad": "Capacidad Máxima",
            "museo": "Museo",
        }
        help_texts = {
            "titulo": "Título de la exposición (máximo 150 caracteres).",
            "fecha_inicio": "Fecha en la que comienza la exposición.",
            "fecha_fin": "Fecha en la que finaliza la exposición (puede dejarse en blanco).",
            "descripcion": "Breve descripción de la exposición (opcional).",
            "capacidad": "Número máximo de visitantes permitidos.",
            "museo": "Seleccione el museo al que pertenece la exposición.",
        }
        widgets = {
            "fecha_inicio": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "fecha_fin": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "descripcion": forms.Textarea(attrs={"rows": 3, "placeholder": "Añade una breve descripción de la exposición (opcional)."}),
        }
        localized_fields = ["fecha_inicio", "fecha_fin"]
        
    def clean(self):
        super().clean()

        # Obtener campos del formulario
        titulo = self.cleaned_data.get('titulo')
        fecha_inicio = self.cleaned_data.get('fecha_inicio')
        fecha_fin = self.cleaned_data.get('fecha_fin')
        descripcion = self.cleaned_data.get('descripcion', '')  # Valor por defecto si es None
        capacidad = self.cleaned_data.get('capacidad')
        museo = self.cleaned_data.get('museo')

        # Validar que el título no supere los 150 caracteres
        if len(titulo) > 150:
            self.add_error('titulo', 'El título no puede superar los 150 caracteres.')

        # Validar que no exista una exposición con el mismo título en el mismo museo
        exposicion_titulo = Exposicion.objects.filter(titulo=titulo, museo=museo).first()
        if exposicion_titulo and (not self.instance or exposicion_titulo.id != self.instance.id):
            self.add_error('titulo', 'Ya existe una exposición con este título en el museo seleccionado.')

        # Validar que la fecha de inicio no sea mayor que la fecha de fin
        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            self.add_error('fecha_inicio', 'La fecha de inicio debe ser anterior a la fecha de fin.')

        # Validar que la capacidad sea mayor que cero
        if capacidad is not None and capacidad <= 0:
            self.add_error('capacidad', 'La capacidad debe ser un número positivo.')

        # Validar que la descripción tenga al menos 10 caracteres (si se proporciona)
        if descripcion and len(descripcion) < 10:
            self.add_error('descripcion', 'La descripción debe tener al menos 10 caracteres.')

        return self.cleaned_data

class BusquedaAvanzadaExposicionForm(forms.Form):
    titulo = forms.CharField(
        required=False,
        label="Escriba el título de la exposición",
        widget=forms.TextInput(attrs={"placeholder": "Título de la exposición"})
    )
    descripcion = forms.CharField(
        required=False,
        label="Escriba la descripción de la exposición",
        widget=forms.TextInput(attrs={"placeholder": "Descripción de la exposición"})
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
    museo = forms.ModelChoiceField(
        queryset=Museo.objects.all(),
        required=False,
        label="Museo",
        empty_label="Seleccione un museo"
    )

    def clean(self):
        super().clean()
        titulo = self.cleaned_data.get('titulo')
        descripcion = self.cleaned_data.get('descripcion')
        fecha_desde = self.cleaned_data.get('fecha_desde')
        fecha_hasta = self.cleaned_data.get('fecha_hasta')
        museo = self.cleaned_data.get('museo')

        # Validación: al menos un campo debe estar lleno
        if (titulo == "" and descripcion == "" and fecha_desde is None and fecha_hasta is None and museo is None):
            self.add_error('titulo','Debe introducir al menos un valor en un campo del formulario')
            self.add_error('descripcion','Debe introducir al menos un valor en un campo del formulario')
            self.add_error('fecha_desde','Debe introducir al menos un valor en un campo del formulario')
            self.add_error('fecha_hasta','Debe introducir al menos un valor en un campo del formulario')
            self.add_error('museo','Debe seleccionar al menos un museo')
        
        # Validación: fecha_hasta no puede ser menor que fecha_desde
        if not fecha_desde is None and not fecha_hasta is None and fecha_hasta < fecha_desde:
            self.add_error('fecha_desde', "La fecha hasta no puede ser menor que la fecha desde.")
            self.add_error('fecha_hasta', "La fecha hasta no puede ser menor que la fecha desde.")

        return self.cleaned_data
