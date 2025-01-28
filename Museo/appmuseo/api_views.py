from .models import *
from .serializers import *
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
def museo_buscar_avanzado_api(request):
    """
    Vista API para buscar museos avanzados.
    """
    if len(request.query_params) > 0:
        # Recibir los parámetros de búsqueda
        nombre_descripcion = request.query_params.get('nombre_descripcion', None)
        ubicacion = request.query_params.get('ubicacion', None)
        fecha_desde = request.query_params.get('fecha_desde', None)
        fecha_hasta = request.query_params.get('fecha_hasta', None)

        # Inicializar la consulta base
        museos = Museo.objects.all()

        # Aplicar filtros condicionales
        if nombre_descripcion:
            museos = museos.filter(Q(nombre__icontains=nombre_descripcion) | Q(descripcion__icontains=nombre_descripcion))
        
        if ubicacion:
            museos = museos.filter(ubicacion__icontains=ubicacion)
        
        if fecha_desde:
            museos = museos.filter(fecha_fundacion__gte=fecha_desde)
        
        if fecha_hasta:
            museos = museos.filter(fecha_fundacion__lte=fecha_hasta)

        # Serializar los resultados
        serializer = MuseoSerializer(museos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # Si no hay parámetros, retornar un error o mensaje vacío
    return Response({"error": "No se han proporcionado parámetros de búsqueda."}, status=status.HTTP_400_BAD_REQUEST)