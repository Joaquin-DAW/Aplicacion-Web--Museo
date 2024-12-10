from django.shortcuts import render,redirect
from django.db.models import Q, Avg
from datetime import date
from .models import Museo,Obra,Exposicion, Visitante, Artista, Guia, Producto
from .forms import *
from django.contrib import messages

#Index donde podremos acceder a todas las URLs.
def index(request):
    return render(request, 'index.html')

#Esta vista saca todos los datos de museo y accede a todos los modelos relacionados con el mismo para poder sacar información sobre ellos.
#Usamos prefetch_related en lugar de select_releted porque, aunque no haya ninguna relación ManyToMany, son relaciones reversas, ya que la foreingKey 
#se encuentra en los otros modelos.
#Esto tambien estaria usando una relación reversa.
def listar_museos(request):
    museos = (Museo.objects.prefetch_related("exposiciones","visitantes","tienda","guias")).all()
    return render(request, "museo/lista.html", {"museos":museos})

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
                return redirect("museo_lista")
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


def museo_eliminar(request,museo_id):
    museo = Museo.objects.get(id=museo_id)
    try:
        museo.delete()
        messages.success(request, "Se ha elimnado el museo '"+museo.nombre+"' correctamente")
    except Exception as error:
        messages.error(request, "Hubo un error al intentar eliminar el museo.")
        print(error)
    return redirect('listar_museos')

def exposicion_create(request):
    if request.method == "POST":
        formulario = ExposicionModelForm(request.POST)
        if formulario.is_valid():
            try:
                # Guarda la exposición en la base de datos
                formulario.save()
                messages.success(request, "La exposición se ha creado correctamente.")
                return redirect("exposicion_lista")
            except Exception as error:
                print(error)
    else:
        formulario = ExposicionModelForm()
          
    return render(request, 'exposicion/create.html',{"formulario":formulario}) 


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