"""
URL configuration for Conf project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from FubukiApp import views
from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path
from FubukiApp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('productos.html', views.productos, name='productos'),
    path('promociones.html', views.promociones, name='promociones'),
    path('resenas.html', views.resenas, name='resenas'),
    path('buzon_pedidos_sugerencias.html', views.buzon_pedidos_sugerencias, name='buzon_pedidos_sugerencias'),
    path('agendamiento_especial.html', views.agendamiento_especial, name='agendamiento_especial'),
    path('registrarse.html', views.registrarse, name='registrarse'),
    path('iniciar_sesion.html', views.iniciar_sesion, name='iniciar_sesion'),
    path('cerrar_sesion/', views.cerrar_sesion, name='cerrar_sesion'),
    #Productos
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('crear_producto.html/', views.agregar_producto, name='crear_producto'),
    #Carrito
    path('carrito.html', views.carrito, name='carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_carrito, name='agregar_carrito'),
    path('carrito/actualizar/<int:producto_id>/', views.actualizar_carrito, name='actualizar_carrito'),
    path('carrito/quitar/<int:producto_id>/', views.quitar_carrito, name='quitar_carrito'),

    #Transbank pago
    path('iniciar-pago/', views.iniciar_pago, name='iniciar_pago'),
    path('respuesta-pago/', views.respuesta_pago, name='respuesta_pago'),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
