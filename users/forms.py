# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserRegisterForm(UserCreationForm):
    # Добавляем поле email, делаем его обязательным
    email = forms.EmailField()

    class Meta:
        # Указываем, что форма работает с моделью User
        model = User
        # Поля, которые будут отображаться в форме
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        # Вызываем родительский конструктор
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        # Применяем стили Bootstrap к полям формы для красивого отображения
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        # Поля для пароля (password1 и password2) уже есть в базовом классе UserCreationForm
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].label = "Пароль"
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].label = "Подтверждение пароля"