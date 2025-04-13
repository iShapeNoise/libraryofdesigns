from django.shortcuts import render

from thing.models import Category, Thing


def index(request):
    things = Thing.objects.filter(is_sold=False)[0:6]
    categories = Category.objects.all()
    return render(request, 'core/index.html', {
        'categories': categories,
        'things': things,
    })


def contact(request):
    return render(request, 'core/contact.html')

