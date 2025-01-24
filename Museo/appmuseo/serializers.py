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
        
class ArtistaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artista
        fields = '__all__'
        
class ObraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Obra
        fields = '__all__'