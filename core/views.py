from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import HttpResponse
from django.template import Template
from .forms import RegisterForm, CursedWordsForm, ProxyURLForm
from .models import CursedWordsModel
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse, urljoin, urlunparse

def index(request):
    if request.user.is_authenticated:
        return redirect('redirect_proxy')
    else:
        return render(request, 'index.html')

def register(request):
    form = RegisterForm(request.POST or None) 
    if str(request.method) == 'POST':
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data["usuario"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["senha"],
                first_name=form.cleaned_data["menor_de_idade"] # underage
            )        
            print(dir(user))
            print(user.first_name)
            print(type(user.first_name))
            return redirect('login')
    else:
        context = {
            'form':form
        }
        return render(request, 'register.html', context)

def logout_view(request):
    logout(request)
    return redirect('index')

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
    print(dir(request.session))
    print(request.session.values)
    id_user = request.user.id
    cursed_words = CursedWordsModel.objects.filter(id_user=id_user)
    context = {
        'words': cursed_words
    }
    return render(request, 'list_of_words.html', context=context)

@login_required
def redirect_proxy(request):
    form = ProxyURLForm(request.POST or None)
    context = {
        'form':form
    }
    if str(request.method) == 'POST':
        if form.is_valid():
            url = form.cleaned_data["url"]
            return redirect(f'http://127.0.0.1:8000/proxy?url={url}')
    else:
        return render(request, 'proxy.html', context)
    

@login_required
def proxy(request):
    if str(request.method) == 'GET':
        url = request.GET.get('url', '')
        request_html = requests.get(url)
        soup = BeautifulSoup(request_html.text, features="html.parser")
        html = apply_proxy_word_filter(soup=soup, user=request.user, url=url)
        html = change_anchors_to_proxy(soup=soup, url=url)
        return HttpResponse(str(html))
    else:
        return redirect('redirect_proxy')

def change_anchors_to_proxy(soup, url):
    parsed_url = urlparse(url)
    base_url = urlunparse((parsed_url.scheme, parsed_url.netloc, '', '', '', ''))
    for anchor in soup.find_all('a', href=True):
        anchor_url = anchor['href']
        absolute_url = urljoin(base_url, anchor_url)
        anchor['href'] = f'http://127.0.0.1:8000/proxy?url={absolute_url}'
    return soup

def apply_proxy_word_filter(soup: str, user, url: str) -> BeautifulSoup:
    # https://www.digitalocean.com/community/tutorials/getting-started-with-python-requests-get-requests
    # https://docs.docker.com/language/python/containerize/
    
    if (user.first_name == 'True'): # Verifica se o usuário é menor de idade para aplicar o filtro
        cursed_words = {
            word.word:word.substitute_word for word in CursedWordsModel.objects.filter(id_user=user.id)
        }
        
        for word, substitute_word in cursed_words.items():
        # Encontrar todas as ocorrências da palavra proibida
            for element in soup.find_all(text=lambda text: text and word in text):
                # Substituir a palavra proibida pelo texto alternativo
                new_content = element.replace_with(str(element).replace(word, substitute_word))        
    
    parsed_url = urlparse(url)
    base_url = urlunparse((parsed_url.scheme, parsed_url.netloc, '', '', '', ''))

    for link in soup.find_all('img', src=True):
        asset_url = link['src']
        absolute_url = urljoin(base_url, asset_url)
        link['src'] = absolute_url
        
    for link in soup.find_all('link', href=True): # css
        asset_url = link['href']
        absolute_url = urljoin(base_url, asset_url)
        asset_response = requests.get(absolute_url)
        content_type = asset_response.headers.get('content-type', '').split(';')[0].strip()
        if content_type == 'text/css':
            new_tag = soup.new_tag('style', type='text/css')
            new_tag.string = asset_response.text
            link.replace_with(new_tag)
        if content_type == 'text/javascript':
            new_tag = soup.new_tag('script', type='text/javascript')
            new_tag.string = asset_response.text
            link.i.replace_with(new_tag)    
    
    for link in soup.find_all('script', src=True): # js    
        asset_url = link['src']
        absolute_url = urljoin(base_url, asset_url)
        link['src'] = absolute_url
        link['crossorigin'] = True
    
    # for link in soup.find_all('script', src=True): # js    
    #     asset_url = link['src']
    #     absolute_url = urljoin(base_url, asset_url)
    #     asset_response = requests.get(absolute_url)
    #     # content_type = asset_response.headers.get('content-type', '').split(';')[0].strip()
    #     # if content_type == 'text/javascript':
    #     try:
    #         # new_tag = soup.new_tag('script', type='text/javascript')
    #         # new_tag.string = asset_response.text
    #         # new_tag['src'] = ''
    #         # new_tag['href'] = ''
            
    #         link.string = asset_response.text
    #         # link.i.replace_with(new_tag)    
    #     except:
    #         link['src'] = ''
    #         link['href'] = ''
    
    return soup
