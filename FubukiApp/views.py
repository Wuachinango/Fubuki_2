import uuid # para generar los codigos de compra
from django.shortcuts import render
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.db import IntegrityError
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_POST
from .forms import MensajeBuzonForm, ResenaForm, SolicitudEspecialForm, ProductoForm
from .models import Cliente, Resena, Producto, MensajeBuzon
from django.views.decorators.csrf import csrf_exempt
from transbank.common.integration_commerce_codes import IntegrationCommerceCodes
from transbank.common.integration_api_keys import IntegrationApiKeys
from transbank.common.integration_type import IntegrationType
from transbank.common.options import WebpayOptions
from transbank.webpay.webpay_plus.transaction import Transaction
from django.contrib.auth.decorators import login_required 


# Create your views here.
def index(request):
    cliente_actual = None
    if request.user.is_authenticated:
        try:
            # Buscamos el cliente que pertenece al usuario logueado
            cliente_actual = Cliente.objects.get(usuario=request.user)
        except Cliente.DoesNotExist:
            cliente_actual = None
    matcha = Producto.objects.get(nombre='Mochi Matcha')
    cookie = Producto.objects.get(nombre='Mochi Cookie')
    limon = Producto.objects.get(nombre='Mochi Pie de Limon')
    return render(request, 'index.html', {
        'cliente': cliente_actual,
        'Matcha': matcha,
        'Cookie': cookie,
        'Limon': limon,
        'resenas': Resena.objects.all()[:2],
    })

def registrarse(request):
    
    if request.method == 'GET':
        return render(request, 'registrarse.html')
    # Recogemos los 4 datos del formulario HTML
    nombre_usuario = request.POST.get('nombre_usuario')
    correo = request.POST.get('correo')
    contrasena1 = request.POST.get('contrasena1')
    contrasena2 = request.POST.get('contrasena2')

    # Validamos que las contraseñas coincidan
    if contrasena1 != contrasena2:
        return render(request, 'registrarse.html', {
            'error': 'Las contraseñas no coinciden'
        })

    try:
        # Crear usuario de autenticación de Django usando el correo como nombre
        user = User.objects.create_user(username=correo, email=correo, password=contrasena1)
        user.save() #Se usa correo para distinguir el usuario

        # Guardamos los datos en modelo Cliente 
        Cliente.objects.create(
            usuario = user,
            nombre_usuario=nombre_usuario
        )

            #Inicio de sesión automatica
        login(request, user)
        return redirect('index')

    except IntegrityError:
        return render(request, 'registrarse.html', {
            'error': 'Este correo ya está registrado.'
    })


def iniciar_sesion(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        correo = request.POST.get('correo')
        contrasena = request.POST.get('contrasena')
        
        user = authenticate(username=correo, password=contrasena)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return render(request,'iniciar_sesion.html',{
                'error': 'Correo o contraseña incorrectos'},
            )
    return render(request, 'iniciar_sesion.html')


@login_required
def cerrar_sesion(request):
    logout(request)
    return redirect('index')

def productos(request):
    # productos listados
    lista_productos = Producto.objects.all()
    for producto in lista_productos:
        producto.imagen_url = _imagen_producto(producto.imagen)
    return render(request, 'productos.html', {
        'productos': lista_productos
    })

def promociones(request):
    return render(request, 'promociones.html')

def resenas(request):
    if request.method == 'POST':
        form = ResenaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Gracias! Tu reseña quedó publicada.')
            return redirect('resenas')
    else:
        form = ResenaForm()

    return render(request, 'resenas.html', {
        'form': form,
        'resenas': Resena.objects.all(),
    })


#Productos vista unica
def detalle_producto(request, producto_id):
    # Busca el producto por ID o lanza un error 404 si no existe
    producto = get_object_or_404(Producto, id=producto_id)
    producto.imagen_url = _imagen_producto(producto.imagen)
    
   #definir tope de compra
    limite_compra_maximo = 50
    
    #definir el tope en base si el stock es menor o si el limite es menor al stock
    tope_maximo = min(producto.stock, limite_compra_maximo)
    
    return render(request, 'detalle_producto.html', {
        'producto': producto,
        'tope_maximo': tope_maximo
    })
    
def agregar_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto agregado con exito.')
            return redirect('productos')
    else:
        form = ProductoForm()
        
    return render(request, 'crear_producto.html', {
            'form': form,
        })
    
def _imagen_producto(imagen_field):
    """Devuelve la URL del media si existe, o la imagen por defecto de estáticos."""
    # Verificamos si el campo tiene un archivo asociado y existe físicamente
    if not imagen_field:
        return 'img/mochi.png'  # Tu imagen por defecto en static/img/mochi.png
    
    try:
        # Si es un ImageField, .url nos da la ruta web correcta (ej: /media/productos/foto.jpg)
        return imagen_field.url
    except (ValueError, AttributeError):
        return 'img/mochi.png'


@require_POST #evita accesos directo por la url
def agregar_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    try:
        cantidad = int(request.POST.get('cantidad', 1))
    except (TypeError, ValueError):
        cantidad = 1
    if cantidad < 1 or producto.stock < 1:
        messages.error(request, 'La cantidad indicada no es válida o el producto no tiene stock.')
        return redirect('detalle_producto', producto_id=producto.id)

    carrito = request.session.get('carrito', {})
    id_producto = str(producto.id)
    cantidad_actual = int(carrito.get(id_producto, 0))
    if cantidad_actual + cantidad > producto.stock:
        messages.error(request, f'Solo hay {producto.stock} unidades disponibles de {producto.nombre}.')
    else:
        carrito[id_producto] = cantidad_actual + cantidad
        request.session['carrito'] = carrito
        messages.success(request, f'{producto.nombre} se agregó al carrito.')
    return redirect('carrito')


@require_POST
def actualizar_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})
    id_producto = str(producto_id)
    producto = get_object_or_404(Producto, id=producto_id)
    try:
        cantidad = int(request.POST.get('cantidad', 1))
    except (TypeError, ValueError):
        cantidad = 1
    if cantidad <= 0:
        carrito.pop(id_producto, None)
    elif cantidad > producto.stock:
        messages.error(request, f'Solo hay {producto.stock} unidades disponibles de {producto.nombre}.')
    else:
        carrito[id_producto] = cantidad
    request.session['carrito'] = carrito
    return redirect('carrito')


@require_POST
def quitar_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})
    carrito.pop(str(producto_id), None)
    request.session['carrito'] = carrito
    return redirect('carrito')


def carrito(request):
    carrito_sesion = request.session.get('carrito', {})
    items = []
    subtotal = 0
    carrito_actualizado = {}
    for producto in Producto.objects.filter(id__in=carrito_sesion.keys()): #busca en la base de datos los productos id que esta guardados
        cantidad = int(carrito_sesion.get(str(producto.id), 0))
        if cantidad <= 0 or producto.stock <= 0:
            continue
        cantidad = min(cantidad, producto.stock)
        carrito_actualizado[str(producto.id)] = cantidad
        total_item = producto.precio * cantidad
        subtotal += total_item
        items.append({
            'producto': producto,
            'cantidad': cantidad,
            'total': total_item,
            'imagen_url': _imagen_producto(producto.imagen),
        })
    request.session['carrito'] = carrito_actualizado
    request.session['total_carrito'] = subtotal
    return render(request, 'carrito.html', {'items': items, 'subtotal': subtotal, 'total': subtotal})

def get_transaction():
    # retorna la transaccion otorgandole a la clase WebPayOptions todas las credenciales necesarias para ejecutar metodos como:
    #iniciar pago y confirmar pago
    return Transaction(WebpayOptions(
        IntegrationCommerceCodes.WEBPAY_PLUS, 
        IntegrationApiKeys.WEBPAY, 
        IntegrationType.TEST
    ))

def iniciar_pago(request):
    total = int(request.session.get('total_carrito') or 10000)
    
    buy_order = str(uuid.uuid4())[:26]
    session_id = str(uuid.uuid4())[:26]
    return_url = request.build_absolute_uri('/respuesta-pago/')
    
    try:
        tx = get_transaction()
        response = tx.create(buy_order, session_id, total, return_url) #envia peticion a transbank
        
        # Como response es un diccionario, accedemos con corchetes ['url'] y ['token']
        return render(request, 'redirect_webpay.html', {
            'url': response['url'],
            'token': response['token']
        })
    except Exception as e: 
        return render(request, 'pago_fallido.html', {'error': str(e)})

@csrf_exempt
def respuesta_pago(request):
    token = request.POST.get('token_ws') or request.GET.get('token_ws')
    
    if not token:
        return render(request, 'pago_fallido.html', {'error': 'No se encontró el token de la transacción.'})
    
    try:
        tx = get_transaction()
        response = tx.commit(token) #respuesta de si el pago fue autorizado o rechazado
        
        # Usamos .get('status') de forma segura ya que response es un diccionario
        status = response.get('status') if isinstance(response, dict) else getattr(response, 'status', None)
        
        if status == 'AUTHORIZED':
            # 1. Descontar stock y limpiar carrito tras compra exitosa
            carrito_sesion = request.session.get('carrito', {})
            for producto_id, cantidad in carrito_sesion.items():
                try:
                    producto = Producto.objects.get(id=int(producto_id))
                    if producto.stock >= cantidad:
                        producto.stock -= cantidad
                        producto.save()
                except Producto.DoesNotExist:
                    pass
            
            # 2. Limpiar variables de sesión de la compra
            request.session['carrito'] = {}
            if 'total_carrito' in request.session:
                del request.session['total_carrito']
                
            return render(request, 'pago_exitoso.html', {'response': response})
        else:
            return render(request, 'pago_fallido.html', {'response': response})
    
    except Exception as e:
        return render(request, 'pago_fallido.html', {'error': str(e)})
    
def agendamiento_especial(request):
    if request.method == 'POST':
        form = SolicitudEspecialForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tu solicitud de agendamiento fue enviada.')
            return redirect('agendamiento_especial')
    else:
        form = SolicitudEspecialForm()

    return render(request, 'agendamiento_especial.html', {
        'form': form,
    })

def buzon_pedidos_sugerencias(request):
    if request.method == 'POST':
        form = MensajeBuzonForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tu mensaje fue enviado. ¡Gracias por escribirnos!')
            return redirect('buzon_pedidos_sugerencias')
    else:
        form = MensajeBuzonForm()

    return render(request, 'buzon_pedidos_sugerencias.html', {
        'form': form,
    })
