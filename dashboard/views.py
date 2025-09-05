from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from design.models import Design
from core.views import get_design_images
from django.core.paginator import Paginator


@login_required
def index(request):
    designs = Design.objects.filter(created_by=request.user)

    # Add first image to each design object (same as homepage)  
    for design in designs:
        design_images = get_design_images(design)
        design.first_image = design_images[0] if design_images else None

    # Paginate with 12 designs per page (3 rows of 4)
    paginator = Paginator(designs, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'dashboard/index.html', {
        'designs': designs,
        'page_obj': page_obj,
    })
