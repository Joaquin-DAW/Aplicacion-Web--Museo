from django.urls import path
from .import views


urlpatterns = [
    path('', views.index, name='index'),
    path('obras',views.listar_obras,name='listar_obras'),
]