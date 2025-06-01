from django.shortcuts import render, redirect

# from django.contrib.auth import login, authenticate

# from django.contrib.auth.forms import AuthenticationForm

from design.models import Category, Design
from django.contrib.auth import logout
from .forms import SignupForm


def index(request):
    designs = Design.objects.filter(is_modified=False)[0:6]
    categories = Category.objects.all()
    return render(request, 'core/index.html', {
        'categories': categories,
        'designs': designs,
    })


def contact(request):
    return render(request, 'core/contact.html')


def logout_user(request):
    designs = Design.objects.filter(is_modified=False)[0:6]
    categories = Category.objects.all()
    logout(request)
    return render(request, 'core/index.html', {
        'categories': categories,
        'designs': designs,
    })


def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            # Validate the reCAPTCHA
            form.save()

        return redirect('/login/')
    else:
        form = SignupForm()

    return render(request, 'core/signup.html', {
        'form': form
    })
