# direct/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Direct, DirectMessage
from users.models import CustomUser

# @login_required
def inbox(request):
    directs = Direct.objects.filter(
        user1=request.user
    ) | Direct.objects.filter(
        user2=request.user
    )
    directs = directs.order_by('-created_at')
    return render(request, 'direct/inbox.html', {
        'directs': directs
    })

# @login_required
def thread(request, direct_id):
    direct = get_object_or_404(Direct, id=direct_id)
    if request.user not in [direct.user1, direct.user2]:
        return redirect('direct:inbox')

    messages = DirectMessage.objects.filter(direct=direct).order_by('created_at')
    other = direct.get_receiver(request.user)
    return render(request, 'direct/thread.html', {
        'direct': direct,
        'messages': messages,
        'other': other,
    })
