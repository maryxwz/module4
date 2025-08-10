from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Direct, DirectMessage

@login_required
def inbox(request):
    directs = Direct.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    ).order_by('-created_at')

    for chat in directs:
        chat.other = chat.get_receiver(request.user)

    return render(request, 'direct/inbox.html', {'directs': directs})

@login_required
def thread(request, direct_id):
    direct = get_object_or_404(Direct, id=direct_id)
    if request.user not in (direct.user1, direct.user2):
        return redirect('direct:inbox')

    messages = DirectMessage.objects.filter(direct=direct).order_by('created_at')
    other = direct.get_receiver(request.user)
    return render(request, 'direct/thread.html', {
        'direct': direct,
        'messages': messages,
        'other': other,
    })
