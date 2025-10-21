from django.urls import path
from . import views

urlpatterns = [
    path('', views.comprar_entradas_view, name='comprar_entradas'),
]