from django.shortcuts import render, get_object_or_404

from .models import Thing


def detail(request, pk):
    thing = get_object_or_404(Thing, pk=pk)
    related_things = Thing.objects.filter(category=thing.category,
                                          is_sold=False).exclude(pk=pk)[0:3]

    return render(request, 'thing/detail.html', {
        'thing': thing,
        'related_things': related_things
    })
