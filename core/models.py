from django.db import models
from django.contrib.auth.models import User

class CursedWordsModel(models.Model):
    id_user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    word = models.CharField('Palavra_Proibida', max_length=100)
    substitute_word = models.CharField('Palavra_Substituta', max_length=100)