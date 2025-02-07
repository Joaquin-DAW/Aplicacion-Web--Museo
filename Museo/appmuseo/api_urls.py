from django.urls import path

from .api_views import *

urlpatterns = [
    path('museos',museo_list),
    path('obras',obra_list),
    path('exposiciones',exposicion_list),
    path('entradas',entrada_list),
    path('museos/busqueda_simple/', museo_buscar_simple),
    path('museos/busqueda_avanzada/', museo_buscar_avanzada),
]