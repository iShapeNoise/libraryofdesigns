from django.shortcuts import render, redirect

# from django.contrib.auth import login, authenticate

# from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from design.models import Category, Design
from django.contrib.auth import logout
from .forms import SignupForm, ContactForm
from django.conf import settings
import os
import markdown


def index(request):
    designs = Design.objects.filter(is_modified=False)[0:6]
    categories = Category.objects.all()
    return render(request, 'core/index.html', {
        'categories': categories,
        'designs': designs,
    })


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request,'Your message has been sent sucessfully!')
            return redirect('core:contact')
    else:
        form = ContactForm()

    return render(request, 'core/contact.html', {
            'form': form
        })


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


def license(request):
    path = os.path.join(str(settings.MEDIA_ROOT), 'LICENSE.md')
    text = ''
    with open(path, 'r', encoding="utf-8") as f:
        text = f.read()
    html_code = markdown.markdown(text)
    context = {
        'html_code': html_code,
    }
    return render(request, 'core/license.html', context)


def terms_of_use(request):
    path = os.path.join(str(settings.MEDIA_ROOT), 'TERMS_OF_USE.md')
    text = ''
    with open(path, 'r', encoding="utf-8") as f:
        text = f.read()
    html_code = markdown.markdown(text)
    context = {
        'html_code': html_code,
    }
    return render(request, 'core/terms_of_use.html', context)


def about_lod(request):
    path = os.path.join(str(settings.MEDIA_ROOT), 'README.md')
    text = ''
    with open(path, 'r', encoding="utf-8") as f:
        text = f.read()
    html_code = markdown.markdown(text)
    context = {
        'html_code': html_code,
    }
    return render(request, 'core/about.html', context)
