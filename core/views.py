from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import Template
from .forms import RegisterForm, CursedWordsForm, ProxyURLForm
from .models import CursedWordsModel
from bs4 import BeautifulSoup
import requests

def index(request):
    return render(request, 'index.html')

def register(request):
    form = RegisterForm(request.POST or None) 
    if str(request.method) == 'POST':
        if form.is_valid():
            user = User.objects.create_user(
                form.cleaned_data["usuario"],
                form.cleaned_data["email"],
                form.cleaned_data["senha"]
            )        
            return redirect('login')
    else:
        context = {
            'form':form
        }
        return render(request, 'register.html', context)

@login_required
def cursed_word(request):
    form = CursedWordsForm(request.POST or None)
    
    context = {
        'form':form
    }
    
    if str(request.method) == 'POST':
        if form.is_valid():
            user = request.user
            word = form.cleaned_data["word"]
            substitute_word = form.cleaned_data["substitute_word"]
            cursedWord = CursedWordsModel(id_user = user, word = word, substitute_word=substitute_word)
            cursedWord.save()
            form.clean()
    
    return render(request, 'cursed_words.html', context)

@login_required
def show_cursed_words(request):
    id_user = request.user.id
    cursed_words = CursedWordsModel.objects.filter(id_user=id_user)
    context = {
        'words': cursed_words
    }
    return render(request, 'list_of_words.html', context=context)

@login_required
def proxy(request):
    form = ProxyURLForm(request.POST or None)
    context = {
        'form':form
    }
    if str(request.method) == 'POST':
        if form.is_valid():
            cursed_words = {
                word.word:word.substitute_word for word in CursedWordsModel.objects.filter(id_user=request.user.id)
            }
            url = form.cleaned_data["url"]
            html = BeautifulSoup(requests.get(url).text, features="html.parser")
            for word in cursed_words.keys():
                palavra = html.find(text=word)
                if palavra != None: 
                    html.find(text=word).replaceWith(cursed_words[word])
            return HttpResponse(html)
    return render(request, 'proxy.html', context)
