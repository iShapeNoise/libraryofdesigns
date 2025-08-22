from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from design.models import Design
from core.views import get_design_images


@login_required
def index(request):
    designs = Design.objects.filter(created_by=request.user)

    # Add first image to each design object (same as homepage)  
    for design in designs:
        design_images = get_design_images(design)
        design.first_image = design_images[0] if design_images else None

    return render(request, 'dashboard/index.html', {
        'designs': designs,
    })
