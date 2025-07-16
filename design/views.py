from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from .forms import NewDesignForm, EditDesignForm
from .models import Design, Category


def designs(request):
    query = request.GET.get('query', '')
    category_id = request.GET.get('category', 0)
    categories = Category.objects.all()
    designs = Design.objects.filter()

    if category_id:
        designs = designs.filter(category_id=category_id)

    if query:
        designs = designs.filter(Q(name__icontains=query) |
                                 Q(description__icontains=query))

    return render(request, 'design/designs.html', {
        'designs': designs,
        'query': query,
        'categories': categories,
        'category_id': int(category_id),
    })


def detail(request, pk):
    design = get_object_or_404(Design, pk=pk)
    related_designs = Design.objects.filter(category=design.category)
    related_designs.exclude(pk=pk)[0:3]

    return render(request, 'design/detail.html', {
        'design': design,
        'related_designs': related_designs,
    })


@login_required
def new(request):
    if request.method == 'POST':
        form = NewDesignForm(request.POST, request.FILES)

        if form.is_valid():
            design = form.save(commit=False)
            design.created_by = request.user
            design.save()
            return redirect('design:detail', pk=design.id)
        # If form is invalid, fall through to render the form with errors
    else:
        form = NewDesignForm()

    return render(request, 'design/form.html', {
        'form': form,
        'title': 'New Design',
    })


@login_required
def edit(request, pk):
    design = get_object_or_404(Design, pk=pk, created_by=request.user)
    if request.method == 'POST':
        form = EditDesignForm(request.POST, request.FILES, instance=design)

        if form.is_valid():
            design = form.save(commit=False)
            design.created_by = request.user
            design.save()
            return redirect('design:detail', pk=design.id)
    else:
        form = EditDesignForm(instance=design)

    return render(request, 'design/form.html', {
        'form': form,
        'title': 'New Design',
    })


@login_required
def delete(request, pk):
    design = get_object_or_404(Design, pk=pk, created_by=request.user)
    design.delete()

    return redirect('dashboard:index')
