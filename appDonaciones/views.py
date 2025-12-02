from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q

# --- AGREGADO: Importaciones para enviar correos ---
from django.core.mail import send_mail
from django.conf import settings

# Importar modelos
# --- 'TipoDeAlimento' ELIMINADO ---
from .models import Donaciones, Donante, BajoRecursos, Zoo

# Importar formularios
# --- 'TipoDeAlimentoForm' ELIMINADO ---
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
        
    return render(request, 'template/html/signup.html', {
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
        
    return render(request, 'template/html/signin.html', {'form': form})


def signout(request):
    """Vista para cierre de sesión"""
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('home')


# =============================================
# VISTAS PRINCIPALES (CON LÓGICA DE ROLES)
# =============================================

@login_required
def home(request):
    """
    Página principal que redirige según el rol.
    - Admin (is_staff) ve el dashboard completo.
    - Usuario (not is_staff) ve una vista simple de solicitud.
    """
    if request.user.is_staff:
        # Lógica para el ADMIN: Muestra el Dashboard
        donaciones_count = Donaciones.objects.count()
        donantes_count = Donante.objects.count()
        zonas_count = BajoRecursos.objects.count()
        zoos_count = Zoo.objects.count()
        # --- 'tipos_count' ELIMINADO ---
        
        context = {
            'donaciones_count': donaciones_count,
            'donantes_count': donantes_count,
            'zonas_count': zonas_count,
            'zoos_count': zoos_count,
            # --- 'tipos_count' ELIMINADO ---
        }
        return render(request, 'template/html/home.html', context)
    
    else:
        # Lógica para el USUARIO NORMAL: Muestra una página simple
        return render(request, 'template/html/usuario_home.html')


@login_required 
def vista_solo_para_admin(request):
    """Vista exclusiva para administradores"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('home')

    return render(request, 'template/html/panel_admin_custom.html')


# =============================================
# VISTAS DE DONACIONES
# =============================================

@login_required
def donaciones_list(request):
    """Lista de todas las donaciones (SOLO ADMIN)"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('home')
    
    donaciones = Donaciones.objects.all()
    return render(request, 'template/html/donaciones_list.html', {'donaciones': donaciones})


@login_required
def donaciones_create(request):
    """Crear nueva donación (VISTA PARA USUARIOS NORMALES Y ADMIN)"""
    
    if request.method == 'POST':
        form = DonacionesForm(request.POST)
        if form.is_valid():
            # 1. Guardamos la donación en la base de datos
            donacion = form.save()
            
            # --- INICIO: LÓGICA DE CORREO INTEGRADA ---
            try:
                asunto = f'Confirmación de Donación #{donacion.id_donacion} - Sistema Donaciones'
                
                mensaje = f"""
                Hola {request.user.username},
                
                Tu donación ha sido registrada exitosamente en nuestro sistema.
                
                --- DETALLE DE LA DONACIÓN ---
                ID: {donacion.id_donacion}
                Donante: {donacion.donante}
                Tipo de Alimento: {donacion.tipo_alimento}
                Cantidad: {donacion.cantidad} kg
                Destino: {donacion.destino}
                Fecha de Llegada: {donacion.fecha_llegada}
                
                Gracias por tu aporte a la comunidad.
                """
                
                remitente = settings.EMAIL_HOST_USER
                # Enviamos al correo del usuario (si tiene uno)
                destinatarios = [request.user.email]
                
                if request.user.email: 
                    send_mail(asunto, mensaje, remitente, destinatarios, fail_silently=True)
                    messages.success(request, 'Donación registrada')
                else:
                    messages.success(request, 'Donación registrada')

            except Exception as e:
                print(f"Error enviando correo: {e}")
                messages.warning(request, 'Donación guardada, pero hubo un error al enviar el correo de confirmación.')
            # --- FIN: LÓGICA DE CORREO ---

            return redirect('home')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = DonacionesForm()
    
    return render(request, 'template/html/donaciones_form.html', {
        'form': form, 
        'title': 'Registrar (Solicitar) Donación'
    })


@login_required
def donaciones_update(request, pk):
    """Actualizar donación existente (SOLO ADMIN)"""
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
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = DonacionesForm(instance=donacion)
    
    return render(request, 'template/html/donaciones_form.html', {
        'form': form, 
        'title': 'Editar Donación'
    })


@login_required
def donaciones_delete(request, pk):
    """Eliminar donación (SOLO ADMIN)"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('home')
    
    donacion = get_object_or_404(Donaciones, pk=pk)
    
    if request.method == 'POST':
        donacion.delete()
        messages.success(request, 'Donación eliminada exitosamente.')
        return redirect('donaciones_list')
    
    return render(request, 'template/html/donaciones_confirm_delete.html', {'donacion': donacion})


# =============================================
# VISTAS DE DONANTES (SOLO ADMIN)
# =============================================

@login_required
def donante_list(request):
    """Lista de donantes con filtros y búsqueda (SOLO ADMIN)"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('home')
    
    try:
        donantes = Donante.objects.all().order_by('-fecha_registro')
        
        tipo_filter = request.GET.get('tipo')
        estado_filter = request.GET.get('estado')
        search_query = request.GET.get('search')
        
        if tipo_filter:
            donantes = donantes.filter(tipo_donante=tipo_filter)
        if estado_filter:
            donantes = donantes.filter(estado=estado_filter)
        if search_query:
            donantes = donantes.filter(
                Q(nombre__icontains=search_query) |
                Q(ciudad__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        
        context = {
            'donantes': donantes,
            'tipos_donante': Donante.TIPO_DONANTE_CHOICES, 
            'estados_donante': Donante.ESTADO_DONANTE_CHOICES, 
            'current_tipo': tipo_filter,
            'current_estado': estado_filter,
            'search_query': search_query,
        }
        
        return render(request, 'template/html/donante_list.html', context)
        
    except Exception as e:
        messages.error(request, f'Error al cargar la lista de donantes: {str(e)}')
        return render(request, 'template/html/donante_list.html', {'donantes': []})


@login_required
def donante_create(request):
    """Crear nuevo donante (SOLO ADMIN)"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('home')
    
    if request.method == 'POST':
        form = DonanteForm(request.POST)
        if form.is_valid():
            donante = form.save()
            messages.success(request, f'Donante "{donante.nombre or donante.ciudad}" creado exitosamente.')
            return redirect('donante_list')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = DonanteForm()
    
    return render(request, 'template/html/donante_form.html', {
        'form': form, 
        'title': 'Registrar Nuevo Donante'
    })


@login_required
def donante_update(request, pk):
    """Actualizar donante existente (SOLO ADMIN)"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('home')
    
    donante = get_object_or_404(Donante, pk=pk)
    
    if request.method == 'POST':
        form = DonanteForm(request.POST, instance=donante)
        if form.is_valid():
            donante = form.save()
            messages.success(request, f'Donante "{donante.nombre or donante.ciudad}" actualizado exitosamente.')
            return redirect('donante_list')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = DonanteForm(instance=donante)
    
    return render(request, 'template/html/donante_form.html', {
        'form': form, 
        'title': f'Editar Donante: {donante.nombre or donante.ciudad}',
        'donante': donante
    })


@login_required
def donante_delete(request, pk):
    """Eliminar donante (SOLO ADMIN)"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('home')
    
    donante = get_object_or_404(Donante, pk=pk)
    nombre_donante = donante.nombre or donante.ciudad
    
    if request.method == 'POST':
        donante.delete()
        messages.success(request, f'Donante "{nombre_donante}" eliminado exitosamente.')
        return redirect('donante_list')
    
    donaciones = Donaciones.objects.filter(donante=donante.ciudad)
    total_donaciones = donaciones.count()
    cantidad_total = sum(donacion.cantidad for donacion in donaciones)
    
    return render(request, 'template/html/donante_confirm_delete.html', {
        'donante': donante,
        'total_donaciones': total_donaciones,
        'cantidad_total': cantidad_total
    })


@login_required
def donante_detail(request, pk):
    """Vista detallada del donante con estadísticas (SOLO ADMIN)"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('home')
    
    donante = get_object_or_404(Donante, pk=pk)
    donaciones = Donaciones.objects.filter(donante=donante.ciudad).order_by('-fecha_llegada')
    
    total_donaciones = donaciones.count()
    cantidad_total = sum(donacion.cantidad for donacion in donaciones)
    
    context = {
        'donante': donante,
        'donaciones': donaciones,
        'total_donaciones': total_donaciones,
        'cantidad_total': cantidad_total,
    }
    
    return render(request, 'template/html/donante_detail.html', context)


# =============================================
# VISTAS DE BAJO RECURSOS (SOLO ADMIN)
# =============================================
@login_required
def bajorecursos_list(request):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('home')
    bajorecursos = BajoRecursos.objects.all()
    return render(request, 'template/html/bajorecursos_list.html', {'bajorecursos': bajorecursos})


@login_required
def bajorecursos_create(request):
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('home')
    if request.method == 'POST':
        form = BajoRecursosForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Zona de bajo recursos creada exitosamente.')
            return redirect('bajorecursos_list')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = BajoRecursosForm()
    
    return render(request, 'template/html/bajorecursos_form.html', {
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
            messages.success(request, 'Zona de bajo recursos actualizada exitosamente.')
            return redirect('bajorecursos_list')
    else:
        form = BajoRecursosForm(instance=bajorecursos)
    
    return render(request, 'template/html/bajorecursos_form.html', {
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
        messages.success(request, 'Zona de bajo recursos eliminada exitosamente.')
        return redirect('bajorecursos_list')
    
    return render(request, 'template/html/bajorecursos_confirm_delete.html', {'bajorecursos': bajorecursos})

# =============================================
# VISTAS DE ZOOLÓGICOS (SOLO ADMIN)
# =============================================

@login_required
def zoo_list(request):
    """Lista de zoológicos (SOLO ADMIN)"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('home')
    
    zoos = Zoo.objects.all()
    return render(request, 'template/html/zoo_list.html', {'zoos': zoos})


@login_required
def zoo_create(request):
    """Crear nuevo zoológico (SOLO ADMIN)"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('home')
    
    if request.method == 'POST':
        form = ZooForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Zoológico creado exitosamente.')
            return redirect('zoo_list')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = ZooForm()
    
    return render(request, 'template/html/zoo_form.html', {
        'form': form, 
        'title': 'Crear Zoológico'
    })


@login_required
def zoo_update(request, pk):
    """Actualizar zoológico (SOLO ADMIN)"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('home')
    
    zoo = get_object_or_404(Zoo, pk=pk)
    
    if request.method == 'POST':
        form = ZooForm(request.POST, instance=zoo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Zoológico actualizado exitosamente.')
            return redirect('zoo_list')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = ZooForm(instance=zoo)
    
    return render(request, 'template/html/zoo_form.html', {
        'form': form, 
        'title': 'Editar Zoológico'
    })


@login_required
def zoo_delete(request, pk):
    """Eliminar zoológico (SOLO ADMIN)"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes permisos para acceder a esta página.')
        return redirect('home')
    
    zoo = get_object_or_404(Zoo, pk=pk)
    
    if request.method == 'POST':
        zoo.delete()
        messages.success(request, 'Zoológico eliminado exitosamente.')
        return redirect('zoo_list')
    
    return render(request, 'template/html/zoo_confirm_delete.html', {'zoo': zoo})