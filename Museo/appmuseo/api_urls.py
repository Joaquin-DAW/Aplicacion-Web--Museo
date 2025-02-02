from django.urls import path

from .api_views import *

urlpatterns = [
    path('museos',museo_list),
    path('obras',obra_list),
    path('exposiciones',exposicion_list),
    path('entradas',entrada_list),
    path('artistas',artista_list),
]