from django.urls import path

from .api_views import *

urlpatterns = [
    path('museos',museo_list),
    path('museos/busqueda_simple/', museo_buscar_simple),
    path('museos/busqueda_avanzada/', museo_buscar_avanzada),
    path('museos/crear', museo_create),
    path('museos/<int:museo_id>/', museo_obtener),
    path('museos/editar/<int:museo_id>', museo_editar),
    path('museos/editar/nombre/<int:museo_id>', museo_editar_nombre, name='museo_editar_nombre'),
    path('museos/eliminar/<int:museo_id>', museo_eliminar, name='museo_eliminar'),

    path('obras',obra_list),
    path('obras/busqueda_avanzada/', obra_buscar_avanzada),
    
    path('exposiciones',exposicion_list),
    path('exposiciones/busqueda_avanzada/', exposicion_buscar_avanzada),
    path('exposiciones/crear', exposicion_create, name='exposicion_create'),
    path('exposiciones/<int:exposicion_id>/', exposicion_obtener, name='exposicion_obtener'),
    path('exposiciones/editar/<int:exposicion_id>', exposicion_editar, name="exposicion_editar"),
    path('exposiciones/editar/capacidad/<int:exposicion_id>/', exposicion_editar_capacidad, name='exposicion_editar_capacidad'),
    path('exposiciones/eliminar/<int:exposicion_id>', exposicion_eliminar, name='exposicion_eliminar'),
    
    path('entradas',entrada_list),
    path('entradas/busqueda_avanzada/', entrada_buscar_avanzada),
    
    path('guias/', guia_list, name='guia_list'),
    path('visitantes/', visitante_list, name='visitante_list'),
    
    path('visitasguiadas/', visita_guiada_list, name='visita_guiada_list'),
    path('visitasguiadas/crear', visita_guiada_create, name='visita_guiada_create'),
    path('visitasguiadas/<int:visita_id>/', visita_guiada_obtener, name="visita_guiada_obtener"),
    path('visitasguiadas/editar/<int:visita_id>/', visita_guiada_editar, name="visita_guiada_editar"),
    path('visitasguiadas/editar/capacidad/<int:visita_id>/', visita_guiada_editar_capacidad, name='visita_guiada_editar_capacidad'),
    path('visitasguiadas/eliminar/<int:visita_id>', visita_guiada_eliminar, name='visita_guiada_eliminar'),
    
    path('tiendas/', tienda_list, name='tienda_list'),
    
    path('productos/', producto_list, name='producto_list'),
    path('productos/crear', producto_create, name='producto_create'),
    path('productos/<int:producto_id>/', producto_obtener, name="producto_obtener"),
    path('productos/editar/<int:producto_id>/', producto_editar, name="producto_editar"),
    path('productos/editar/stock/<int:producto_id>/', producto_editar_stock, name='producto_editar_stock'),
    path('productos/eliminar/<int:producto_id>', producto_eliminar, name='producto_eliminar'),
]