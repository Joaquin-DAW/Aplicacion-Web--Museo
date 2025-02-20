from rest_framework import serializers
from .models import *
from .forms import *
from datetime import datetime

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'
        
class ResponsableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Responsable
        fields = '__all__'
        
class MuseoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Museo
        fields = '__all__'
        
class ExposicionSerializer(serializers.ModelSerializer):
    museo = serializers.SerializerMethodField()  # 🔹 Agregamos este campo personalizado

    class Meta:
        model = Exposicion
        fields = ['id', 'titulo', 'fecha_inicio', 'fecha_fin', 'descripcion', 'capacidad', 'museo']

    def get_museo(self, obj):
        """ Devuelve el nombre del museo en lugar de su ID """
        return obj.museo.nombre if obj.museo else "Sin Museo"  # Maneja casos sin museo
        
class EntradaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entrada
        fields = '__all__'
        
class ObraSerializer(serializers.ModelSerializer):
    artista = serializers.StringRelatedField()
    exposicion = serializers.StringRelatedField()
    
    class Meta:
        model = Obra
        fields = '__all__'
        
class ArtistaSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Artista
        fields = '__all__'
        
class MuseoSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = Museo
        fields = ['id','nombre', 'ubicacion', 'fecha_fundacion', 'descripcion']
    
    def validate_nombre(self, nombre):
        if Museo.objects.filter(nombre=nombre).exists():
            raise serializers.ValidationError("Ya existe un museo con ese nombre")
        return nombre
    
    def validate_descripcion(self, descripcion):
        if len(descripcion) < 10:
            raise serializers.ValidationError("La descripción debe tener al menos 10 caracteres")
        return descripcion
    
    def validate_fecha_fundacion(self, fecha_fundacion):
        if fecha_fundacion > date.today():
            raise serializers.ValidationError("La fecha de fundación no puede ser en el futuro")
        return fecha_fundacion
    
class MuseoSerializerEditarNombre(serializers.ModelSerializer):

    class Meta:
        model = Museo
        fields = ['nombre']

    def validate_nombre(self, nombre):
        museo_existente = Museo.objects.filter(nombre=nombre).first()
        if museo_existente and museo_existente.id != self.instance.id:
            raise serializers.ValidationError("Ya existe un museo con ese nombre.")
        return nombre
    
    
class ExposicionSerializerCreate(serializers.ModelSerializer):
    museo = serializers.PrimaryKeyRelatedField(
        queryset=Museo.objects.all()  # ✅ Filtra solo IDs de museos válidos
    )

    class Meta:
        model = Exposicion
        fields = ['id', 'titulo', 'fecha_inicio', 'fecha_fin', 'descripcion', 'capacidad', 'museo']

    def validate_titulo(self, titulo):
        """
        Valida que el título no esté duplicado en otras exposiciones.
        Al editar, se excluye la propia exposición de la validación.
        """
        if self.instance:  # Si estamos editando...
            if Exposicion.objects.exclude(id=self.instance.id).filter(titulo=titulo).exists():
                raise serializers.ValidationError("Ya existe una exposición con ese título")
        else:  # Si estamos creando...
            if Exposicion.objects.filter(titulo=titulo).exists():
                raise serializers.ValidationError("Ya existe una exposición con ese título")
        return titulo

    def validate_fecha_fin(self, fecha_fin):
        fecha_inicio = self.initial_data.get('fecha_inicio')

        if isinstance(fecha_inicio, str):  # 🔹 Convertir `fecha_inicio` si es string
            fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()

        if fecha_inicio and fecha_fin and fecha_fin < fecha_inicio:
            raise serializers.ValidationError("La fecha de fin debe ser posterior a la de inicio")

        return fecha_fin
    
    def validate_capacidad(self, capacidad):
        if capacidad <= 0:
            raise serializers.ValidationError("La capacidad debe ser mayor que cero")
        return capacidad