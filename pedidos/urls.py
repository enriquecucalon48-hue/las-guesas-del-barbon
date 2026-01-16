from django.urls import path
from .views import inicio, menu, api_pedido

urlpatterns = [
    path("", inicio, name="inicio"),
    path("menu/", menu, name="menu"),
    path("api/pedido/<int:pedido_id>/", api_pedido),
]

