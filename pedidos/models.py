from django.db import models

# Create your models here.
from django.db import models


# -------------------------
# Producto
# -------------------------
class Producto(models.Model):

    CATEGORIAS = (
        ("hamburguesa", "Hamburguesa"),
        ("extra", "Extra"),
        ("papa", "Papa"),
        ("bebida", "Bebida"),
    )

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=6, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} (${self.precio})"


# -------------------------
# Pedido
# -------------------------
class Pedido(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=8, decimal_places=2)
    nombre_cliente = models.CharField(max_length=100, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    confirmado = models.BooleanField(default=False)
    entregado = models.BooleanField(default=False)

    def __str__(self):
        return f"Pedido #{self.id} - ${self.total}"


# -------------------------
# PedidoItem
# -------------------------
class PedidoItem(models.Model):
    pedido = models.ForeignKey(Pedido, related_name="items", on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio = models.DecimalField(max_digits=6, decimal_places=2)

    def subtotal(self):
        return self.cantidad * self.precio

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

direccion = models.TextField(blank=True, null=True)
