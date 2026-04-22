from django import forms
from .models import Caja, Banco, MonedaExtranjera, ValorADepositar, PlazoFijo, FCI, TituloON

class CajaForm(forms.ModelForm):
    class Meta:
        model = Caja
        fields = ['empresa', 'saldo']
        widgets = {
            'empresa': forms.Select(attrs={'class': 'form-select'}),
            'saldo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class BancoForm(forms.ModelForm):
    class Meta:
        model = Banco
        fields = ['nombre', 'saldo_cuenta_corriente',
                  'cheque_pendiente_acreditar', 'cheque_pendiente_debito', 'saldo_usd']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'saldo_cuenta_corriente': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cheque_pendiente_acreditar': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cheque_pendiente_debito': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'saldo_usd': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class MonedaExtranjeraForm(forms.ModelForm):
    class Meta:
        model = MonedaExtranjera
        fields = ['empresa', 'saldo_dolares']
        widgets = {
            'empresa': forms.Select(attrs={'class': 'form-select'}),
            'saldo_dolares': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class ValorADepositarForm(forms.ModelForm):
    class Meta:
        model = ValorADepositar
        fields = ['empresa', 'mes_vencimiento', 'anio_vencimiento', 'monto']
        widgets = {
            'empresa': forms.Select(attrs={'class': 'form-select'}),
            'mes_vencimiento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: MARZO'}),
            'anio_vencimiento': forms.NumberInput(attrs={'class': 'form-control'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class PlazoFijoForm(forms.ModelForm):
    class Meta:
        model = PlazoFijo
        fields = ['banco', 'monto_invertido', 'fecha_constitucion',
                  'fecha_vencimiento', 'interes']
        widgets = {
            'banco': forms.TextInput(attrs={'class': 'form-control'}),
            'monto_invertido': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'fecha_constitucion': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'interes': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class FCIForm(forms.ModelForm):
    class Meta:
        model = FCI
        fields = ['nombre', 'banco', 'cuotapartes', 'saldo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'banco': forms.TextInput(attrs={'class': 'form-control'}),
            'cuotapartes': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'saldo': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class TituloONForm(forms.ModelForm):
    class Meta:
        model = TituloON
        fields = ['nombre', 'tipo', 'ticker', 'cuotapartes_actual']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'ticker': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: BYCH (ON) o TX26 (Bono)'}),
            'cuotapartes_actual': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
        }