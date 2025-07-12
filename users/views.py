# users/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from .forms import UserRegisterForm

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Аккаунт для {user.username} успешно создан! Вы вошли в систему.')
            return redirect('ad_list') # Имя 'ad_list' все еще доступно глобально
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})