from django import forms

from .models import MensajeBuzon, Resena, SolicitudEspecial


class ResenaForm(forms.ModelForm):
    class Meta:
        model = Resena
        fields = ['nombre', 'calificacion', 'comentario']
        labels = {
            'nombre': 'Tu nombre',
            'calificacion': 'Calificación',
            'comentario': 'Tu reseña',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '¿Cómo te llamas?',
                'autocomplete': 'name',
            }),
            'calificacion': forms.Select(attrs={'class': 'form-select'}),
            'comentario': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Cuéntanos cómo fue tu experiencia',
            }),
        }

class SolicitudEspecialForm(forms.ModelForm):
    class Meta:
        model = SolicitudEspecial
        fields = [
            'nombre',
            'correo',
            'producto',
            'cantidad',
            'fecha_deseada',
            'comentarios',
        ]
        labels = {
            'nombre': 'Tu nombre',
            'correo': 'Tu correo',
            'producto': 'Producto',
            'cantidad': 'Cantidad (más de 50)',
            'fecha_deseada': 'Fecha deseada',
            'comentarios': 'Comentarios',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'cantidad': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 51,
            }),
            'fecha_deseada': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'comentarios': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
            }),
        }

    def clean_cantidad(self):
        cantidad = self.cleaned_data['cantidad']
        if cantidad <= 50:
            raise forms.ValidationError(
                'El agendamiento especial es para pedidos superiores a 50 unidades.'
            )
        return cantidad


class MensajeBuzonForm(forms.ModelForm):
    class Meta:
        model = MensajeBuzon
        fields = ['nombre', 'correo', 'tipo', 'mensaje']
        labels = {
            'nombre': 'Tu nombre',
            'correo': 'Tu correo',
            'tipo': '¿Qué quieres enviar?',
            'mensaje': 'Mensaje',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'autocomplete': 'name',
            }),
            'correo': forms.EmailInput(attrs={
                'class': 'form-control',
                'autocomplete': 'email',
            }),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'mensaje': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Escribe aquí tu pedido o sugerencia',
            }),
        }