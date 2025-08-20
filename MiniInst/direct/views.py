from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
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
def thread_view(request, direct_id):
    direct = get_object_or_404(Direct, id=direct_id)
    if request.user not in (direct.user1, direct.user2):
        return redirect('direct:inbox')

    other = direct.get_receiver(request.user)

    qs_desc = DirectMessage.objects.filter(direct=direct).select_related('sender').order_by('-created_at')
    per_page = 10
    paginator = Paginator(qs_desc, per_page)
    num_pages = paginator.num_pages or 1

    page_obj = paginator.get_page(1)
    msgs = list(page_obj.object_list)[::-1] 

    return render(request, 'direct/thread.html', {
        'direct': direct,
        'messages': msgs,
        'other': other,
        'current_page': num_pages,
        'num_pages': num_pages,
    })


@login_required
def thread_messages_api(request, direct_id):
    direct = get_object_or_404(Direct, id=direct_id)
    if request.user not in (direct.user1, direct.user2):
        return JsonResponse({'error': 'Not allowed'}, status=403)

    qs_desc = DirectMessage.objects.filter(direct=direct).select_related('sender').order_by('-created_at')
    per_page = 10
    paginator = Paginator(qs_desc, per_page)
    num_pages = paginator.num_pages or 1

    try:
        client_page = int(request.GET.get('page', num_pages))
    except (ValueError, TypeError):
        client_page = num_pages

    internal_page = num_pages - client_page + 1
    if internal_page < 1 or internal_page > num_pages:
        return JsonResponse({'messages': [], 'page': client_page, 'num_pages': num_pages})

    page_obj = paginator.get_page(internal_page)
    msgs = list(page_obj.object_list)[::-1] 

    data = [{
        'id': str(m.id),
        'message': m.message,
        'sender_id': m.sender.id,
        'sender_username': m.sender.username,
        'created_at': m.created_at.isoformat(),
        'created_time': m.created_at.strftime('%H:%M'),
    } for m in msgs]

    return JsonResponse({'messages': data, 'page': client_page, 'num_pages': num_pages})