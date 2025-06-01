from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from .forms import NewThingForm, EditThingForm
from .models import Thing, Category


def things(request):
    query = request.GET.get('query', '')
    category_id = request.GET.get('category', 0)
    categories = Category.objects.all()
    things = Thing.objects.filter()

    if category_id:
        things = things.filter(category_id=category_id)

    if query:
        things = things.filter(Q(name__icontains=query) |
                               Q(description__icontains=query))

    return render(request, 'thing/things.html', {
        'things': things,
        'query': query,
        'categories': categories,
        'category_id': int(category_id),
    })


def detail(request, pk):
    thing = get_object_or_404(Thing, pk=pk)
    related_things = Thing.objects.filter(category=thing.category)
    related_things.exclude(pk=pk)[0:3]

    return render(request, 'thing/detail.html', {
        'thing': thing,
        'related_things': related_things,
    })


@login_required
def new(request):
    if request.method == 'POST':
        form = NewThingForm(request.POST, request.FILES)

        if form.is_valid():
            thing = form.save(commit=False)
            thing.created_by = request.user
            thing.save()
            return redirect('thing:detail', pk=thing.id)
    else:
        form = NewThingForm()

    return render(request, 'thing/form.html', {
        'form': form,
        'title': 'New thing',
    })


@login_required
def edit(request, pk):
    thing = get_object_or_404(Thing, pk=pk, created_by=request.user)
    if request.method == 'POST':
        form = EditThingForm(request.POST, request.FILES, instance=thing)

        if form.is_valid():
            thing = form.save(commit=False)
            thing.created_by = request.user
            thing.save()
            return redirect('thing:detail', pk=thing.id)
    else:
        form = EditThingForm(instance=thing)

    return render(request, 'thing/form.html', {
        'form': form,
        'title': 'New thing',
    })


@login_required
def delete(request, pk):
    thing = get_object_or_404(Thing, pk=pk, created_by=request.user)
    thing.delete()

    return redirect('dashboard:index')
