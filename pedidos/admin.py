from django.contrib import admin
from .models import Producto, Pedido, PedidoItem


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria", "precio", "stock", "activo")


class PedidoItemInline(admin.TabularInline):
    model = PedidoItem
    extra = 0
    readonly_fields = ("producto", "cantidad", "precio")


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = (
        "id", "nombre_cliente", "telefono",
        "total", "confirmado", "entregado", "fecha"
    )
    list_filter = ("confirmado", "entregado")
    inlines = [PedidoItemInline]
    actions = ["marcar_entregado"]

    def marcar_entregado(self, request, queryset):
        queryset.update(entregado=True)

    marcar_entregado.short_description = "🚚 Marcar como entregado"