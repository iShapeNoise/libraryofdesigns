from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from design.models import Design
from .forms import ConversationMessageForm
from .models import Conversation


@login_required
def new_conversation(request, design_pk):
    design = get_object_or_404(Design, pk=design_pk)

    if design.created_by == request.user:
        return redirect('dashboard:index')

    conversations = Conversation.objects.filter(design=design).filter(members__in=[request.user.id])

    if conversations:
        return redirect('conversation:detail', pk=conversations.first().id)

    if request.method == 'POST':
        form = ConversationMessageForm(request.POST)

        if form.is_valid():
            conversation = Conversation.objects.create(design=design)
            conversation.members.add(request.user)
            conversation.members.add(design.created_by)
            conversation.save()

            conversation_message = form.save(commit=False)
            conversation_message.conversation = conversation
            conversation_message.created_by = request.user
            conversation_message.save()

            return redirect('design:detail', pk=design_pk)

    else:
        form = ConversationMessageForm()

    return render(request, 'conversation/new.html', {
        'form': form
    })


@login_required
def inbox(request):
    conversations = Conversation.objects.filter(members__in=[request.user.id])

    return render(request, 'conversation/inbox.html', {
        'conversations': conversations
    })


@login_required
def detail(request, pk):
    conversation = Conversation.objects.filter(members__in=[request.user.id]).get(pk=pk)

    if request.method == 'POST':
        form = ConversationMessageForm(request.POST)

        if form.is_valid():
            conversation_message = form.save(commit=False)
            conversation_message.conversation = conversation
            conversation_message.created_by = request.user
            conversation_message.save()

            conversation.save()

            return redirect('conversation:detail', pk=pk)
    else:
        form = ConversationMessageForm()

    return render(request, 'conversation_detail.html', {
        'conversation': conversation,
        'form': form
    })

