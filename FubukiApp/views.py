from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect 
from django.db import IntegrityError
from django.contrib.auth.models import User
from .models import Cliente

# Create your views here.
def index(request):
    return render(request, 'index.html')

def registrarse(request):
    if request.method == 'GET':
        return render(request, 'registrarse.html')
    else:
        # Recogemos los 3 datos del formulario HTML
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
            user.save()

            # Guardamos los datos en modelo Cliente 
            Cliente.objects.create(
                nombre_usuario=nombre_usuario,
                correo=correo,
                contrasena=contrasena1 
            )

            #Inicio de sesión automatica
            login(request, user)
            return redirect('index')

        except IntegrityError:
            return render(request, 'registrarse.html', {
                'error': 'Este correo ya está registrado.'
            })
   

def productos(request):
    return render(request, 'productos.html')