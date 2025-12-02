"""
URL configuration for prjDonaciones project.

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
# appDonaciones/urls.py

from django.urls import path
from appDonaciones import views
from django.urls import path, include
from django.contrib import admin
urlpatterns = [
    # URLs para Donaciones
    path('donaciones/', views.donaciones_list, name='donaciones_list'),
    path('donaciones/crear/', views.donaciones_create, name='donaciones_create'),
    path('donaciones/editar/<int:pk>/', views.donaciones_update, name='donaciones_update'),
    path('donaciones/eliminar/<int:pk>/', views.donaciones_delete, name='donaciones_delete'),

    # URLs para Donante
    path('donantes/', views.donante_list, name='donante_list'),
    path('donantes/create/', views.donante_create, name='donante_create'),
    path('donantes/update/<int:pk>/', views.donante_update, name='donante_update'),
    path('donantes/delete/<int:pk>/', views.donante_delete, name='donante_delete'),
    path('donantes/<int:pk>/', views.donante_detail, name='donante_detail'),
    
    # URLs para BajoRecursos
    path('bajorecursos/', views.bajorecursos_list, name='bajorecursos_list'),
    path('bajorecursos/crear/', views.bajorecursos_create, name='bajorecursos_create'),
    path('bajorecursos/editar/<int:pk>/', views.bajorecursos_update, name='bajorecursos_update'),
    path('bajorecursos/eliminar/<int:pk>/', views.bajorecursos_delete, name='bajorecursos_delete'),
    
    # URLs para Zoo
    path('zoos/', views.zoo_list, name='zoo_list'),
    path('zoos/crear/', views.zoo_create, name='zoo_create'),
    path('zoos/editar/<int:pk>/', views.zoo_update, name='zoo_update'),
    path('zoos/eliminar/<int:pk>/', views.zoo_delete, name='zoo_delete'),

    # URL para la página principal
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('signup/', views.signup, name='signup'), # Ruta de registro
    path('signin/', views.signin, name='signin'), # Ruta de inicio de sesión
    path('logout/', views.signout, name='logout'), # Ruta de cierre de sesión


    
]