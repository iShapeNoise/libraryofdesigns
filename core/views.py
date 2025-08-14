from django.shortcuts import render, redirect, get_object_or_404
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
from django.core.paginator import Paginator
from .models import UserProfile
# for debugging
import logging
logger = logging.getLogger(__name__)


def get_design_images(design):
    """Get list of images from the design's organized directory structure"""
    import os
    from django.conf import settings

    try:
        category_path = design.category.get_full_path().replace(' > ', '/').replace(' ', '_')
        design_name_fs = design.name.replace(' ', '_')
        images_dir = os.path.join(settings.LOD_CONTENT_URL, 'designs', category_path, design_name_fs, 'images')
        image_files = []

        if os.path.exists(images_dir):
            for filename in os.listdir(images_dir):
                if filename.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    image_url = os.path.join(images_dir, filename)
                    image_files.append({
                        'filename': filename,
                        'url': image_url
                    })
        logger.debug(f"Looking for images in: {images_dir}")
        logger.debug(f"Looking for image url: {image_url}")

        return image_files

    except Exception as e:
        print(f"Error in get_design_images: {e}")
        return []


def index(request):
    designs = Design.objects.filter(is_modified=False)[0:6]
    categories = Category.objects.filter(parent__isnull=True)

    # Add first image to each design object directly
    for design in designs:
        design_images = get_design_images(design)
        design.first_image = design_images[0] if design_images else None

    return render(request, 'core/index.html', {
        'categories': categories,
        'designs': designs,  # Keep the original variable name  
    })


def browse_categories(request, category_id=None):
    if category_id:
        current_category = get_object_or_404(Category, id=category_id)
        categories = current_category.get_children()
        breadcrumbs = current_category.get_ancestors(include_self=True)
        # Get designs for this category, excluding placeholder images
        designs_queryset = Design.objects.filter(category=current_category).exclude(image='No image provided')

        # Add pagination
        paginator = Paginator(designs_queryset, 25)  # 25 designs per page
        page_number = request.GET.get('page')
        designs = paginator.get_page(page_number)
    else:
        current_category = None
        categories = Category.objects.filter(parent__isnull=True)
        breadcrumbs = []
        designs = Design.objects.none()  # No designs at root level

    return render(request, 'core/browse_categories.html', {
        'categories': categories,
        'current_category': current_category,
        'breadcrumbs': breadcrumbs,
        'designs': designs,
        'is_paginated': designs.has_other_pages() if hasattr(designs, 'has_other_pages') else False,
        'page_obj': designs if hasattr(designs, 'has_other_pages') else None,
    })


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '<p class="success_login">You were successfully login</p>')
            return redirect('core:contact')
    else:
        form = ContactForm()

    return render(request, 'core/contact.html', {
            'form': form
        })


def logout_user(request):
    designs = Design.objects.filter(is_modified=False)[0:6]
    categories = Category.objects.all().filter(parent__isnull=True)
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
            messages.success(request, '<p class="success_signup">Account created successfully! Please log in.<(p>')
        return redirect('/login/')
    else:
        form = SignupForm()

    return render(request, 'core/signup.html', {
        'form': form
    })


def license(request):
    path = os.path.join(str(settings.LOD_CONTENT_ROOT), 'LICENSE.md')
    text = ''
    with open(path, 'r', encoding="utf-8") as f:
        text = f.read()
    html_code = markdown.markdown(text)
    context = {
        'html_code': html_code,
    }
    return render(request, 'core/license.html', context)


def terms_of_use(request):
    path = os.path.join(str(settings.LOD_CONTENT_ROOT), 'TERMS_OF_USE.md')
    text = ''
    with open(path, 'r', encoding="utf-8") as f:
        text = f.read()
    html_code = markdown.markdown(text)
    context = {
        'html_code': html_code,
    }
    return render(request, 'core/terms_of_use.html', context)


def about_lod(request):
    path = os.path.join(str(settings.LOD_CONTENT_ROOT), 'about', 'ABOUT.md')
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

    # Initialize both forms at the start  
    profile_form = ProfileForm(instance=profile, user=request.user)
    password_form = PasswordChangeForm()

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
            # Keep password_form initialized for template rendering  

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
            # Keep profile_form initialized for template rendering  

    return render(request, 'core/profile_settings.html', {
        'profile_form': profile_form,
        'password_form': password_form,
        'profile': profile
    })
