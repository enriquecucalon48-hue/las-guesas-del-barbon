from django.shortcuts import render
from django.http import JsonResponse
from .models import Producto, Pedido, PedidoItem


# =========================
# VISTAS WEB
# =========================

def inicio(request):
    return render(request, "inicio.html")


def menu(request):
    productos = Producto.objects.filter(activo=True)

    hamburguesas = productos.filter(categoria="hamburguesa")
    extras = productos.filter(categoria="extra")
    papas = productos.filter(categoria="papa")
    bebidas = productos.filter(categoria="bebida")

    telegram_link = None
    error = None

    if request.method == "POST":
        nombre_cliente = request.POST.get("nombre_cliente", "").strip()
        telefono = request.POST.get("telefono", "").strip()

        if not nombre_cliente or not telefono:
            error = "Debes ingresar tu nombre y teléfono"
        else:
            total = 0
            items = []

            # Calcular total y guardar items
            for producto in productos:
                cantidad = int(request.POST.get(f"cantidad_{producto.id}", 0))

                if cantidad > 0:
                    subtotal = producto.precio * cantidad
                    total += subtotal

                    items.append({
                        "producto": producto,
                        "cantidad": cantidad,
                        "precio": producto.precio,
                    })

            if total == 0:
                error = "Debes seleccionar al menos un producto"
            else:
                # Crear pedido
                pedido = Pedido.objects.create(
                    nombre_cliente=nombre_cliente,
                    telefono=telefono,
                    total=total
                )

                # Crear items del pedido
                for item in items:
                    PedidoItem.objects.create(
                        pedido=pedido,
                        producto=item["producto"],
                        cantidad=item["cantidad"],
                        precio=item["precio"]
                    )

                # Link al bot de Telegram
                telegram_link = (
                    f"https://t.me/Las_guesas_del_BarbonBot?start=pedido_{pedido.id}"
                )

    context = {
        "hamburguesas": hamburguesas,
        "extras": extras,
        "papas": papas,
        "bebidas": bebidas,
        "telegram_link": telegram_link,
        "error": error,
    }

    return render(request, "menu.html", context)


# =========================
# CONFIRMAR PEDIDO DESDE TELEGRAM
# =========================

def confirmar_pedido_bot(request, pedido_id):
    try:
        pedido = Pedido.objects.get(id=pedido_id)
        pedido.confirmado = True
        pedido.save()

        return JsonResponse({
            "ok": True,
            "mensaje": "Pedido confirmado"
        })

    except Pedido.DoesNotExist:
        return JsonResponse(
            {"error": "Pedido no encontrado"},
            status=404
        )



# =========================
# API PARA EL BOT
# =========================

def api_pedido(request, pedido_id):
    """
    Endpoint para que el bot lea un pedido
    URL: /api/pedido/<id>/
    """
    try:
        pedido = Pedido.objects.get(id=pedido_id)
    except Pedido.DoesNotExist:
        return JsonResponse({"error": "Pedido no encontrado"}, status=404)

    items = [
        {
            "producto": item.producto.nombre,
            "cantidad": item.cantidad,
            "precio": float(item.precio),
            "subtotal": float(item.cantidad * item.precio),
        }
        for item in PedidoItem.objects.filter(pedido=pedido)
    ]

    data = {
        "id": pedido.id,
        "nombre": pedido.nombre_cliente,
        "telefono": pedido.telefono,
        "total": float(pedido.total),
        "items": items,
        "confirmado": pedido.confirmado,
        "entregado": pedido.entregado,
    }

    return JsonResponse(data)
