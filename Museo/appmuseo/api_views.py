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


@api_view(['GET'])
def obra_buscar_avanzada(request):
    formulario = BusquedaAvanzadaObraForm(request.query_params)
    
    if formulario.is_valid():
        titulo = formulario.cleaned_data.get('titulo')
        fecha_creacion_desde = formulario.cleaned_data.get('fecha_creacion_desde')
        fecha_creacion_hasta = formulario.cleaned_data.get('fecha_creacion_hasta')
        tipo = formulario.cleaned_data.get('tipo')
        exposicion = formulario.cleaned_data.get('exposicion')
        artista = formulario.cleaned_data.get('artista')
        
        obras = Obra.objects.all()
        if titulo:
            obras = obras.filter(titulo__icontains=titulo)
        if fecha_creacion_desde:
            obras = obras.filter(fecha_creacion__gte=fecha_creacion_desde)
        if fecha_creacion_hasta:
            obras = obras.filter(fecha_creacion__lte=fecha_creacion_hasta)
        if tipo:
            obras = obras.filter(tipo=tipo)
        if exposicion:
            obras = obras.filter(exposicion=exposicion)
        if artista:
            obras = obras.filter(artista=artista)
        
        serializer = ObraSerializer(obras, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(formulario.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def exposicion_buscar_avanzada(request):
    # Instancia el formulario con los parámetros GET (query_params)
    formulario = BusquedaAvanzadaExposicionForm(request.query_params)
    
    if formulario.is_valid():
        # Extraer datos limpios del formulario
        titulo = formulario.cleaned_data.get('titulo')
        descripcion = formulario.cleaned_data.get('descripcion')
        fecha_inicio_desde = formulario.cleaned_data.get('fecha_desde')
        fecha_inicio_hasta = formulario.cleaned_data.get('fecha_hasta')
        museo = formulario.cleaned_data.get('museo')
        
        # Iniciar la consulta base
        exposiciones = Exposicion.objects.all()
        
        # Filtro por título y/o descripción (se usa OR)
        if titulo or descripcion:
            q = Q()
            if titulo:
                q |= Q(titulo__icontains=titulo)
            if descripcion:
                q |= Q(descripcion__icontains=descripcion)
            exposiciones = exposiciones.filter(q)
        
        # Filtro por fecha de inicio desde
        if fecha_inicio_desde:
            exposiciones = exposiciones.filter(fecha_inicio__gte=fecha_inicio_desde)
        
        # Filtro por fecha de inicio hasta
        if fecha_inicio_hasta:
            exposiciones = exposiciones.filter(fecha_inicio__lte=fecha_inicio_hasta)
        
        # Filtro por museo
        if museo:
            exposiciones = exposiciones.filter(museo=museo)
        
        serializer = ExposicionSerializer(exposiciones, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(formulario.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def entrada_buscar_avanzada(request):
    # Instanciar el formulario con los parámetros GET (request.query_params)
    formulario = BusquedaAvanzadaEntradaForm(request.query_params)
    
    if formulario.is_valid():
        # Extraer campos limpios
        codigo = formulario.cleaned_data.get('codigo')
        tipo = formulario.cleaned_data.get('tipo')
        fecha_compra_desde = formulario.cleaned_data.get('fecha_compra_desde')
        fecha_compra_hasta = formulario.cleaned_data.get('fecha_compra_hasta')
        precio_min = formulario.cleaned_data.get('precio_min')
        precio_max = formulario.cleaned_data.get('precio_max')
        visitante = formulario.cleaned_data.get('visitante')
        
        # Iniciar la consulta base
        entradas = Entrada.objects.all()
        
        if codigo:
            entradas = entradas.filter(codigo__icontains=codigo)
        if tipo:
            entradas = entradas.filter(tipo=tipo)
        if fecha_compra_desde:
            entradas = entradas.filter(fecha_compra__gte=fecha_compra_desde)
        if fecha_compra_hasta:
            entradas = entradas.filter(fecha_compra__lte=fecha_compra_hasta)
        if precio_min:
            entradas = entradas.filter(precio__gte=precio_min)
        if precio_max:
            entradas = entradas.filter(precio__lte=precio_max)
        if visitante:
            entradas = entradas.filter(visitante=visitante)
        
        serializer = EntradaSerializer(entradas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(formulario.errors, status=status.HTTP_400_BAD_REQUEST)