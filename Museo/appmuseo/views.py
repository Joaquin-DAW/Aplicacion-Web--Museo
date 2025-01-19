from django.shortcuts import render,redirect
from django.db.models import Q, Avg
from .models import Museo,Obra,Exposicion, Visitante, Artista, Guia, Producto
from .forms import *
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Group

from datetime import datetime

#Index donde podremos acceder a todas las URLs.
def index(request):
    if(not "fecha_inicio" in request.session):
        request.session["fecha_inicio"] = datetime.now().strftime('%d/%m/%Y %H:%M')
        
    return render(request, 'index.html')

#Esta vista saca todos los datos de museo y accede a todos los modelos relacionados con el mismo para poder sacar información sobre ellos.
#Usamos prefetch_related en lugar de select_releted porque, aunque no haya ninguna relación ManyToMany, son relaciones reversas, ya que la foreingKey 
#se encuentra en los otros modelos.
#Esto tambien estaria usando una relación reversa.
def listar_museos(request):
    museos = (Museo.objects.prefetch_related("exposiciones","visitantes","tienda","guias")).all()
    return render(request, "museo/lista.html", {"museos":museos})

def listar_exposiciones(request):
    exposiciones = Exposicion.objects.select_related("museo").prefetch_related("obras_exposicion", "obras_exposicion__artista").all()
    return render(request, "exposicion/lista.html", {"exposiciones": exposiciones})

def listar_artistas(request):
    artistas = Artista.objects.prefetch_related("obras_artista").all()
    return render(request, "artista/lista.html", {"artistas": artistas})

def listar_obras(request):
    obras = Obra.objects.prefetch_related("artista", "exposicion").all()
    return render(request, "obra/lista.html", {"obras": obras})

def listar_guias(request):
    guias = Guia.objects.prefetch_related("museo").all()
    return render(request, "guia/lista.html", {"guias": guias})

def listar_visitas_guiadas(request):
    visita_guiadas = VisitaGuiada.objects.prefetch_related("guias").all()
    return render(request, "visita_guiada/lista.html", {"visita_guiadas": visita_guiadas})


#Esta vista accede a una exposición de un año concreto y muestra toda su información.
#Usa una relacion reversa al acceder a las obras de cada exposición y a sus artistas.
#Utilizamos "select_related("museo")" para reducir las consultas necesarias al obtener el museo relacionado con cada exposición.
def listar_exposiciones_anyo(request, year):
    exposiciones = Exposicion.objects.filter(fecha_inicio__year=year).select_related("museo").prefetch_related("obras_exposicion", "obras_exposicion__artista").all()
    return render(request, "exposicion/exposicion_anyo.html", {"exposiciones": exposiciones, "year": year})

#Esta vista lista todas las obras de un artista y una exposición concretas.
#Usar un filtro AND y dos parametros en la URL, no necesito hacer un objects.prefetch_related para sacar la informacion del artista y la exposición 
#porque al usar el filtro por artista y exposicion ya filtramos por el artista y exposición específicos, ahorrandonos las consultas adicionales.
#Y en el html el usuario vera tambien la información del artista y su exposición
def listar_obras_artista_exposicion(request, artista, exposicion):
    obras = Obra.objects.filter(artista__nombre_completo=artista, exposicion__titulo=exposicion).all()
    return render(request, "obra/obra_artista_exposicion.html", {"obras": obras, "artista": artista, "exposicion":exposicion})

#Esta vista saca todos los visitantes y sus datos con una edad mayor a una concreta que le pasamos y ordenados alfabéticamente
#Usamos un parametro entero, filtro y gt para sacar las edades superiores. También el order by para ordenar el resultado.
def listar_visitantes_edad(request, edad):
    visitantes = Visitante.objects.select_related("museo").prefetch_related("entradas", "visita_guiada_visitante").filter(edad__gt=edad).order_by("nombre").all()
    temp_alta1 = date(2023, 11, 2)
    temp_alta2 = date(2023, 11, 27)
    return render(request, "visitante/visitante_edad.html", {"visitantes": visitantes, "edad": edad, "temp_alta1":temp_alta1, "temp_alta2":temp_alta2}) 

#Esta vista saca todos los datos de artistas de una nacionalidad concreta. Ordenados por fecha de nacimiento de manera descendente (por eso ponemos el "-" delante "fecha_nacimiento")
#Usamos un filtro y un parametro de tipo str.
def listar_artistas_nacionalidad(request, nacionalidad):
    artistas = Artista.objects.prefetch_related("obras_artista").filter(nacionalidad=nacionalidad).order_by("-fecha_nacimiento").all()
    return render(request, "artista/artista_nacionalidad.html", {"artistas": artistas, "nacionalidad":nacionalidad})

#Esta vista nos muestra todos los datos de los guias que hablen un idioma u otro. Ambos idiomas se pasan en la URL.
#Usamos dos parametros y el filtro OR. Al usar un filtro OR debemos usar Q y | para este tipo de filtros. La Q se usa como condicional y la | indicar que solo se necedita que se cumpla una de las dos condiciones.
#Usamos icontains en el filtro para que el idioma coincida parcialmente, permitiendo búsquedas como "francés" o "inglés" sin distinguir entre mayúsculas, minúsculas o palabras tildadas.
def listar_guias_idiomas(request, idioma1, idioma2):
    guias = Guia.objects.select_related("museo").prefetch_related("visita_guiada_guia").filter(Q(idiomas__icontains=idioma1) | Q(idiomas__icontains=idioma2)).all()
    return render(request, "guia/guia_nacionalidad.html", {"guias": guias, "idioma1":idioma1, "idioma2":idioma2})

#Esa vista muestra todos los datos de los productos junto a la media de su precio
#Usamos aggregate para generar un atributo nuevo, en este caso la media y volcar en el la media del precio total de los productos.
#Para sacar la media usamos la función Avg, que viene de average en ingles, nos permite saber la media aritmética de un conjutno de valores.
def producto_precio_media(request):
    resultado = Producto.objects.aggregate(Avg("precio"))
    media = resultado["precio__avg"]
    producto = Producto.objects.prefetch_related("inventario_producto", "tiendas").all()
    return render(request, "producto/precio_medio.html", {"productos":producto, "media":media})

#Esta vista muestra al primer visitante que hubo en un año concreto, concretamente de 2023 (solo tengo visitantes de ese año, aún así el año se puede cambiar desde la URL)
#Usamos un limit para sacar solo 1 [:1] y con un order by por fecha_visita sacamos al prmer visitante de ese año. Podríamos sacar el último añadiendo un "-" al parametro de "fecha_visita" del order_by
def primer_visitante_2023(request):
    visitantes = Visitante.objects.select_related("museo").prefetch_related("entradas", 
    "visita_guiada_visitante").filter(fecha_visita__year=2023).order_by('fecha_visita')[:1]
    return render(request, "visitante/primer_visitante_2023.html", {"visitantes": visitantes})

#Esta vista muestra los productos que aún no se han vendido en la tienda.
#Para ello lo que hacemos es un filter con la tabla intermedia de inventario, que es la que guarda la fecha de la ultima venta.
#Debemos filtrar por la "fecha_ultima_venta" y no por la cantidad vendida porque de fecha si que tenemos un valor null, compatible con la condición de None
#Podriamos obtener el mismo resultado pero poniendo en el filtro el atributo de "cantidad_vendida" igual a 0, pero no cumpliriá el requisito del trabajo.
#Este filtro nos mostrará los productos que no tienen una ultima fecha de venta, por lo cual, nunca se han vendido.
def productos_sin_vender(request):
    productos = Producto.objects.prefetch_related("inventario_producto", "tiendas").all()
    productos = productos.filter(inventario_producto__fecha_ultima_venta=None)
    return render(request, "producto/productos_sin_vender.html", {"productos": productos})


#Esta vista muetras todos los visitantes cuya edad esta por debajo de la media.
#Usamos la combinación de un filtro y un aggregate, con el aggregate sacamos la media de la edad de los visitantes y lo guardamos en el atributo "edad_media"
#Ahora solo debemos aplicar un filtro a ese atributo de aggregate. Para ello usamos filter el atributo de edad, seguido de lt para indicar los que sean menores a la media, y lo igualamos al atributo de "edad_media"
def visitantes_menor_media(request):
    resultado = Visitante.objects.aggregate(Avg("edad"))
    edad_media = resultado["edad__avg"]
    visitantes = Visitante.objects.select_related("museo").prefetch_related("entradas", 
    "visita_guiada_visitante").filter(edad__lt=edad_media)
    return render(request, "visitante/visitante_menor_media.html", {"visitantes": visitantes, "edad_media": edad_media})



#Aqui vamos a crear lo que corresponda a los formularios.

#Creación de museo.
def museo_create(request):
    if request.method == "POST":
        formulario = MuseoModelForm(request.POST)
        if formulario.is_valid():
            try:
                # Guarda el museo en la base de datos
                formulario.save()
                messages.success(request, "El museo se ha creado correctamente.")
                return redirect("listar_museos")
            except Exception as error:
                print(error)
    else:
        formulario = MuseoModelForm()
          
    return render(request, 'museo/create.html',{"formulario":formulario}) 

#Busqueda avanzada de museo.
def museo_buscar_avanzado(request):

    if len(request.GET) > 0:
        formulario = BusquedaAvanzadaMuseoForm(request.GET)

        if formulario.is_valid():
            
            mensaje_busqueda = "Se ha buscado por los siguientes valores:\n"
            QSmuseos = Museo.objects.all()
            
            nombre_descripcion = formulario.cleaned_data.get('nombre_descripcion')
            ubicacion = formulario.cleaned_data.get('ubicacion')
            fecha_desde = formulario.cleaned_data.get('fecha_desde')
            fecha_hasta = formulario.cleaned_data.get('fecha_hasta')

            # Filtro por texto en nombre o descripción
            if nombre_descripcion:
                QSmuseos = QSmuseos.filter(Q(nombre__icontains=nombre_descripcion) | Q(descripcion__icontains=nombre_descripcion))
                mensaje_busqueda += "Nombre o descripción contienen: "+ nombre_descripcion+"\n"
            
            # Filtro por texto en ubicación 
            if ubicacion:
                QSmuseos = QSmuseos.filter(ubicacion__icontains=ubicacion)
                mensaje_busqueda += "Nombre o descripción contienen:"+ ubicacion+"\n"

            # Filtro por fecha desde
            if fecha_desde:
                QSmuseos = QSmuseos.filter(fecha_fundacion__gte=fecha_desde)
                mensaje_busqueda += "Fecha de fundación mayor o igual a "+str(fecha_desde)+"\n"

            # Filtro por fecha hasta
            if fecha_hasta:
                QSmuseos = QSmuseos.filter(fecha_fundacion__lte=fecha_hasta)
                mensaje_busqueda += "Fecha de fundación menor o igual a " +str(fecha_hasta)+"\n"
                
            museos = QSmuseos.all()

            return render(request, 'museo/lista_busqueda.html',
                {"museos": museos, "mensaje_busqueda": mensaje_busqueda }
            )
    else:
        formulario = BusquedaAvanzadaMuseoForm(None)

    return render(request, 'museo/busqueda_avanzada.html', {"formulario": formulario})

#Editar de museo.
def museo_editar(request,museo_id):
    museo = Museo.objects.get(id=museo_id)
    
    datosFormulario = None
    
    if request.method == "POST":
        datosFormulario = request.POST
    
    
    formulario = MuseoModelForm(datosFormulario,instance = museo)
    
    if (request.method == "POST"):
       
        if formulario.is_valid():
            try:  
                formulario.save()
                messages.success(request, 'Se ha editado el museo'+formulario.cleaned_data.get('nombre')+" correctamente")
                return redirect('listar_museos')  
            except Exception as error:
                print(error)
                
    return render(request, 'museo/actualizar.html',{"formulario":formulario,"museo":museo})

#Eliminar de museo.
def museo_eliminar(request,museo_id):
    museo = Museo.objects.get(id=museo_id)
    try:
        museo.delete()
        messages.success(request, "Se ha elimnado el museo '"+museo.nombre+"' correctamente")
    except Exception as error:
        messages.error(request, "Hubo un error al intentar eliminar el museo.")
        print(error)
    return redirect('listar_museos')


#Creación de exposición.
def exposicion_create(request):
    if request.method == "POST":
        formulario = ExposicionModelForm(request.POST)
        if formulario.is_valid():
            try:
                # Guarda la exposición en la base de datos
                formulario.save()
                messages.success(request, "La exposición se ha creado correctamente.")
                return redirect("listar_exposiciones")
            except Exception as error:
                print(error)
    else:
        formulario = ExposicionModelForm()
          
    return render(request, 'exposicion/create.html',{"formulario":formulario}) 

#Busqueda avanzada de exposición
def exposicion_buscar_avanzado(request):
    if len(request.GET) > 0:
        formulario = BusquedaAvanzadaExposicionForm(request.GET)

        if formulario.is_valid():
            mensaje_busqueda = "Se ha buscado por los siguientes valores:\n"
            QSexposiciones = Exposicion.objects.all()
            
            titulo = formulario.cleaned_data.get('titulo')
            descripcion = formulario.cleaned_data.get('descripcion')
            fecha_desde = formulario.cleaned_data.get('fecha_desde')
            fecha_hasta = formulario.cleaned_data.get('fecha_hasta')
            museo = formulario.cleaned_data.get('museo')

            # Filtro por título y descripción
            if titulo:
                QSexposiciones = QSexposiciones.filter(
                    Q(titulo__icontains=titulo) | 
                    Q(descripcion__icontains=descripcion)
                )
                mensaje_busqueda += "Título o descripción contienen: "+ titulo+"\n"
            
            # Filtro por fecha desde
            if fecha_desde:
                QSexposiciones = QSexposiciones.filter(fecha_inicio__gte=fecha_desde)
                mensaje_busqueda += "Fecha de inicio mayor o igual a "+str(fecha_desde)+"\n"

            # Filtro por fecha hasta
            if fecha_hasta:
                QSexposiciones = QSexposiciones.filter(fecha_fin__lte=fecha_hasta)
                mensaje_busqueda += "Fecha de fin menor o igual a " +str(fecha_hasta)+"\n"

            # Filtro por museo
            if museo:
                QSexposiciones = QSexposiciones.filter(museo=museo)
                mensaje_busqueda += "Museo: "+ museo.nombre +"\n"
                
            exposiciones = QSexposiciones.all()

            return render(request, 'exposicion/lista_busqueda.html',
                {"exposiciones": exposiciones, "mensaje_busqueda": mensaje_busqueda }
            )
    else:
        formulario = BusquedaAvanzadaExposicionForm(None)

    return render(request, 'exposicion/busqueda_avanzada.html', {"formulario": formulario})


#Editar de exposición.
def exposicion_editar(request, exposicion_id):
    exposicion = Exposicion.objects.get(id=exposicion_id)
    
    datosFormulario = None
    
    if request.method == "POST":
        datosFormulario = request.POST
    
    formulario = ExposicionModelForm(datosFormulario, instance=exposicion)
    
    if request.method == "POST":
        if formulario.is_valid():
            try:
                formulario.save()
                messages.success(request, f'Se ha editado la exposición {formulario.cleaned_data.get("titulo")} correctamente.')
                return redirect('listar_exposiciones')  
            except Exception as error:
                print(error)
                
    return render(request, 'exposicion/actualizar.html', {"formulario": formulario, "exposicion": exposicion})

#Eliminar de Exposición
def exposicion_eliminar(request, exposicion_id):
    exposicion = Exposicion.objects.get(id=exposicion_id)
    
    try:
        exposicion.delete()
        messages.success(request, f"Se ha eliminado la exposición '{exposicion.titulo}' correctamente.")
    except Exception as error:
        messages.error(request, "Hubo un error al intentar eliminar la exposición.")
        print(error)
        
    return redirect('listar_exposiciones')

# Creación de artista.
def artista_create(request):
    if request.method == "POST":
        formulario = ArtistaModelForm(request.POST)
        if formulario.is_valid():
            try:
                # Guarda el artista en la base de datos
                formulario.save()
                messages.success(request, "El artista se ha creado correctamente.")
                return redirect("listar_artistas")
            except Exception as error:
                print("Error al guardar:", error)
        else:
            print("Errores del formulario:", formulario.errors)  # Para depuración
    else:
        formulario = ArtistaModelForm()

    return render(request, 'artista/create.html', {"formulario": formulario})

# Búsqueda avanzada de artista
def artista_buscar_avanzado(request):
    if len(request.GET) > 0:
        formulario = BusquedaAvanzadaArtistaForm(request.GET)

        if formulario.is_valid():
            mensaje_busqueda = "Se ha buscado por los siguientes valores:\n"
            QSartistas = Artista.objects.all()
            
            nombre_completo = formulario.cleaned_data.get('nombre_completo')
            fecha_nacimiento_desde = formulario.cleaned_data.get('fecha_nacimiento_desde')
            fecha_nacimiento_hasta = formulario.cleaned_data.get('fecha_nacimiento_hasta')
            nacionalidad = formulario.cleaned_data.get('nacionalidad')
            biografia = formulario.cleaned_data.get('biografia')

            # Filtro por nombre completo
            if nombre_completo:
                QSartistas = QSartistas.filter(nombre_completo__icontains=nombre_completo)
                mensaje_busqueda += "Nombre contiene: " + nombre_completo + "\n"

            # Filtro por fecha de nacimiento desde
            if fecha_nacimiento_desde:
                QSartistas = QSartistas.filter(fecha_nacimiento__gte=fecha_nacimiento_desde)
                mensaje_busqueda += "Fecha de nacimiento desde: " + str(fecha_nacimiento_desde) + "\n"

            # Filtro por fecha de nacimiento hasta
            if fecha_nacimiento_hasta:
                QSartistas = QSartistas.filter(fecha_nacimiento__lte=fecha_nacimiento_hasta)
                mensaje_busqueda += "Fecha de nacimiento hasta: " + str(fecha_nacimiento_hasta) + "\n"

            # Filtro por nacionalidad
            if nacionalidad:
                QSartistas = QSartistas.filter(nacionalidad=nacionalidad)
                mensaje_busqueda += "Nacionalidad: " + nacionalidad + "\n"

            # Filtro por biografía
            if biografia:
                QSartistas = QSartistas.filter(biografia__icontains=biografia)
                mensaje_busqueda += "Biografía contiene: " + biografia + "\n"

            artistas = QSartistas.all()

            return render(request, 'artista/lista_busqueda.html',
                {"artistas": artistas, "mensaje_busqueda": mensaje_busqueda}
            )
    else:
        formulario = BusquedaAvanzadaArtistaForm(None)

    return render(request, 'artista/busqueda_avanzada.html', {"formulario": formulario})


# Editar Artista
def artista_editar(request, artista_id):
    artista = Artista.objects.get(id=artista_id)
    
    datosFormulario = None
    
    if request.method == "POST":
        datosFormulario = request.POST
    
    formulario = ArtistaModelForm(datosFormulario, instance=artista)
    
    if request.method == "POST":
        if formulario.is_valid():
            try:
                formulario.save()
                messages.success(request, f'Se ha editado el artista {formulario.cleaned_data.get("nombre")} correctamente.')
                return redirect('listar_artistas')  
            except Exception as error:
                print(error)
                
    return render(request, 'artista/actualizar.html', {"formulario": formulario, "artista": artista})

# Eliminar Artista
def artista_eliminar(request, artista_id):
    artista = Artista.objects.get(id=artista_id)
    
    try:
        artista.delete()
        messages.success(request, f"Se ha eliminado el artista '{artista.nombre}' correctamente.")
    except Exception as error:
        messages.error(request, "Hubo un error al intentar eliminar el artista.")
        print(error)
        
    return redirect('listar_artistas')

# Creación de obra
def obra_create(request):
    if request.method == "POST":
        formulario = ObraModelForm(request.POST, request.FILES)
        if formulario.is_valid():
            try:
                formulario.save()
                messages.success(request, "La obra se ha creado correctamente.")
                return redirect("listar_obras")  # Cambia esto al nombre de tu lista de obras
            except Exception as error:
                print(error)
                messages.error(request, "Ocurrió un error al crear la obra.")
    else:
        formulario = ObraModelForm()
    
    return render(request, 'obra/create.html', {"formulario": formulario})

# Busqueda avanzada de obra
def obra_buscar_avanzado(request):
    if len(request.GET) > 0:
        formulario = BusquedaAvanzadaObraForm(request.GET)

        if formulario.is_valid():
            mensaje_busqueda = "Se ha buscado por los siguientes valores:\n"
            QSobras = Obra.objects.all()

            titulo = formulario.cleaned_data.get('titulo')
            fecha_creacion_desde = formulario.cleaned_data.get('fecha_creacion_desde')
            fecha_creacion_hasta = formulario.cleaned_data.get('fecha_creacion_hasta')
            tipo = formulario.cleaned_data.get('tipo')
            exposicion = formulario.cleaned_data.get('exposicion')
            artista = formulario.cleaned_data.get('artista')

            # Filtro por título
            if titulo:
                QSobras = QSobras.filter(titulo__icontains=titulo)
                mensaje_busqueda += f"Título contiene: {titulo}\n"

            # Filtro por fecha de creación desde
            if fecha_creacion_desde:
                QSobras = QSobras.filter(fecha_creacion__gte=fecha_creacion_desde)
                mensaje_busqueda += f"Fecha de creación desde: {fecha_creacion_desde}\n"

            # Filtro por fecha de creación hasta
            if fecha_creacion_hasta:
                QSobras = QSobras.filter(fecha_creacion__lte=fecha_creacion_hasta)
                mensaje_busqueda += f"Fecha de creación hasta: {fecha_creacion_hasta}\n"

            # Filtro por tipo
            if tipo:
                QSobras = QSobras.filter(tipo=tipo)
                mensaje_busqueda += f"Tipo: {tipo}\n"

            # Filtro por exposición
            if exposicion:
                QSobras = QSobras.filter(exposicion=exposicion)
                mensaje_busqueda += f"Exposición: {exposicion.titulo}\n"

            # Filtro por artista
            if artista:
                QSobras = QSobras.filter(artista=artista)
                mensaje_busqueda += f"Artista: {artista.nombre_completo}\n"

            obras = QSobras.all()

            return render(request, 'obra/lista_busqueda.html',
                          {"obras": obras, "mensaje_busqueda": mensaje_busqueda})
    else:
        formulario = BusquedaAvanzadaObraForm(None)

    return render(request, 'obra/busqueda_avanzada.html', {"formulario": formulario})


# Editar de obra
def obra_editar(request, obra_id):
    obra = Obra.objects.get(id=obra_id)  # Obtenemos la obra con el id proporcionado

    datosFormulario = None  # Inicializamos el formulario

    if request.method == "POST":
        datosFormulario = request.POST  # Si es POST, obtenemos los datos del formulario

    # Creamos el formulario con los datos del POST y la instancia de la obra a editar
    formulario = ObraModelForm(datosFormulario, instance=obra)

    if request.method == "POST":
        if formulario.is_valid():  # Si el formulario es válido
            try:
                formulario.save()  # Guardamos los cambios
                messages.success(request, f'Se ha editado la obra "{formulario.cleaned_data.get("titulo")}" correctamente.')
                return redirect('listar_obras')  # Redirigimos a la lista de obras
            except Exception as error:
                print(error)
                messages.error(request, 'Hubo un error al intentar editar la obra.')

    return render(request, 'obra/actualizar.html', {"formulario": formulario, "obra": obra})

# Eliminar de obra
def obra_eliminar(request, obra_id):
    obra = Obra.objects.get(id=obra_id)  # Obtenemos la obra con el id proporcionado

    try:
        obra.delete()  # Eliminamos la obra
        messages.success(request, f"Se ha eliminado la obra '{obra.titulo}' correctamente.")
    except Exception as error:
        messages.error(request, "Hubo un error al intentar eliminar la obra.")
        print(error)

    return redirect('listar_obras')  # Redirigimos a la lista de obras después de eliminar

# Creación de guía
def guia_create(request):
    if request.method == "POST":
        formulario = GuiaModelForm(request.POST)
        if formulario.is_valid():
            try:
                # Convertir disponibilidad de texto a booleano
                disponibilidad = formulario.cleaned_data.get('disponibilidad')
                guia = formulario.save(commit=False)
                guia.disponibilidad = disponibilidad == 'Disponible'  
                guia.save() 
                messages.success(request, "El guía se ha creado correctamente.")
                return redirect("listar_guias")
            except Exception as error:
                print("Error al guardar:", error)
        else:
            print("Errores del formulario:", formulario.errors)  # Para depuración
    else:
        formulario = GuiaModelForm()

    return render(request, 'guia/create.html', {"formulario": formulario})

# Búsqueda avanzada de guía
def guia_buscar_avanzado(request):
    if len(request.GET) > 0:
        formulario = BusquedaAvanzadaGuiaForm(request.GET)

        if formulario.is_valid():
            mensaje_busqueda = "Se ha buscado por los siguientes valores:\n"
            QSguias = Guia.objects.all()
            
            nombre = formulario.cleaned_data.get('nombre')
            idiomas = formulario.cleaned_data.get('idiomas')
            especialidad = formulario.cleaned_data.get('especialidad')
            disponibilidad = formulario.cleaned_data.get('disponibilidad')
            museo = formulario.cleaned_data.get('museo')

            # Filtro por nombre
            if nombre:
                QSguias = QSguias.filter(nombre__icontains=nombre)
                mensaje_busqueda += "Nombre contiene: " + nombre + "\n"

            # Filtro por idiomas
            if idiomas:
                idiomas_list = idiomas.split(',')
                QSguias = QSguias.filter(idiomas__in=idiomas_list)
                mensaje_busqueda += "Idiomas contienen: " + ', '.join(idiomas_list) + "\n"

            # Filtro por especialidad
            if especialidad:
                QSguias = QSguias.filter(especialidad__icontains=especialidad)
                mensaje_busqueda += "Especialidad contiene: " + especialidad + "\n"

            # Filtro por disponibilidad
            if disponibilidad is not None:
                QSguias = QSguias.filter(disponibilidad=disponibilidad)
                mensaje_busqueda += "Disponible: " + ("Sí" if disponibilidad else "No") + "\n"

            # Filtro por museo
            if museo:
                QSguias = QSguias.filter(museo=museo)
                mensaje_busqueda += "Museo: " + museo.nombre + "\n"

            guias = QSguias.all()

            return render(request, 'guia/lista_busqueda.html',
                {"guias": guias, "mensaje_busqueda": mensaje_busqueda}
            )
    else:
        formulario = BusquedaAvanzadaGuiaForm(None)

    return render(request, 'guia/busqueda_avanzada.html', {"formulario": formulario})

# Editar Guía
def guia_editar(request, guia_id):
    guia = Obra.objects.get(id=guia_id)
    
    datosFormulario = None

    if request.method == "POST":
        datosFormulario = request.POST

    formulario = GuiaModelForm(datosFormulario, instance=guia)

    if request.method == "POST":
        if formulario.is_valid():
            try:
                formulario.save()
                messages.success(request, f'Se ha editado el guía {formulario.cleaned_data.get("nombre")} correctamente.')
                return redirect('listar_guias')  # Redirige a la lista de guías
            except Exception as error:
                print(error)

    return render(request, 'guia/actualizar.html', {"formulario": formulario, "guia": guia})

# Eliminar Guía
def guia_eliminar(request, guia_id):
    guia = Guia.objects.get(id=guia_id)

    try:
        guia.delete()
        messages.success(request, f"Se ha eliminado el guía '{guia.nombre}' correctamente.")
    except Exception as error:
        messages.error(request, "Hubo un error al intentar eliminar el guía.")
        print(error)

    return redirect('listar_guias')  # Redirige a la lista de guías


# Crear de visita guiada
def visita_guiada_create(request):
    if request.method == "POST":
        formulario = VisitaGuiadaModelForm(request.POST)
        if formulario.is_valid():
            try:
                visita_guiada = formulario.save(commit=False)
                visita_guiada.save()
                messages.success(request, "La visita guiada se ha creado correctamente.")
                return redirect("listar_visitas_guiadas")  # Cambiar según la URL correspondiente
            except Exception as error:
                print("Error al guardar:", error)
        else:
            print("Errores del formulario:", formulario.errors)  # Para depuración
    else:
        formulario = VisitaGuiadaModelForm()

    return render(request, 'visita_guiada/create.html', {"formulario": formulario})

# Búsqueda avanzada de visita guiada
def visita_guiada_buscar_avanzado(request):
    if len(request.GET) > 0:
        formulario = BusquedaAvanzadaVisitaGuiadaForm(request.GET)

        if formulario.is_valid():
            mensaje_busqueda = "Se ha buscado por los siguientes valores:\n"
            QSvisitas_guiadas = VisitaGuiada.objects.all()
            
            nombre_visita_guia = formulario.cleaned_data.get('nombre_visita_guia')
            duracion = formulario.cleaned_data.get('duracion')
            capacidad_maxima = formulario.cleaned_data.get('capacidad_maxima')
            idioma = formulario.cleaned_data.get('idioma')

            # Filtro por nombre de visita guiada
            if nombre_visita_guia:
                QSvisitas_guiadas = QSvisitas_guiadas.filter(nombre_visita_guia__icontains=nombre_visita_guia)
                mensaje_busqueda += "Nombre contiene: " + nombre_visita_guia + "\n"

            # Filtro por duración
            if duracion:
                QSvisitas_guiadas = QSvisitas_guiadas.filter(duracion=duracion)
                mensaje_busqueda += "Duración: " + str(duracion) + "\n"

            # Filtro por capacidad máxima
            if capacidad_maxima:
                QSvisitas_guiadas = QSvisitas_guiadas.filter(capacidad_maxima=capacidad_maxima)
                mensaje_busqueda += "Capacidad máxima: " + str(capacidad_maxima) + "\n"

            # Filtro por idioma
            if idioma:
                QSvisitas_guiadas = QSvisitas_guiadas.filter(idioma=idioma)
                mensaje_busqueda += "Idioma: " + idioma + "\n"

            visitas_guiadas = QSvisitas_guiadas.all()

            return render(request, 'visita_guiada/lista_busqueda.html',
                {"visitas_guiadas": visitas_guiadas, "mensaje_busqueda": mensaje_busqueda}
            )
    else:
        formulario = BusquedaAvanzadaVisitaGuiadaForm(None)

    return render(request, 'visita_guiada/busqueda_avanzada.html', {"formulario": formulario})


# Editar de visita guiada
def visita_guiada_editar(request, visita_guiada_id):
    visita_guiada = VisitaGuiada.objects.get(id=visita_guiada_id)
    
    datosFormulario = None
    
    if request.method == "POST":
        datosFormulario = request.POST
    
    formulario = VisitaGuiadaModelForm(datosFormulario, instance=visita_guiada)
    
    if request.method == "POST":
        if formulario.is_valid():
            try:
                formulario.save()
                messages.success(request, f'Se ha editado la visita guiada {formulario.cleaned_data.get("nombre_visita_guia")} correctamente.')
                return redirect('listar_visitas_guiadas')  
            except Exception as error:
                print(error)
                
    return render(request, 'visita_guiada/actualizar.html', {"formulario": formulario, "visita_guiada": visita_guiada})


#Eliminar de visita guiada
def visita_guiada_eliminar(request, visita_guiada_id):
    visita_guiada = VisitaGuiada.objects.get(id=visita_guiada_id)
    
    try:
        visita_guiada.delete()
        messages.success(request, f"Se ha eliminado la visita guiada '{visita_guiada.nombre_visita_guia}' correctamente.")
    except Exception as error:
        messages.error(request, "Hubo un error al intentar eliminar la visita guiada.")
        print(error)
        
    return redirect('listar_visitas_guiadas')


#Usuarios y Sesiones

def registrar_usuario(request):
    if request.method == 'POST':
        formulario = RegistroForm(request.POST)
        if formulario.is_valid():
            user = formulario.save()
            rol = int(formulario.cleaned_data.get('rol'))
            museo = formulario.cleaned_data.get('museo')
            if(rol == Usuario.VISITANTE):
                grupo = Group.objects.get(name='Visitantes')
                grupo.user_set.add(user)
                visitante = Visitante.objects.create( usuario = user, museo=museo)
                visitante.save()
            elif(rol == Usuario.RESPONSABLE):
                grupo = Group.objects.get(name='Responsables')
                grupo.user_set.add(user)
                responsable = Responsable.objects.create(usuario = user)
                responsable.save()
            
            login(request, user)
            return redirect('index')
    else:
        formulario = RegistroForm()
    return render(request, 'registration/signup.html', {'formulario': formulario})



@permission_required('appmuseo.add_visita')
def visita_crear(request):
    if request.method == 'POST':
        formulario = VisitaForm(request.POST)
        if formulario.is_valid():
            visita = formulario.save(commit=False)  # Crear la instancia sin guardarla en la base de datos todavía
            visita.visitante = Visitante.objects.get(usuario=request.user)  # Asociar el visitante actual
            visita.save()  # Guardar la visita con todos los datos
            return redirect('visita_lista_usuario',usuario_id=request.user.visitante.id)  # Redirige a la página principal o a otra página
    else:
        formulario = VisitaForm()

    return render(request, 'visita/create.html', {'form': formulario})





def visita_lista_usuario(request, usuario_id):
    visitante = Visitante.objects.get(id=usuario_id).get()
    visitas = Visita.objects.select_related("museo")
    visitas = visitas.filter(visitante=visitante.id).all()
    return render(request, 'visita/lista.html', {"visitas_mostrar": visitas, "visitante": visitante})


#Aquí creamos las vistas para cada una de las cuatro páginas de errores que vamos a controlar.

#Este error indica que el servidor no entiende la solicitud del navegador.
def error_400(request,exception=None):
    return render(request, 'errores/400.html',None,None,400)

#Este error indica que el usuario no tiene permisos para acceder a la página.
def error_403(request,exception=None):
    return render(request, 'errores/403.html',None,None,403)

#Este error se produce cuando el servidor no puede encontrar la página solicitada.
def error_404(request,exception=None):
    return render(request, 'errores/404.html',None,None,404)

#Este error ocurre cuando hay un proble interno en el servidor.
def error_500(request,exception=None):
    return render(request, 'errores/500.html',None,None,500)