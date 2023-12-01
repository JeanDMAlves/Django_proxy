from django.contrib import admin
from django.urls import path, include
from .views import register, index, cursed_word, show_cursed_words, proxy, redirect_proxy

urlpatterns = [
    path('', index, name='index'),
    path('register/', register, name='register'),
    path('words/', cursed_word, name='cursed_word'),
    path('list-words/', show_cursed_words, name='list_words'),
    path('proxy/', proxy, name='proxy'),
    path('redirect_proxy/', redirect_proxy, name="redirect_proxy"),
]
