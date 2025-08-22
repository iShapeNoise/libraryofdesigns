from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.contrib import messages
from .models import ForumCategory, Topic, Post
from .forms import NewTopicForm, PostForm


def forum_index(request):
    categories = ForumCategory.objects.filter(parent=None).prefetch_related('children')
    return render(request, 'forum/index.html', {'categories': categories})


def category_view(request, pk):
    category = get_object_or_404(ForumCategory, pk=pk)
    topics = category.topics.select_related('created_by').prefetch_related('posts')

    paginator = Paginator(topics, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'forum/category.html', {
        'category': category,
        'topics': page_obj,
        'page_obj': page_obj
    })


def topic_view(request, pk):
    topic = get_object_or_404(Topic, pk=pk)
    topic.views += 1
    topic.save(update_fields=['views'])

    posts = topic.posts.select_related('created_by')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == 'POST' and request.user.is_authenticated:
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()
            messages.success(request, 'Your reply has been posted.')
            return redirect('forum:topic', pk=topic.pk)
    else:
        form = PostForm()

    return render(request, 'forum/topic.html', {
        'topic': topic,
        'posts': page_obj,
        'page_obj': page_obj,
        'form': form
    })


@login_required
def new_topic(request, category_pk):
    category = get_object_or_404(ForumCategory, pk=category_pk)

    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.category = category
            topic.created_by = request.user
            topic.save()

            # Create first post
            Post.objects.create(
                topic=topic,
                created_by=request.user,
                content=form.cleaned_data['content']
            )

            messages.success(request, 'Your topic has been created.')
            return redirect('forum:topic', pk=topic.pk)
    else:
        form = NewTopicForm()

    return render(request, 'forum/new_topic.html', {
        'category': category,
        'form': form
    })
