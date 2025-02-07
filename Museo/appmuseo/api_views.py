from .models import *
from .serializers import *
from django.db.models import Q,Prefetch
from rest_framework.response import Response
from rest_framework.decorators import api_view,authentication_classes,permission_classes
from rest_framework import status
from .forms import *


@api_view(['GET'])
def museo_list(request):
    museos = Museo.objects.all()
    serializer = MuseoSerializer(museos, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def obra_list(request):
    obras = Obra.objects.select_related('artista', 'exposicion').all()
    serializer = ObraSerializer(obras, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def exposicion_list(request):
    exposiciones = Exposicion.objects.select_related('museo').all()
    serializer = ExposicionSerializer(exposiciones, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def entrada_list(request):
    entradas = Entrada.objects.select_related('visitante').all()
    serializer = EntradaSerializer(entradas, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def museo_buscar_simple(request):
    formulario = BusquedaMuseoForm(request.query_params)

    if formulario.is_valid():
        texto = formulario.cleaned_data.get('textoBusqueda')
        museos = Museo.objects.select_related("creado_por")
        museos = museos.filter(Q(nombre__icontains=texto) | Q(descripcion__icontains=texto)).all()

        if not museos:
            return Response({"message": "No se encontraron museos con los criterios de búsqueda."}, status=status.HTTP_404_NOT_FOUND)

        # Usar un serializer para convertir los museos a formato JSON
        serializer = MuseoSerializer(museos, many=True)
        return Response(serializer.data)

    # Si el formulario no es válido, devuelve los errores de la validación
    return Response(formulario.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def museo_buscar_avanzada(request):
    
    formulario = BusquedaAvanzadaMuseoForm(request.query_params)
    
    if formulario.is_valid():
        nombre_descripcion = formulario.cleaned_data.get('nombre_descripcion')
        ubicacion = formulario.cleaned_data.get('ubicacion')
        fecha_desde = formulario.cleaned_data.get('fecha_desde')
        fecha_hasta = formulario.cleaned_data.get('fecha_hasta')
        
        # Inicializar la consulta base
        museos = Museo.objects.all()
        if nombre_descripcion:
            museos = museos.filter(Q(nombre__icontains=nombre_descripcion) | Q(descripcion__icontains=nombre_descripcion))
        if ubicacion:
            museos = museos.filter(ubicacion__icontains=ubicacion)
        if fecha_desde:
            museos = museos.filter(fecha_fundacion__gte=fecha_desde)
        if fecha_hasta:
            museos = museos.filter(fecha_fundacion__lte=fecha_hasta)

        serializer = MuseoSerializer(museos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(formulario.errors, status=status.HTTP_400_BAD_REQUEST)