from django.urls import path
from .views import inicio, menu, api_pedido, confirmar_pedido_bot

urlpatterns = [
    path("", inicio, name="inicio"),
    path("menu/", menu, name="menu"),

    # API para que el bot lea el pedido
    path(
        "api/pedido/<int:pedido_id>/",
        api_pedido,
        name="api_pedido"
    ),

    # Endpoint para confirmar pedido desde Telegram
    path(
        "bot/confirmar/<int:pedido_id>/",
        confirmar_pedido_bot,
        name="confirmar_pedido_bot"
    ),
]
