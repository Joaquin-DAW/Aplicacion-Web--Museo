from rest_framework import serializers
from .models import *
from .forms import *

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
    class Meta:
        model = Exposicion
        fields = '__all__'
        
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
        fields = ['nombre', 'ubicacion', 'fecha_fundacion', 'descripcion']
    
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