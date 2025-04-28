from django.shortcuts import render, redirect

# from django.contrib.auth import login, authenticate

# from django.contrib.auth.forms import AuthenticationForm

from thing.models import Category, Thing

from .forms import SignupForm


def index(request):
    things = Thing.objects.filter(is_sold=False)[0:6]
    categories = Category.objects.all()
    return render(request, 'core/index.html', {
        'categories': categories,
        'things': things,
    })


def contact(request):
    return render(request, 'core/contact.html')


def signup(request):
    form = SignupForm()

    return render(request, 'core/signup.html', {
        'form': form
    })
