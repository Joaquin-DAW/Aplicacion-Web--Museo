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
    path('exposiciones/editar/<int:exposicion_id>', exposicion_editar, name="exposicion_editar"),
    
    path('entradas',entrada_list),
    path('entradas/busqueda_avanzada/', entrada_buscar_avanzada),
]