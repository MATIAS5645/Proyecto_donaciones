from django import forms
from django.core.exceptions import ValidationError
from .models import Donaciones, Donante, BajoRecursos, Zoo, TipoDeAlimento
import datetime

# --- IMPORTACIONES PARA RECAPTCHA ---
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox

class DonanteForm(forms.ModelForm):
    # (Este formulario se mantiene igual)
    TIPOS_DONANTE = [
        ('', 'Seleccione tipo de donante...'),
        ('individual', 'Individual'),
        ('empresa', 'Empresa'),
        ('organizacion', 'Organización'),
        ('institucion', 'Institución'),
    ]
    ESTADOS_DONANTE = [
        ('', 'Seleccione estado...'),
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('suspendido', 'Suspendido'),
    ]
    tipo_donante = forms.ChoiceField(
        choices=TIPOS_DONANTE,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Tipo de Donante'
    )
    estado = forms.ChoiceField(
        choices=ESTADOS_DONANTE,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label='Estado'
    )
    class Meta:
        model = Donante
        fields = ['nombre', 'tipo_donante', 'ciudad', 'direccion', 'telefono', 'email', 'estado', 'notas']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre completo o razón social'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ciudad del donante'}),
            'direccion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Dirección completa', 'rows': 3}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número de teléfono'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Información adicional sobre el donante', 'rows': 4}),
        }
        labels = {
            'nombre': 'Nombre/Razón Social', 'ciudad': 'Ciudad', 'direccion': 'Dirección',
            'telefono': 'Teléfono', 'email': 'Correo Electrónico', 'notas': 'Notas Adicionales',
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        if telefono and not telefono.replace(' ', '').replace('-', '').replace('+', '').isdigit():
            raise ValidationError("El teléfono debe contener solo números y caracteres válidos.")
        return telefono
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            donantes_con_email = Donante.objects.filter(email=email)
            if self.instance and self.instance.pk:
                donantes_con_email = donantes_con_email.exclude(pk=self.instance.pk)
            if donantes_con_email.exists():
                raise ValidationError("Este correo electrónico ya está registrado para otro donante.")
        return email

class TipoDeAlimentoForm(forms.ModelForm):
    # (Este formulario se mantiene igual)
    PERECIBLE_CHOICES = [('', 'Seleccione...'), ('0', 'No'), ('1', 'Sí')]
    ESTADO_CHOICES = [('', 'Seleccione...'), ('1', 'Bueno'), ('2', 'Regular'), ('3', 'Malo')]
    perecible = forms.ChoiceField(
        choices=PERECIBLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Es Perecible"
    )
    no_perecibles = forms.ChoiceField(
        choices=PERECIBLE_CHOICES, 
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Es No Perecible"
    )
    estado = forms.ChoiceField(
        choices=ESTADO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Estado del Alimento"
    )
    class Meta:
        model = TipoDeAlimento
        fields = ['perecible', 'no_perecibles', 'estado', 'fecha_caducidad']
        widgets = {
            'fecha_caducidad': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
        labels = {'fecha_caducidad': 'Fecha de Caducidad'}
    def clean_perecible(self):
        perecible = self.cleaned_data.get('perecible')
        if not perecible: raise ValidationError("Debe seleccionar si es perecible o no")
        return perecible 
    def clean_no_perecibles(self):
        no_perecibles = self.cleaned_data.get('no_perecibles')
        if not no_perecibles: raise ValidationError("Debe seleccionar si es no perecible o no")
        return no_perecibles 
    def clean_estado(self):
        estado = self.cleaned_data.get('estado')
        if not estado: raise ValidationError("Debe seleccionar el estado del alimento")
        return estado 
    def clean_fecha_caducidad(self):
        fecha_caducidad = self.cleaned_data.get('fecha_caducidad')
        if fecha_caducidad and fecha_caducidad < datetime.date.today():
             raise ValidationError("La fecha de caducidad no puede ser una fecha pasada.")
        return fecha_caducidad
    def clean(self):
        cleaned_data = super().clean()
        perecible = cleaned_data.get('perecible') 
        no_perecibles = cleaned_data.get('no_perecibles')
        if perecible and no_perecibles:
            if perecible == '1' and no_perecibles == '1':
                raise ValidationError("Un alimento no puede ser perecible y no perecible al mismo tiempo.")
            elif perecible == '0' and no_perecibles == '0':
                raise ValidationError("Un alimento debe ser perecible o no perecible.")
        return cleaned_data

class BajoRecursosForm(forms.ModelForm):
    # (Este formulario se mantiene igual, con la corrección de SQLite)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        ciudades_qs = Donante.objects.order_by('ciudad').values_list('ciudad', flat=True).distinct()
        ciudad_choices = [('', 'Seleccione una ciudad')] + [(ciudad, ciudad) for ciudad in ciudades_qs]
        donaciones = Donaciones.objects.all()
        donacion_choices = [('', 'Seleccione una donación')] + [
            (donacion.id_donacion, f"Donación #{donacion.id_donacion} - {donacion.donante}") 
            for donacion in donaciones
        ]
        self.fields['ciudad'] = forms.ChoiceField(
            choices=ciudad_choices, widget=forms.Select(attrs={'class': 'form-control'}), required=True
        )
        self.fields['donacion'] = forms.ChoiceField(
            choices=donacion_choices, widget=forms.Select(attrs={'class': 'form-control'}), required=True
        )
    class Meta:
        model = BajoRecursos
        fields = ['ciudad', 'donacion']
    def clean_ciudad(self):
        ciudad = self.cleaned_data.get('ciudad')
        if not ciudad: raise ValidationError("Debe seleccionar una ciudad")
        return ciudad
    def clean_donacion(self):
        donacion_id = self.cleaned_data.get('donacion')
        if not donacion_id: raise ValidationError("Debe seleccionar una donación")
        try:
            return int(donacion_id)
        except ValueError:
            raise ValidationError("Donación no válida")

class ZooForm(forms.ModelForm):
    # (Este formulario se mantiene igual)
    TIPO_ANIMAL_CHOICES = [
        ('', 'Seleccione tipo de animal...'), (1, 'Mamíferos'), (2, 'Aves'),
        (3, 'Reptiles'), (4, 'Anfibios'),
    ]
    tipo_animal = forms.ChoiceField(
        choices=TIPO_ANIMAL_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}), required=True
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        donaciones = Donaciones.objects.all()
        donacion_choices = [('', 'Seleccione una donación')] + [
            (donacion.id_donacion, f"Donación #{donacion.id_donacion} - {donacion.donante}") 
            for donacion in donaciones
        ]
        self.fields['donacion'] = forms.ChoiceField(
            choices=donacion_choices, widget=forms.Select(attrs={'class': 'form-control'}), required=True
        )
    class Meta:
        model = Zoo
        fields = ['animales', 'trabajadores', 'tipo_animal', 'donacion']
        widgets = {
            'animales': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Especies de animales'}),
            'trabajadores': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombres de trabajadores'}),
        }
    def clean_animales(self):
        animales = self.cleaned_data.get('animales')
        if not animales or animales.strip() == '': raise ValidationError("El campo animales no puede estar vacío")
        return animales.strip()
    def clean_trabajadores(self):
        trabajadores = self.cleaned_data.get('trabajadores')
        if not trabajadores or trabajadores.strip() == '': raise ValidationError("El campo trabajadores no puede estar vacío")
        return trabajadores.strip()
    def clean_tipo_animal(self):
        tipo_animal = self.cleaned_data.get('tipo_animal')
        if not tipo_animal: raise ValidationError("Debe seleccionar un tipo de animal")
        return int(tipo_animal)
    def clean_donacion(self):
        donacion_id = self.cleaned_data.get('donacion')
        if not donacion_id: raise ValidationError("Debe seleccionar una donación")
        try:
            return int(donacion_id)
        except ValueError:
            raise ValidationError("Donación no válida")

# ===================================================================
# FORMULARIO 'DonacionesForm' CON RECAPTCHA
# ===================================================================
class DonacionesForm(forms.ModelForm):
    
    TIPOS_ALIMENTO = [
        ('', 'Selecciona un tipo'),
        ('Frutas y Verduras', 'Frutas y Verduras'),
        ('Carnes', 'Carnes'),
        ('Granos y Cereales', 'Granos y Cereales'),
        ('Alimento no perecible', 'Alimento no perecible'),
        ('Lácteos', 'Lácteos'),
    ]
    
    DESTINO_CHOICES = [
        ('', 'Seleccione destino...'),
        ('Bajo Recursos', 'Bajo Recursos'),
        ('Zoológico', 'Zoológico'),
    ]
    
    donante = forms.ChoiceField(
        choices=[], 
        widget=forms.Select(attrs={'class': 'form-control'}), 
        required=True
    )
    
    tipo_alimento = forms.ChoiceField(
        choices=TIPOS_ALIMENTO, 
        widget=forms.Select(attrs={'class': 'form-control'}), 
        required=True
    )
    
    destino = forms.ChoiceField(
        choices=DESTINO_CHOICES, 
        widget=forms.Select(attrs={'class': 'form-control'}), 
        required=True
    )

    # --- CAMPO CAPTCHA AÑADIDO ---
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)
    # -----------------------------
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cargar_opciones_donantes()
    
    def _cargar_opciones_donantes(self):
        try:
            # 1. Ordenar por nombre para que sea fácil de encontrar
            donantes = Donante.objects.all().order_by('nombre')
            
            # 2. Cambiar la etiqueta por defecto
            choices = [('', 'Seleccione un donante...')]
            
            for donante in donantes:
                # 3. Usar el nombre para la etiqueta (display)
                display_name = donante.nombre
                # Si el nombre está vacío, usar la ciudad como alternativa
                if not display_name:
                    display_name = f"{donante.ciudad} (Sin Nombre)"
                
                # El valor es el ID, pero la etiqueta es el NOMBRE
                choices.append((donante.id_donante, display_name))
            
            self.fields['donante'].choices = choices
        except Exception as e:
            self.fields['donante'].choices = [('', 'Error cargando donantes')]
    
    class Meta:
        model = Donaciones
        fields = ['donante', 'cantidad', 'fecha_llegada', 'tipo_alimento', 'destino']
        widgets = {
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cantidad en kg', 'min': '1'}),
            'fecha_llegada': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def clean_donante(self):
        # Esta función recibe el ID del donante (ej. 1)
        donante_id = self.cleaned_data.get('donante')
        if not donante_id:
            raise ValidationError("Debe seleccionar un donante")
        try:
            donante = Donante.objects.get(id_donante=int(donante_id))
            # 2. Devuelve la CIUDAD (ya que tu modelo Donaciones espera un CharField)
            return donante.ciudad
        except (Donante.DoesNotExist, ValueError):
            raise ValidationError("Donante no válido")

    def clean_tipo_alimento(self):
        tipo_alimento = self.cleaned_data.get('tipo_alimento')
        if not tipo_alimento:
            raise ValidationError("Debe seleccionar un tipo de alimento")
        return tipo_alimento

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad is None:
            raise ValidationError("La cantidad es requerida")
        if cantidad < 1:
            raise ValidationError("La cantidad debe ser al menos 1 kg")
        return cantidad

    def clean_destino(self):
        destino = self.cleaned_data.get('destino')
        if not destino:
            raise ValidationError("Debe seleccionar un destino")
        return destino 

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data