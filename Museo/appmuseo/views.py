from django.shortcuts import render
from django.db.models import Prefetch
from .models import Museo,Obra,Artista

# Create your views here.
def index(request):
    return render(request, 'index.html')

#    1 - Crear una URL que muestre una lista de todas las obras con sus datos correspondientes.

def listar_obras(request):
    
    obras = (Obra.objects.select_related("exposicion","artista")).all()
    return render(request, "obra/lista.html", {"obras":obras})