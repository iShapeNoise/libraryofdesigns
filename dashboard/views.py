from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from thing.models import Thing


@login_required
def index(request):
    things = Thing.objects.filter(created_by=request.user)

    return render(request, 'dashboard/index.html', {
        'things': things,
    })

