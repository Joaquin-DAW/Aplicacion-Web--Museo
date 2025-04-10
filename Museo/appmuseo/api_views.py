from .models import *
from .serializers import *
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated

from rest_framework.permissions import AllowAny
from django.contrib.auth.decorators import login_required
from .forms import *


@api_view(['GET'])
def museo_list(request):
    museos = Museo.objects.prefetch_related('exposiciones').all()
    serializer = MuseoSerializer(museos, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def obra_list(request):
    obras = Obra.objects.select_related('artista', 'exposicion').all()
    serializer = ObraSerializer(obras, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def artista_list(request):
    artistas = Artista.objects.all()
    serializer = ArtistaSerializer(artistas, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def exposicion_list(request):
    
    exposiciones = Exposicion.objects.select_related('museo').all()
    serializer = ExposicionSerializer(exposiciones, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def entrada_list(request):
    user = request.user

    print(f"Usuario autenticado: {user}")  # Ver qué usuario está autenticado
    print(f"Usuario ID: {user.id}")  # Ver ID del usuario
    print(f"Rol del usuario: {user.rol}")  # Ver rol del usuario


    # Bloquear acceso a usuarios no autenticados
    if not user.is_authenticated:
        return Response({"error": "Debes estar autenticado para ver las entradas."}, status=status.HTTP_401_UNAUTHORIZED)

    # Si el usuario es un responsable, puede ver todas las entradas
    if user.rol == Usuario.RESPONSABLE:
        entradas = Entrada.objects.all()

    # Si el usuario es un visitante, solo puede ver su propia entrada
    elif user.rol == Usuario.VISITANTE:
        entradas = Entrada.objects.filter(visitante__usuario=user)

    # Si no es responsable ni visitante, denegar el acceso
    else:
        return Response({"error": "No tienes permisos para ver entradas."}, status=status.HTTP_403_FORBIDDEN)

    # Si no hay entradas, devolver mensaje en lugar de error
    if not entradas.exists():
        return Response({"mensaje": "No tienes entradas registradas."}, status=status.HTTP_204_NO_CONTENT)

    serializer = EntradaSerializer(entradas, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def guia_list(request):
    guias = Guia.objects.all()
    serializer = GuiaSerializer(guias, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def visitante_list(request):
    visitantes = Visitante.objects.all()
    serializer = VisitanteSerializer(visitantes, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def visita_guiada_list(request):
    visitas = VisitaGuiada.objects.all()  # Un responsable puede ver todas
    serializer = VisitaGuiadaSerializer(visitas, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def tienda_list(request):
    tiendas = Tienda.objects.all()
    serializer = TiendaSerializer(tiendas, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def producto_list(request):
    """
    Obtiene la lista de productos junto con la información de las tiendas y el inventario asociado.
    """
    productos = Producto.objects.prefetch_related('inventario_producto').all()  # 🔹 Relación con Inventario
    serializer = ProductoSerializer(productos, many=True)
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

@api_view(['POST'])
def museo_create(request):
    if not request.user.has_perm("appmuseo.add_museo"):
        return Response({"error": "No tienes permiso para crear museos."}, status=403)
    
    print(request.data)
    museo_serializer = MuseoSerializerCreate(data=request.data)
    if museo_serializer.is_valid():
        try:
            museo_serializer.save(creado_por=request.user)
            return Response("Museo CREADO", status=status.HTTP_201_CREATED)
        except serializers.ValidationError as error:
            return Response(error.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            print(repr(error))
            return Response(repr(error), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(museo_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
def museo_obtener(request, museo_id):
    try:
        museo = Museo.objects.get(id=museo_id)
        serializer = MuseoSerializerCreate(museo)  # Serializamos el museo existente
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Museo.DoesNotExist:
        return Response({"error": "Museo no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    
    
@api_view(['PUT'])
def museo_editar(request, museo_id):
    if not request.user.has_perm("appmuseo.change_museo"):
        return Response({"error": "No tienes permiso para crear museos."}, status=403)
    print("📥 Petición PUT recibida para museo:", museo_id)  # 🔹 Verifica si la API recibe la petición
    print("📨 Datos recibidos:", request.data) 
    try:
        museo = Museo.objects.get(id=museo_id)
    except Museo.DoesNotExist:
        return Response({"error": "Museo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    museo_serializer = MuseoSerializerCreate(data=request.data, instance=museo)
    if museo_serializer.is_valid():
        try:
            museo_serializer.save()
            return Response({"mensaje": "Museo EDITADO"}, status=status.HTTP_200_OK)
        except serializers.ValidationError as error:
            return Response(error.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({"error": repr(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(museo_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['PATCH'])
def museo_editar_nombre(request, museo_id):
    if not request.user.has_perm("appmuseo.change_museo"):
        return Response({"error": "No tienes permiso para crear museos."}, status=403)
    try:
        museo = Museo.objects.get(id=museo_id)
    except Museo.DoesNotExist:
        return Response({"error": "Museo no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    serializer = MuseoSerializerEditarNombre(data=request.data, instance=museo)
    if serializer.is_valid():
        try:
            serializer.save()
            return Response({"mensaje": "Nombre del museo actualizado correctamente"}, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({"error": repr(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['DELETE'])
def museo_eliminar(request, museo_id):
    if not request.user.has_perm("appmuseo.delete_museo"):
        return Response({"error": "No tienes permiso para crear museos."}, status=403)
    try:
        museo = Museo.objects.get(id=museo_id)
        museo.delete()
        return Response({"mensaje": "Museo eliminado correctamente"}, status=status.HTTP_200_OK)
    except Museo.DoesNotExist:
        return Response({"error": "Museo no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as error:
        return Response({"error": repr(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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

@api_view(['POST'])
def exposicion_create(request):
    if not request.user.has_perm("appmuseo.add_exposicion"):
        return Response({"error": "No tienes permiso para crear museos."}, status=403)
    print("📡 Datos recibidos en la API:", request.data)  # 🔍 Verifica los datos que llegan
    
    exposicion_serializer = ExposicionSerializerCreate(data=request.data)

    if exposicion_serializer.is_valid():
        try:
            exposicion_serializer.save()
            return Response({"mensaje": "Exposición CREADA"}, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as error:
            return Response(error.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            print("❌ Error en el servidor:", repr(error))  # 🔍 Muestra el error exacto
            return Response({"error": repr(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        print("❌ Errores de validación:", exposicion_serializer.errors)  # 🔍 Debug de validaciones
        return Response(exposicion_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
def exposicion_obtener(request, exposicion_id):
    """
    Obtiene los detalles de una exposición específica por su ID.
    """
    try:
        exposicion = Exposicion.objects.get(id=exposicion_id)
        serializer = ExposicionSerializerCreate(exposicion)  # Usa el serializador correcto
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exposicion.DoesNotExist:
        return Response({"error": "Exposición no encontrada"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
def exposicion_editar(request, exposicion_id):
    if not request.user.has_perm("appmuseo.change_exposicion"):
        return Response({"error": "No tienes permiso para crear museos."}, status=403)
    print("📥 Petición PUT recibida para exposición:", exposicion_id)  # 🔹 Verifica si la API recibe la petición
    print("📨 Datos recibidos:", request.data)

    try:
        exposicion = Exposicion.objects.get(id=exposicion_id)
    except Exposicion.DoesNotExist:
        return Response({"error": "Exposición no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    exposicion_serializer = ExposicionSerializerCreate(data=request.data, instance=exposicion)
    if exposicion_serializer.is_valid():
        try:
            exposicion_serializer.save()
            return Response({"mensaje": "Exposición EDITADA"}, status=status.HTTP_200_OK)
        except serializers.ValidationError as error:
            return Response(error.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({"error": repr(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(exposicion_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
def exposicion_editar_capacidad(request, exposicion_id):
    if not request.user.has_perm("appmuseo.change_exposicion"):
        return Response({"error": "No tienes permiso para crear museos."}, status=403)
    try:
        exposicion = Exposicion.objects.get(id=exposicion_id)
    except Exposicion.DoesNotExist:
        return Response({"error": "Exposición no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ExposicionSerializerEditarCapacidad(data=request.data, instance=exposicion)
    if serializer.is_valid():
        try:
            serializer.save()
            return Response({"mensaje": "Capacidad de la exposición actualizada correctamente"}, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({"error": repr(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['DELETE'])
def exposicion_eliminar(request, exposicion_id):
    if not request.user.has_perm("appmuseo.delete_exposicion"):
        return Response({"error": "No tienes permiso para crear museos."}, status=403)
    try:
        exposicion = Exposicion.objects.get(id=exposicion_id)
        exposicion.delete()
        return Response({"mensaje": "Exposición eliminada correctamente"}, status=status.HTTP_200_OK)
    except Exposicion.DoesNotExist:
        return Response({"error": "Exposición no encontrada"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as error:
        return Response({"error": repr(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['POST'])
@permission_classes([IsAuthenticated])  # ✅ Requiere autenticación
def entrada_create(request):
    if not request.user.has_perm("appmuseo.add_entrada"):
        return Response({"error": "No tienes permiso para crear entradas."}, status=403)
    
    print("📡 Datos recibidos en la API:", request.data)  # 🔍 Verifica los datos que llegan
    
    entrada_serializer = EntradaSerializerCreate(data=request.data, context={'request': request})
    
    if entrada_serializer.is_valid():
        try:
            entrada_serializer.save()
            return Response({"mensaje": "Entrada CREADA"}, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as error:
            return Response(error.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            print("❌ Error en el servidor:", repr(error))  # 🔍 Muestra el error exacto
            return Response({"error": repr(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        print("❌ Errores de validación:", entrada_serializer.errors)  # 🔍 Debug de validaciones
        return Response(entrada_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

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

@api_view(['DELETE'])
def entrada_eliminar(request, entrada_id):
    if not request.user.has_perm("appmuseo.delete_entrada"):
        return Response({"error": "No tienes permiso para crear museos."}, status=403)
    user = request.user
    try:
        entrada = Entrada.objects.get(id=entrada_id)
        
        # Solo el dueño de la entrada puede eliminarla
        if entrada.visitante.usuario != user:
            return Response({"error": "No tienes permiso para eliminar esta entrada."}, status=status.HTTP_403_FORBIDDEN)

        entrada.delete()
        return Response({"mensaje": "Entrada eliminada correctamente."}, status=status.HTTP_204_NO_CONTENT)

    except Entrada.DoesNotExist:
        return Response({"error": "Entrada no encontrada."}, status=status.HTTP_404_NOT_FOUND)
    
    
@api_view(['POST'])
def visita_guiada_create(request):
    if not request.user.has_perm("appmuseo.add_visitaguiada"):
        return Response({"error": "No tienes permiso para crear museos."}, status=403)
    print("Datos recibidos en la API:", request.data)  # Verifica los datos que llegan
    
    user = request.user

    if user.rol != Usuario.VISITANTE:
        return Response({"error": "Solo los visitantes pueden reservar visitas."}, status=status.HTTP_403_FORBIDDEN)

    data = request.data.copy()
    data["creador"] = [request.user.id]  #Se asigna automáticamente el usuario en la lista de visitantes
    
    visita_serializer = VisitaGuiadaSerializerCreate(data=request.data)

    if visita_serializer.is_valid():
        try:
            visita_serializer.save()
            print("Visita Guiada creada con éxito")
            return Response({"mensaje": "Visita Guiada CREADA"}, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as error:
            return Response(error.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            print("Error en el servidor:", repr(error))  # 🔍 Muestra el error exacto
            return Response({"error": repr(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        print("Errores de validación:", visita_serializer.errors)  # 🔍 Debug de validaciones
        return Response(visita_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
def visita_guiada_obtener(request, visita_id):
    try:
        visita = VisitaGuiada.objects.get(id=visita_id)
        serializer = VisitaGuiadaSerializerCreate(visita)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except VisitaGuiada.DoesNotExist:
        return Response({"error": "Visita guiada no encontrada"}, status=status.HTTP_404_NOT_FOUND)
    
@api_view(['PUT'])
def visita_guiada_editar(request, visita_id):
    if not request.user.has_perm("appmuseo.change_visita_guiada"):
        return Response({"error": "No tienes permiso para crear museos."}, status=403)
    print("📥 Petición PUT recibida para visita guiada:", visita_id)  # 🔹 Debug
    print("📨 Datos recibidos:", request.data)

    try:
        visita = VisitaGuiada.objects.get(id=visita_id)
    except VisitaGuiada.DoesNotExist:
        return Response({"error": "Visita guiada no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    visita_serializer = VisitaGuiadaSerializerCreate(instance=visita, data=request.data, partial=True)

    if visita_serializer.is_valid():
        try:
            visita_actualizada = visita_serializer.save()  # Guardamos los campos básicos

            # 🔹 Actualizamos las relaciones ManyToMany manualmente
            if "guias" in request.data:
                visita_actualizada.guias.set(request.data["guias"])  # ✅ Actualiza ManyToMany
            if "visitantes" in request.data:
                visita_actualizada.visitantes.set(request.data["visitantes"])  # ✅ Actualiza ManyToMany

            return Response({"mensaje": "Visita guiada EDITADA"}, status=status.HTTP_200_OK)

        except serializers.ValidationError as error:
            return Response(error.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({"error": repr(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    else:
        return Response(visita_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['PATCH'])
def visita_guiada_editar_capacidad(request, visita_id):
    if not request.user.has_perm("appmuseo.change_visita_guiada"):
        return Response({"error": "No tienes permiso para crear museos."}, status=403)
    try:
        visita = VisitaGuiada.objects.get(id=visita_id)
    except VisitaGuiada.DoesNotExist:
        return Response({"error": "Visita guiada no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    serializer = VisitaGuiadaSerializerEditarCapacidad(data=request.data, instance=visita)
    if serializer.is_valid():
        try:
            serializer.save()
            return Response({"mensaje": "Capacidad de la visita guiada actualizada correctamente"}, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({"error": repr(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
def visita_guiada_eliminar(request, visita_id):
    if not request.user.has_perm("appmuseo.delete_visita_guiada"):
        return Response({"error": "No tienes permiso para crear museos."}, status=403)
    try:
        visita = VisitaGuiada.objects.get(id=visita_id)
        visita.delete()
        return Response({"mensaje": "Visita guiada eliminada correctamente"}, status=status.HTTP_200_OK)
    except VisitaGuiada.DoesNotExist:
        return Response({"error": "Visita guiada no encontrada"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as error:
        return Response({"error": repr(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['POST'])
def producto_create(request):
    if not request.user.has_perm("appmuseo.add_producto"):
        return Response({"error": "No tienes permiso para crear museos."}, status=403)
    print("📡 Datos recibidos en la API:", request.data)  
    
    producto_serializer = ProductoSerializerCreate(data=request.data)

    if producto_serializer.is_valid():
        try:
            producto_serializer.save()
            print("✅ Producto creado con éxito")
            return Response({"mensaje": "Producto CREADO"}, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as error:
            return Response(error.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            print("❌ Error en el servidor:", repr(error))
            return Response({"error": repr(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        print("❌ Errores de validación:", producto_serializer.errors)  
        return Response(producto_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def producto_obtener(request, producto_id):
    try:
        producto = Producto.objects.get(id=producto_id)
        serializer = ProductoSerializerCreate(producto)
        
        # Convertimos los datos del producto a diccionario
        producto_data = serializer.data

        # Agregamos manualmente la información de inventario
        inventario_data = Inventario.objects.filter(producto=producto)
        producto_data["inventario"] = [
            {
                "tienda_id": item.tienda.id,
                "tienda_nombre": item.tienda.nombre,
                "stock_inicial": item.stock_inicial,
                "cantidad_vendida": item.cantidad_vendida,
                "fecha_ultima_venta": item.fecha_ultima_venta.strftime("%Y-%m-%d") if item.fecha_ultima_venta else None,
                "ubicacion_almacen": item.ubicacion_almacen
            }
            for item in inventario_data
        ]

        return Response(producto_data, status=status.HTTP_200_OK)
    
    except Producto.DoesNotExist:
        return Response({"error": "Producto no encontrado"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
def producto_editar(request, producto_id):
    if not request.user.has_perm("appmuseo.change_producto"):
        return Response({"error": "No tienes permiso para crear museos."}, status=403)
    print("📥 Petición PUT recibida para producto:", producto_id)  # 🔹 Debug
    print("📨 Datos recibidos:", request.data)

    try:
        producto = Producto.objects.get(id=producto_id)
    except Producto.DoesNotExist:
        return Response({"error": "Producto no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    producto_serializer = ProductoSerializerCreate(instance=producto, data=request.data, partial=True)

    if producto_serializer.is_valid():
        try:
            producto_actualizado = producto_serializer.save()  # Guardamos los campos básicos

            # 🔹 Actualizar la relación ManyToMany manualmente a través de Inventario
            if "tiendas" in request.data:
                tiendas_nuevas = request.data["tiendas"]
                stock_inicial = request.data.get("stock_inicial", 0)
                cantidad_vendida = request.data.get("cantidad_vendida", 0)
                fecha_ultima_venta = request.data.get("fecha_ultima_venta", None)
                ubicacion_almacen = request.data.get("ubicacion_almacen", "")

                # Eliminar Inventario antiguo y reemplazar con el nuevo
                producto_actualizado.inventario_producto.all().delete()

                for tienda_id in tiendas_nuevas:
                    Inventario.objects.create(
                        producto=producto_actualizado,
                        tienda=Tienda.objects.get(id=tienda_id),
                        stock_inicial=stock_inicial,
                        cantidad_vendida=cantidad_vendida,
                        fecha_ultima_venta=fecha_ultima_venta,
                        ubicacion_almacen=ubicacion_almacen
                    )

            return Response({"mensaje": "Producto EDITADO"}, status=status.HTTP_200_OK)

        except serializers.ValidationError as error:
            return Response(error.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({"error": repr(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    else:
        return Response(producto_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['PATCH'])
def producto_editar_stock(request, producto_id):
    if not request.user.has_perm("appmuseo.change_producto"):
        return Response({"error": "No tienes permiso para crear museos."}, status=403)
    try:
        producto = Producto.objects.get(id=producto_id)
    except Producto.DoesNotExist:
        return Response({"error": "Producto no encontrado"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProductoSerializerEditarStock(data=request.data, instance=producto, partial=True)
    if serializer.is_valid():
        try:
            serializer.save()
            return Response({"mensaje": "Stock del producto actualizado correctamente"}, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({"error": repr(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def producto_eliminar(request, producto_id):
    if not request.user.has_perm("appmuseo.delete_producto"):
        return Response({"error": "No tienes permiso para crear museos."}, status=403)
    try:
        producto = Producto.objects.get(id=producto_id)
        producto.delete()
        return Response({"mensaje": "Producto eliminado correctamente"}, status=status.HTTP_200_OK)
    except Producto.DoesNotExist:
        return Response({"error": "Producto no encontrado"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as error:
        return Response({"error": repr(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

class RegistrarUsuarioView(generics.CreateAPIView):
    serializer_class = UsuarioSerializerRegistro
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = UsuarioSerializerRegistro(data=request.data)
        if serializer.is_valid():
            try:
                rol_str = request.data.get('rol')
                rol=int(rol_str) if rol_str else None

                # Crear usuario
                user = Usuario.objects.create_user(
                    username=serializer.validated_data.get("username"),
                    email=serializer.validated_data.get("email"),
                    password=serializer.validated_data.get("password1"),
                    rol=rol,
                )

                # Asignar usuario a un grupo y crear instancia del rol correspondiente
                if rol == Usuario.VISITANTE:
                    grupo, _ = Group.objects.get_or_create(name="Visitantes")
                    grupo.user_set.add(user)
                    visitante = Visitante.objects.create(usuario=user, museo=None)
                    visitante.save()
                elif rol == Usuario.RESPONSABLE:
                    grupo, _ = Group.objects.get_or_create(name="Responsables")
                    grupo.user_set.add(user)
                    responsable = Responsable.objects.create(usuario=user)
                    responsable.save()

                # AUTENTICAR AL USUARIO RECIÉN REGISTRADO
                user = authenticate(username=user.username, password=request.data.get("password1"))

                if user:
                    # CREAR TOKEN PARA EL USUARIO
                    token, created = Token.objects.get_or_create(user=user)
                    
                    # IMPRIMIR INFO EN LA TERMINAL
                    print(f"Token generado para {user.username}: {token.key}")
                    print(f"Usuario autenticado: {user}")  
                    print(f"Usuario ID: {user.id}")  
                    print(f"Rol del usuario: {user.rol}")

                    return Response({
                        "mensaje": "Usuario registrado correctamente",
                        "token": token.key,
                        "username": user.username,
                        "rol": user.rol
                    }, status=status.HTTP_201_CREATED)
                else:
                    return Response({"error": "No se pudo autenticar al usuario."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            except Exception as error:
                print(repr(error))
                return Response({"error": "Error interno del servidor"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from oauth2_provider.models import AccessToken
    
@api_view(['GET'])
def obtener_usuario_token(request, token):
    try:
        modelo_token = AccessToken.objects.get(token=token)
        usuario = Usuario.objects.get(id=modelo_token.user_id)
        serializer = UsuarioSerializer(usuario)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except AccessToken.DoesNotExist:
        return Response({"error": "Token inválido o expirado"}, status=status.HTTP_401_UNAUTHORIZED)
    except Usuario.DoesNotExist:
        return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)