from django.urls import path, re_path
from .import views


urlpatterns = [
    path('', views.index, name='index'),
    
    #Esta URL esta usando una expresión regular, para crearlas usamos el re_path en lugar de solo path 
    #La r al principio indica que es una expresión regular.
    #El ^ indica donde empieza la URL. 
    #exposiciones/ es el texto con el que debe comenzar la URL.
    #(?P<year>\d{4}) este conjunto es un grupo de captura, una forma de crear una parte especifica dentro de la expresión regular
    #La P indica que estamos creando un nombre, el <year> es el nombre que le damos, el valor que tendra este conjunto de grupo se guardará como "year"
    #La \d representa un número y el {4} indica el número de digitos que tendra, por ejemplo 2023.
    #Por último el /$ nos indica que es el final de la cadena.
    #Resumiendo, esta URL debe empezar con "exposiciones/"" despues un número de cuatro cifras y acabar con /
    re_path(r"^exposiciones/(?P<year>\d{4})/$", views.listar_exposiciones_anyo, name="exposiciones_por_anyo"),
    
    
    path('obras/<str:artista>/<str:exposicion>/',views.listar_obras_artista_exposicion, name='obras_por_artista_exposicion'),
    path('visitantes/<int:edad>/',views.listar_visitantes_edad, name='visitantes_edad'),
    path('artistas/<str:nacionalidad>/',views.listar_artistas_nacionalidad, name='artistas_nacionalidad'),
    path('guias/<str:idioma1>/<str:idioma2>/',views.listar_guias_idiomas, name='guias_idiomas'),
    path('producto',views.producto_precio_media, name='media_precio'),
    path('visitante',views.primer_visitante_2023, name='primer_visitante_2023'),
    path('producto_sin_vender',views.productos_sin_vender, name='productos_sin_vender'),
    path('visitantes_media',views.visitantes_menor_media, name='visitantes_menor_media'),
    
    path('museos/',views.listar_museos, name='listar_museos'),
    path('museo/create/',views.museo_create,name='museo_create'),
    path('museo/buscar_avanzado/',views.museo_buscar_avanzado,name='museo_buscar_avanzado'),
    path('museo/editar/<int:museo_id>',views.museo_editar,name='museo_editar'),
    path('museo/eliminar/<int:museo_id>/', views.museo_eliminar, name='museo_eliminar'),
    
    path('exposicion/',views.listar_exposiciones,name='listar_exposiciones'),
    path('exposicion/create/',views.exposicion_create,name='exposicion_create'),
    path('exposicion/buscar_avanzado/', views.exposicion_buscar_avanzado, name='exposicion_buscar_avanzado'),
    path('exposicion/editar/<int:exposicion_id>', views.exposicion_editar, name='exposicion_editar'),
    path('exposicion/eliminar/<int:exposicion_id>/', views.exposicion_eliminar, name='exposicion_eliminar'),
    
    path('artista/',views.listar_artistas,name='listar_artistas'),
    path('artista/create/',views.artista_create,name='artista_create'),
    path('artista/buscar_avanzado/', views.artista_buscar_avanzado, name='artista_buscar_avanzado'),
    path('artista/editar/<int:artista_id>', views.artista_editar, name='artista_editar'),
    path('artista/eliminar/<int:artista_id>/', views.artista_eliminar, name='artista_eliminar'),


]