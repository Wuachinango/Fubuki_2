from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Cliente(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre_usuario = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nombre_usuario


class Resena(models.Model):
    CALIFICACIONES = [(valor, f'{valor} estrellas') for valor in range(1, 6)]

    nombre = models.CharField(max_length=80)
    calificacion = models.PositiveSmallIntegerField(choices=CALIFICACIONES)
    comentario = models.TextField(max_length=700)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f'{self.nombre} — {self.calificacion}/5'
    
class Producto(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(max_length=1000)
    precio = models.IntegerField()
    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)
    stock = models.PositiveIntegerField()
    
    def __str__(self):
        return self.nombre

class SolicitudEspecial(models.Model):
    nombre = models.CharField(max_length=100)
    correo = models.EmailField()
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    fecha_deseada = models.DateField()
    comentarios = models.TextField(max_length=700, blank=True)

    def __str__(self):
        return f'{self.nombre} — {self.producto.nombre} ({self.cantidad} unidades)'


class MensajeBuzon(models.Model):
    TIPOS = [
        ('pedido', 'Pedido'),
        ('sugerencia', 'Sugerencia'),
    ]

    nombre = models.CharField(max_length=100)
    correo = models.EmailField()
    tipo = models.CharField(max_length=12, choices=TIPOS)
    mensaje = models.TextField(max_length=1200)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = 'mensaje del buzón'
        verbose_name_plural = 'mensajes del buzón'

    def __str__(self):
        return f'{self.get_tipo_display()} — {self.nombre}'