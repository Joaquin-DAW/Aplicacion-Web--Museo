from django.db import models

# Create your models here.

class Museo(models.Model):
    nombre = models.CharField(max_length=200, unique=True, verbose_name="Nombre del museo") #"Unique" si esta en "true" indica que el valor de ese campo no puede repetirse en la base de datos
                                                                                            #"Verbose_name" nos permite poner un nombre más entendible a nivel humano para el campo         
    ubicacion = models.CharField(max_length=200, blank=True, null=True)                     #"blank" si esta en "true" nos permite que el campo quede vacío en los formularios
                                                                                            #"null" si esta en "true" nos permite que el campo acepte un valor null en la base de datos
    fecha_fundacion = models.DateField(null=True, help_text="Fecha en que se fundo el museo")
                                                                                            #"help_text" aparece un mensaje de ayuda en la interfaz de Djanho o en los formularios, se usa para guiar o dar más información al usuario
    descripcion = models.TextField(blank=True)
    
class Exposicion(models.Model):
    titulo = models.CharField(max_length=150)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(blank=True, null=True)
    descripcion = models.TextField(blank=True)
    capacidad = models.IntegerField(default=60)                                              #"default" nos permite dar un valor por defecto al campo en caso de que no se proporcione ninguno
    museo = models.ForeignKey(Museo, on_delete=models.CASCADE, related_name="exposiciones")  # ManyToOne con Museo

class Artista(models.Model):
    nombre_completo = models.CharField(max_length=150)                                      #"max_length" nos permite definir la longitud máxima que tendra un campo
    fecha_nacimiento = models.DateField(blank=True, null=True)
    biografia = models.TextField()
    nacionalidad = models.CharField(max_length=50, choices=[('espanola', 'Española'), ('italiana', 'Italiana')], blank=True)

class Obra(models.Model):
    titulo = models.CharField(max_length=200, verbose_name="Título de la obra")
    autor = models.CharField(max_length=100, blank=True)
    fecha_creacion = models.DateField(null=True, blank=True)
    tipo = models.CharField(max_length=50, choices=[('pintura', 'Pintura'), ('escultura', 'Escultura')], default='pintura')
                                                                                            #"choices" nos permite definir un conjunto de opciones para seleccionar
    imagen = models.ImageField(upload_to='obras/', blank=True, null=True)                   #"upload_to" nos permite especificar donde se almacenara los archivos subidos de un tipo ImageField o FileField  
    exposicion = models.ForeignKey(Exposicion, on_delete=models.CASCADE, related_name="obras_exposicion")  # ManyToOne con Exposicion
    artista = models.ForeignKey(Artista, on_delete=models.CASCADE, related_name="obras_artista")        # ManyToOne con Artista

class Visitante(models.Model):
    nombre = models.CharField(max_length=100)
    correo_electronico = models.EmailField(unique=True)
    edad = models.IntegerField(null=True)
    fecha_visita = models.DateField()
    museo = models.ForeignKey(Museo, on_delete=models.CASCADE, related_name="visitantes")  # ManyToOne con Museo

class Entrada(models.Model):
    codigo = models.CharField(max_length=10, unique=True)
    precio = models.DecimalField(max_digits=6, decimal_places=2)
    tipo = models.CharField(max_length=50, choices=[('adulto', 'Adulto'), ('nino', 'Niño')])
    fecha_compra = models.DateField(auto_now_add=True)                                      #"auto_now_add" permite establecer la fecha y hora del momento en el que se crea el registro automáticamente
    visitante = models.OneToOneField(Visitante, on_delete=models.CASCADE, related_name="entradas")  # OneToOne con Visitante

class Tienda(models.Model):
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=200, blank=True, null=True)
    horario_apertura = models.TimeField()
    horario_cierre = models.TimeField()
    museo = models.OneToOneField(Museo, on_delete=models.CASCADE, related_name="tienda")  # OneToOne con Museo

class Producto(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    stock = models.IntegerField(default=0)
    tiendas = models.ManyToManyField(Tienda, through='Inventario', related_name="productos_tienda")  # ManyToMany con Tienda a través de Inventario

class Inventario(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name="inventario_producto")
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE, related_name="inventario_tienda")
    cantidad_vendida = models.IntegerField(default=0)
    fecha_ultima_venta = models.DateField(blank=True, null=True)
    stock_inicial = models.IntegerField(default=100)
    ubicacion_almacen = models.CharField(max_length=100, blank=True)

class Guia(models.Model):
    nombre = models.CharField(max_length=100)
    idiomas = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=100, blank=True, null=True)
    disponibilidad = models.BooleanField(default=True)
    museo = models.ForeignKey(Museo, on_delete=models.CASCADE, related_name="guias")  # ManyToOne con Museo

class VisitaGuiada(models.Model):
    duracion = models.DurationField()
    nombre_visita_guia = models.CharField(max_length=100)
    capacidad_maxima = models.IntegerField(default=20)
    idioma = models.CharField(max_length=50, choices=[('espanol', 'Español'), ('ingles', 'Inglés')])
    guias = models.ManyToManyField(Guia, related_name="visita_guiada_guia")  # ManyToMany con Guia
    visitantes = models.ManyToManyField(Visitante, related_name="visita_guiada_visitante")  # ManyToMany con Visitante