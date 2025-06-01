from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from design.models import Design


@login_required
def index(request):
    designs = Design.objects.filter(created_by=request.user)

    return render(request, 'dashboard/index.html', {
        'designs': designs,
    })

