from django import forms

class RegisterForm(forms.Form):
    usuario = forms.CharField(label="Usuário", max_length=100)
    email = forms.EmailField(label="email", max_length=100)
    senha = forms.CharField(widget=forms.PasswordInput)
    menor_de_idade = forms.BooleanField(label='Menor de idade?', required=False)
    
class CursedWordsForm(forms.Form):
    word = forms.CharField(label="Palavra proibida", max_length=100)
    substitute_word = forms.CharField(label="Palavra substituta", max_length=100)

class ProxyURLForm(forms.Form):
    url = forms.URLField(label="URL")