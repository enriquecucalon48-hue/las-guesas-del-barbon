from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Producto, Pedido, PedidoItem
import json

# =========================
# WEB
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
        nombre = request.POST.get("nombre_cliente", "").strip()
        telefono = request.POST.get("telefono", "").strip()

        if not nombre or not telefono:
            error = "Debes ingresar nombre y teléfono"
        else:
            total = 0
            items = []

            for producto in productos:
                cantidad = int(request.POST.get(f"cantidad_{producto.id}", 0))
                if cantidad > 0:
                    total += producto.precio * cantidad
                    items.append((producto, cantidad))

            if total == 0:
                error = "Selecciona al menos un producto"
            else:
                pedido = Pedido.objects.create(
                    nombre_cliente=nombre,
                    telefono=telefono,
                    total=total
                )

                for producto, cantidad in items:
                    PedidoItem.objects.create(
                        pedido=pedido,
                        producto=producto,
                        cantidad=cantidad,
                        precio=producto.precio
                    )

                telegram_link = f"https://t.me/Las_guesas_del_BarbonBot?start=pedido_{pedido.id}"

    return render(request, "menu.html", {
        "hamburguesas": hamburguesas,
        "extras": extras,
        "papas": papas,
        "bebidas": bebidas,
        "telegram_link": telegram_link,
        "error": error
    })

# =========================
# BOT ENDPOINTS
# =========================

@csrf_exempt
def guardar_chat_id(request, pedido_id):
    if request.method == "POST":
        pedido = Pedido.objects.get(id=pedido_id)
        data = json.loads(request.body)
        pedido.telegram_chat_id = data["chat_id"]
        pedido.save()
        return JsonResponse({"ok": True})


@csrf_exempt
def confirmar_pedido_bot(request, pedido_id):
    pedido = Pedido.objects.get(id=pedido_id)
    pedido.confirmado = True
    pedido.save()
    return JsonResponse({"ok": True})


def api_pedido(request, pedido_id):
    pedido = Pedido.objects.get(id=pedido_id)

    return JsonResponse({
        "id": pedido.id,
        "nombre": pedido.nombre_cliente,
        "telefono": pedido.telefono,
        "total": float(pedido.total),
        "confirmado": pedido.confirmado,
        "entregado": pedido.entregado,
    })
