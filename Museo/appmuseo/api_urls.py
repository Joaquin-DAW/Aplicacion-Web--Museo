from django.urls import path

from .api_views import *

urlpatterns = [
    path('museos',museo_list),
    path('obras',obra_list),
    path('exposiciones',exposicion_list),
    path('entradas',entrada_list),
    path('museos/busqueda_simple/', museo_buscar_simple),
    path('museos/busqueda_avanzada/', museo_buscar_avanzada),
    path('obras/busqueda_avanzada/', obra_buscar_avanzada),
    path('exposiciones/busqueda_avanzada/', exposicion_buscar_avanzada),
    path('entradas/busqueda_avanzada/', entrada_buscar_avanzada),
]