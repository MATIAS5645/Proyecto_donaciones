from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings

from .models import Donaciones, Donante, BajoRecursos, Zoo
from .forms import DonacionesForm, DonanteForm, BajoRecursosForm, ZooForm


# =============================================
# VISTAS DE AUTENTICACIÓN
# =============================================

@login_required 
def signup(request):
    """Vista para registro de nuevos usuarios (SOLO ADMIN)"""
    
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('home')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        
        if form.is_valid():
            user = form.save()
            try:
                grupo_usuario = Group.objects.get(name='Usuario')
                user.groups.add(grupo_usuario)
            except Group.DoesNotExist:
                messages.error(request, 'Error: El rol "Usuario" no existe. Contacta al administrador.')
                user.delete()
                return redirect('signup')

            messages.success(request, f'¡Cuenta de usuario para "{user.username}" creada con éxito!')
            return redirect('home')
        else:
            messages.error(request, 'Hubo un error en el registro. Por favor, revisa los datos.')
    else: 
        form = UserCreationForm()
    
    # CORRECCIÓN: 'html/...' en lugar de 'template/html/...'
    return render(request, 'html/signup.html', {
        'form': form,
        'title': 'Crear Nuevo Usuario'
    })


def signin(request):
    """Vista para inicio de sesión"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido de nuevo, {username}!')
                return redirect('home')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else: 
        form = AuthenticationForm()
        
    # CORRECCIÓN: 'html/...' en lugar de 'template/html/...'
    return render(request, 'html/signin.html', {'form': form})


def signout(request):
    """Vista para cierre de sesión"""
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('home')


# =============================================
# VISTAS PRINCIPALES
# =============================================

@login_required
def home(request):
    if request.user.is_staff:
        donaciones_count = Donaciones.objects.count()
        donantes_count = Donante.objects.count()
        zonas_count = BajoRecursos.objects.count()
        zoos_count = Zoo.objects.count()
        
        context = {
            'donaciones_count': donaciones_count,
            'donantes_count': donantes_count,
            'zonas_count': zonas_count,
            'zoos_count': zoos_count,
        }
        # CORRECCIÓN: 'html/...'
        return render(request, 'html/home.html', context)
    
    else:
        # CORRECCIÓN: 'html/...'
        return render(request, 'html/usuario_home.html')


@login_required 
def vista_solo_para_admin(request):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('home')

    # CORRECCIÓN: 'html/...'
    return render(request, 'html/panel_admin_custom.html')


# =============================================
# VISTAS DE DONACIONES
# =============================================

@login_required
def donaciones_list(request):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('home')
    
    donaciones = Donaciones.objects.all()
    # CORRECCIÓN: 'html/...'
    return render(request, 'html/donaciones_list.html', {'donaciones': donaciones})


@login_required
def donaciones_create(request):
    if request.method == 'POST':
        form = DonacionesForm(request.POST)
        if form.is_valid():
            donacion = form.save()
            
            # Lógica de correo
            try:
                asunto = f'Confirmación de Donación #{donacion.id_donacion} - Sistema Donaciones'
                mensaje = f"""Hola {request.user.username}, ... (Resumen) ..."""
                remitente = settings.EMAIL_HOST_USER
                destinatarios = [request.user.email]
                
                if request.user.email:
                    send_mail(asunto, mensaje, remitente, destinatarios, fail_silently=True)
                    messages.success(request, 'Donación registrada y correo enviado.')
                else:
                    messages.success(request, 'Donación registrada (Sin email).')
            except Exception as e:
                print(f"Error correo: {e}")
                messages.warning(request, 'Donación guardada, error al enviar correo.')

            return redirect('home')
        else:
            messages.error(request, 'Por favor corrige los errores.')
    else:
        form = DonacionesForm()
    
    # CORRECCIÓN: 'html/...'
    return render(request, 'html/donaciones_form.html', {
        'form': form, 
        'title': 'Registrar (Solicitar) Donación'
    })


@login_required
def donaciones_update(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('home')
    
    donacion = get_object_or_404(Donaciones, pk=pk)
    
    if request.method == 'POST':
        form = DonacionesForm(request.POST, instance=donacion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Donación actualizada exitosamente.')
            return redirect('donaciones_list')
        else:
            messages.error(request, 'Corregir errores.')
    else:
        form = DonacionesForm(instance=donacion)
    
    # CORRECCIÓN: 'html/...'
    return render(request, 'html/donaciones_form.html', {
        'form': form, 
        'title': 'Editar Donación'
    })


@login_required
def donaciones_delete(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('home')
    
    donacion = get_object_or_404(Donaciones, pk=pk)
    
    if request.method == 'POST':
        donacion.delete()
        messages.success(request, 'Donación eliminada.')
        return redirect('donaciones_list')
    
    # CORRECCIÓN: 'html/...'
    return render(request, 'html/donaciones_confirm_delete.html', {'donacion': donacion})


# =============================================
# VISTAS DE DONANTES
# =============================================

@login_required
def donante_list(request):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('home')
    
    try:
        donantes = Donante.objects.all().order_by('-fecha_registro')
        # ... lógica de filtros ...
        context = {
            'donantes': donantes,
            'tipos_donante': Donante.TIPO_DONANTE_CHOICES, 
            'estados_donante': Donante.ESTADO_DONANTE_CHOICES, 
            # ...
        }
        # CORRECCIÓN: 'html/...'
        return render(request, 'html/donante_list.html', context)
        
    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return render(request, 'html/donante_list.html', {'donantes': []})


@login_required
def donante_create(request):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('home')
    
    if request.method == 'POST':
        form = DonanteForm(request.POST)
        if form.is_valid():
            donante = form.save()
            messages.success(request, 'Donante creado.')
            return redirect('donante_list')
        else:
            messages.error(request, 'Errores en formulario.')
    else:
        form = DonanteForm()
    
    # CORRECCIÓN: 'html/...'
    return render(request, 'html/donante_form.html', {
        'form': form, 
        'title': 'Registrar Nuevo Donante'
    })


@login_required
def donante_update(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('home')
    
    donante = get_object_or_404(Donante, pk=pk)
    
    if request.method == 'POST':
        form = DonanteForm(request.POST, instance=donante)
        if form.is_valid():
            donante = form.save()
            messages.success(request, 'Donante actualizado.')
            return redirect('donante_list')
        else:
            messages.error(request, 'Errores en formulario.')
    else:
        form = DonanteForm(instance=donante)
    
    # CORRECCIÓN: 'html/...'
    return render(request, 'html/donante_form.html', {
        'form': form, 
        'title': f'Editar Donante: {donante.nombre or donante.ciudad}',
        'donante': donante
    })


@login_required
def donante_delete(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('home')
    
    donante = get_object_or_404(Donante, pk=pk)
    
    if request.method == 'POST':
        donante.delete()
        messages.success(request, 'Donante eliminado.')
        return redirect('donante_list')
    
    # ... lógica extra ...
    return render(request, 'html/donante_confirm_delete.html', {'donante': donante}) # CORRECCIÓN


@login_required
def donante_detail(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('home')
    
    donante = get_object_or_404(Donante, pk=pk)
    donaciones = Donaciones.objects.filter(donante=donante.ciudad).order_by('-fecha_llegada')
    
    context = {
        'donante': donante,
        'donaciones': donaciones,
        # ...
    }
    # CORRECCIÓN: 'html/...'
    return render(request, 'html/donante_detail.html', context)


# =============================================
# VISTAS DE BAJO RECURSOS
# =============================================
@login_required
def bajorecursos_list(request):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('home')
    bajorecursos = BajoRecursos.objects.all()
    # CORRECCIÓN: 'html/...'
    return render(request, 'html/bajorecursos_list.html', {'bajorecursos': bajorecursos})


@login_required
def bajorecursos_create(request):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('home')
    if request.method == 'POST':
        form = BajoRecursosForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Zona creada.')
            return redirect('bajorecursos_list')
        else:
            messages.error(request, 'Errores en formulario.')
    else:
        form = BajoRecursosForm()
    
    # CORRECCIÓN: 'html/...'
    return render(request, 'html/bajorecursos_form.html', {
        'form': form, 
        'title': 'Crear Zona de Bajo Recursos'
    })


@login_required
def bajorecursos_update(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('home')
    bajorecursos = get_object_or_404(BajoRecursos, pk=pk)
    if request.method == 'POST':
        form = BajoRecursosForm(request.POST, instance=bajorecursos)
        if form.is_valid():
            form.save()
            messages.success(request, 'Zona actualizada.')
            return redirect('bajorecursos_list')
    else:
        form = BajoRecursosForm(instance=bajorecursos)
    
    # CORRECCIÓN: 'html/...'
    return render(request, 'html/bajorecursos_form.html', {
        'form': form, 
        'title': 'Editar Zona de Bajo Recursos'
    })


@login_required
def bajorecursos_delete(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('home')
    bajorecursos = get_object_or_404(BajoRecursos, pk=pk)
    if request.method == 'POST':
        bajorecursos.delete()
        messages.success(request, 'Zona eliminada.')
        return redirect('bajorecursos_list')
    
    # CORRECCIÓN: 'html/...'
    return render(request, 'html/bajorecursos_confirm_delete.html', {'bajorecursos': bajorecursos})

# =============================================
# VISTAS DE ZOOLÓGICOS
# =============================================

@login_required
def zoo_list(request):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('home')
    
    zoos = Zoo.objects.all()
    # CORRECCIÓN: 'html/...'
    return render(request, 'html/zoo_list.html', {'zoos': zoos})


@login_required
def zoo_create(request):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('home')
    
    if request.method == 'POST':
        form = ZooForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Zoológico creado.')
            return redirect('zoo_list')
        else:
            messages.error(request, 'Errores en formulario.')
    else:
        form = ZooForm()
    
    # CORRECCIÓN: 'html/...'
    return render(request, 'html/zoo_form.html', {
        'form': form, 
        'title': 'Crear Zoológico'
    })


@login_required
def zoo_update(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('home')
    
    zoo = get_object_or_404(Zoo, pk=pk)
    
    if request.method == 'POST':
        form = ZooForm(request.POST, instance=zoo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Zoológico actualizado.')
            return redirect('zoo_list')
        else:
            messages.error(request, 'Errores en formulario.')
    else:
        form = ZooForm(instance=zoo)
    
    # CORRECCIÓN: 'html/...'
    return render(request, 'html/zoo_form.html', {
        'form': form, 
        'title': 'Editar Zoológico'
    })


@login_required
def zoo_delete(request, pk):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('home')
    
    zoo = get_object_or_404(Zoo, pk=pk)
    
    if request.method == 'POST':
        zoo.delete()
        messages.success(request, 'Zoológico eliminado.')
        return redirect('zoo_list')
    
    # CORRECCIÓN: 'html/...'
    return render(request, 'html/zoo_confirm_delete.html', {'zoo': zoo})