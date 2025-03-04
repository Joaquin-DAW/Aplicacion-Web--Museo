from rest_framework import serializers
from .models import *
from .forms import *
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = '__all__'
        
class ResponsableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Responsable
        fields = '__all__'
        
class ExposicionSerializer(serializers.ModelSerializer):
    museo = serializers.SerializerMethodField()  # 🔹 Agregamos este campo personalizado

    class Meta:
        model = Exposicion
        fields = ['id', 'titulo', 'fecha_inicio', 'fecha_fin', 'descripcion', 'capacidad', 'museo']

    def get_museo(self, obj):
        """ Devuelve el nombre del museo en lugar de su ID """
        return obj.museo.nombre if obj.museo else "Sin Museo"  # Maneja casos sin museo
    
class MuseoSerializer(serializers.ModelSerializer):
    exposiciones = ExposicionSerializer(many=True, read_only=True) 

    class Meta:
        model = Museo
        fields = ['id', 'nombre', 'ubicacion', 'fecha_fundacion', 'descripcion', 'exposiciones']
        
class EntradaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entrada
        fields = '__all__'
        
class GuiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guia
        fields = '__all__'

class VisitanteSerializer(serializers.ModelSerializer):
    usuario = serializers.StringRelatedField()  # Para que devuelva el nombre de usuario

    class Meta:
        model = Visitante
        fields = '__all__'
        
class TiendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tienda
        fields = ['id', 'nombre', 'ubicacion']
        
class VisitaGuiadaSerializer(serializers.ModelSerializer):
    guias = serializers.StringRelatedField(many=True)
    visitantes = serializers.StringRelatedField(many=True)

    class Meta:
        model = VisitaGuiada
        fields = ['id', 'nombre_visita_guia', 'duracion', 'capacidad_maxima', 'idioma', 'guias', 'visitantes']

        
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
    
class ExposicionSerializerEditarCapacidad(serializers.ModelSerializer):
    class Meta:
        model = Exposicion
        fields = ['capacidad']

    def validate_capacidad(self, capacidad):
        if capacidad <= 0:
            raise serializers.ValidationError("La capacidad debe ser mayor que cero.")
        return capacidad

class VisitaGuiadaSerializerCreate(serializers.ModelSerializer):
    guias = serializers.PrimaryKeyRelatedField(
        queryset=Guia.objects.all(),  # ✅ Permitir solo IDs válidos de Guías
        many=True
    )
    visitantes = serializers.PrimaryKeyRelatedField(
        queryset=Visitante.objects.all(),  # ✅ Permitir solo IDs válidos de Visitantes
        many=True
    )

    class Meta:
        model = VisitaGuiada
        fields = ['id', 'nombre_visita_guia', 'duracion', 'capacidad_maxima', 'idioma', 'guias', 'visitantes']

    def validate_nombre_visita_guia(self, nombre):
        """
        Valida que no haya dos visitas guiadas con el mismo nombre.
        """
        if self.instance:  # Si estamos editando...
            if VisitaGuiada.objects.exclude(id=self.instance.id).filter(nombre_visita_guia=nombre).exists():
                raise serializers.ValidationError("Ya existe una visita guiada con ese nombre.")
        else:  # Si estamos creando...
            if VisitaGuiada.objects.filter(nombre_visita_guia=nombre).exists():
                raise serializers.ValidationError("Ya existe una visita guiada con ese nombre.")
        return nombre
    
    def validate_duracion(self, value):
        """
        Valida que la duración esté en el formato correcto.
        """
        if not isinstance(value, timedelta):
            raise serializers.ValidationError("Formato incorrecto. Use HH:MM:SS")
        return value

    def validate_capacidad_maxima(self, capacidad):
        """
        Valida que la capacidad máxima sea un número positivo.
        """
        if capacidad <= 0:
            raise serializers.ValidationError("La capacidad debe ser mayor que cero.")
        return capacidad
    
class VisitaGuiadaSerializerEditarCapacidad(serializers.ModelSerializer):
    class Meta:
        model = VisitaGuiada
        fields = ['capacidad_maxima']

    def validate_capacidad_maxima(self, capacidad):
        if capacidad <= 0:
            raise serializers.ValidationError("La capacidad debe ser mayor que cero.")
        return capacidad
    
    
class TiendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tienda
        fields = ['id', 'nombre', 'ubicacion']
        
class InventarioSerializer(serializers.ModelSerializer):
    producto = serializers.StringRelatedField() 
    tienda = serializers.CharField(source="tienda.nombre") 

    class Meta:
        model = Inventario
        fields = ['producto', 'tienda', 'cantidad_vendida', 'fecha_ultima_venta', 'stock_inicial', 'ubicacion_almacen']

class ProductoSerializer(serializers.ModelSerializer):
    inventario = InventarioSerializer(source='inventario_producto', many=True, read_only=True)  # 🔹 Relación intermedia

    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'descripcion', 'precio', 'stock', 'inventario']
        
        
class ProductoSerializerCreate(serializers.ModelSerializer):
    tiendas = serializers.PrimaryKeyRelatedField(
        queryset=Tienda.objects.all(),  
        many=True
    )
    descripcion = serializers.CharField(required=False, allow_blank=True, default="")
    stock_inicial = serializers.IntegerField(write_only=True, min_value=1)
    cantidad_vendida = serializers.IntegerField(write_only=True, min_value=0)
    fecha_ultima_venta = serializers.DateField(write_only=True, required=False, allow_null=True)
    ubicacion_almacen = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'descripcion', 'precio', 'stock', 'tiendas', 'stock_inicial', 'cantidad_vendida', 'fecha_ultima_venta', 'ubicacion_almacen']

    def validate_nombre(self, nombre):
        if self.instance:
            if Producto.objects.exclude(id=self.instance.id).filter(nombre=nombre).exists():
                raise serializers.ValidationError("Ya existe un producto con este nombre.")
        else:
            if Producto.objects.filter(nombre=nombre).exists():
                raise serializers.ValidationError("Ya existe un producto con este nombre.")
        return nombre

    def create(self, validated_data):
        tiendas = validated_data.pop("tiendas", [])  
        stock_inicial = validated_data.pop("stock_inicial", 0)
        cantidad_vendida = validated_data.pop("cantidad_vendida", 0)
        fecha_ultima_venta = validated_data.pop("fecha_ultima_venta", None)
        ubicacion_almacen = validated_data.pop("ubicacion_almacen", "")
        
        validated_data["descripcion"] = validated_data.get("descripcion", "")
        
        producto = Producto.objects.create(**validated_data)

        for tienda in tiendas:
            Inventario.objects.create(
                producto=producto,
                tienda=tienda,
                stock_inicial=stock_inicial,
                cantidad_vendida=cantidad_vendida,
                fecha_ultima_venta=fecha_ultima_venta,
                ubicacion_almacen=ubicacion_almacen
            )

        return producto
    
class ProductoSerializerEditarStock(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ['stock']

    def validate_stock(self, stock):
        if stock < 0:
            raise serializers.ValidationError("El stock no puede ser negativo.")
        return stock


class UsuarioSerializerRegistro(serializers.Serializer):
    username = serializers.CharField()
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    email = serializers.EmailField()
    rol = serializers.IntegerField()

    def validate_username(self, username):
        """ Verifica que no exista un usuario con ese username """
        usuario = Usuario.objects.filter(username=username).first()
        if usuario:
            raise serializers.ValidationError("Ya existe un usuario con ese nombre.")
        return username