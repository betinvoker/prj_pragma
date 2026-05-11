from django.forms import ModelForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Client, CatalogItem, Document


class ClientForm(ModelForm):
    class Meta:
        model = Client
        fields = ["name", "last_name", "first_name", "patronymic", "company", "email", "phone", "address"]
        labels = {
            "name": "Наименование (логин)",
            "last_name": "Фамилия",
            "first_name": "Имя",
            "patronymic": "Отчество",
            "company": "Название компании",
            "email": "Email",
            "phone": "Номер телефона",
            "address": "Юридический адрес",
        }


class CatalogItemForm(ModelForm):
    class Meta:
        model = CatalogItem
        fields = ["name", "description", "price", "stock", "image"]
        labels = {
            "name": "Название товара",
            "description": "Описание",
            "price": "Цена",
            "stock": "Количество на складе",
            "image": "Изображение",
        }


class ClientProfileForm(ModelForm):
    class Meta:
        model = Client
        fields = ["name", "last_name", "first_name", "patronymic", "company", "email", "phone", "address"]
        labels = {
            "name": "Наименование (логин)",
            "last_name": "Фамилия",
            "first_name": "Имя",
            "patronymic": "Отчество",
            "company": "Название компании",
            "email": "Email",
            "phone": "Номер телефона",
            "address": "Юридический адрес",
        }

class ClientSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class DocumentForm(ModelForm):
    class Meta:
        model = Document
        fields = ["title", "doc_type", "client", "order", "file"]
        labels = {
            "title": "Название документа",
            "doc_type": "Тип документа",
            "client": "Клиент",
            "order": "Заказ",
            "file": "Файл",
        }
