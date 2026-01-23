from django.urls import path
from .views import (
    inicio, menu, api_pedido,
    confirmar_pedido_bot, guardar_chat_id
)

urlpatterns = [
    path("", inicio),
    path("menu/", menu),

    path("api/pedido/<int:pedido_id>/", api_pedido),

    path("bot/confirmar/<int:pedido_id>/", confirmar_pedido_bot),
    path("bot/guardar-chat/<int:pedido_id>/", guardar_chat_id),
]
