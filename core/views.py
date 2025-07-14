from django.shortcuts import render, redirect
# from django.contrib.auth import login, authenticate
# from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from design.models import Category, Design
from django.contrib.auth import logout
from .forms import SignupForm, ContactForm, ProfileForm, PasswordChangeForm
from django.conf import settings
import os
import markdown
from bs4 import BeautifulSoup
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from .models import UserProfile


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
    path = os.path.join(str(settings.MEDIA_ROOT), 'about', 'ABOUT.md')
    text = ''
    with open(path, 'r', encoding="utf-8") as f:
        text = f.read()
    html_text = markdown.markdown(text)
    path_img = path = os.path.join(str(settings.MEDIA_ROOT), 'about', 'img')
    soup = BeautifulSoup(html_text)
    path_here = os.path.join(str(os.getcwd()), 'templates', 'core')
    img_path = os.path.relpath(path_img, path_here)
    for img in soup.findAll('img'):
        img['src'] = img['src'].replace('img', img_path)
        img['width'] = '80%'
    html_code = str(soup)
#    testpath = os.path.join(path, 'debug.html')
#    with open(testpath, "w") as file:
#        file.write(str(soup))
    context = {
        'html_code': html_code,
    }
    return render(request, 'core/about.html', context)


@login_required
def profile_settings(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = ProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
            if profile_form.is_valid():
                # Update user fields
                request.user.first_name = profile_form.cleaned_data['first_name']
                request.user.last_name = profile_form.cleaned_data['last_name']
                request.user.email = profile_form.cleaned_data['email']
                request.user.save()

                # Update profile
                profile_form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('core:profile_settings')

        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(request.POST)
            if password_form.is_valid():
                old_password = password_form.cleaned_data['old_password']
                new_password1 = password_form.cleaned_data['new_password1']
                new_password2 = password_form.cleaned_data['new_password2']

                if not request.user.check_password(old_password):
                    messages.error(request, 'Current password is incorrect.')
                elif new_password1 != new_password2:
                    messages.error(request, 'New passwords do not match.')
                else:
                    request.user.set_password(new_password1)
                    request.user.save()
                    update_session_auth_hash(request, request.user)
                    messages.success(request, 'Password changed successfully!')
                    return redirect('core:profile_settings')
    else:
        profile_form = ProfileForm(instance=profile, user=request.user)
        password_form = PasswordChangeForm()

    return render(request, 'core/profile_settings.html', {
        'profile_form': profile_form,
        'password_form': password_form,
        'profile': profile
    })
