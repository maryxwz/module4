from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Direct, DirectMessage, GroupChat, GroupMessage



@login_required
def inbox(request):
    directs_qs = Direct.objects.filter(
        Q(user1=request.user) | Q(user2=request.user)
    ).order_by('-created_at')

    directs = []
    for chat in directs_qs:
        other = chat.get_receiver(request.user) 
        directs.append({
            'kind': 'direct',
            'id': chat.id,
            'title': other.username,
            'other': other,
            'created_at': chat.created_at,
        })

    groups_qs = GroupChat.objects.filter(members=request.user).order_by('-created_at')
    groups = []
    for g in groups_qs:
        groups.append({
            'kind': 'group',
            'id': g.id,
            'title': g.name or 'Груповий чат',
            'group': g,
            'created_at': g.created_at,
        })
    conversations = sorted(directs + groups, key=lambda x: x['created_at'] or 0, reverse=True)
    return render(request, 'direct/inbox.html', {'conversations': conversations})


@login_required
def thread_view(request, kind, chat_id):
    if kind not in ('direct', 'group'):
        return redirect('direct:inbox')

    if kind == 'direct':
        direct = get_object_or_404(Direct, id=chat_id)
        if request.user not in (direct.user1, direct.user2):
            return redirect('direct:inbox')
        other = direct.get_receiver(request.user)  
        qs_desc = DirectMessage.objects.filter(direct=direct).select_related('sender').order_by('-created_at')

        context_obj = direct
    else:  
        group = get_object_or_404(GroupChat, id=chat_id)
        if not group.members.filter(pk=request.user.pk).exists():
            return redirect('direct:inbox')
        other = group.name or 'Group chat'
        qs_desc = GroupMessage.objects.filter(group_chat=group).select_related('sender').order_by('-created_at')

        context_obj = group

    per_page = 10
    paginator = Paginator(qs_desc, per_page)
    num_pages = paginator.num_pages or 1
    page_obj = paginator.get_page(1)
    msgs = list(page_obj.object_list)[::-1]  

    return render(request, 'direct/thread.html', {
        'kind': kind,
        'chat': context_obj,
        'messages': msgs,
        'other': other,
        'current_page': num_pages,
        'num_pages': num_pages,
    })



@login_required
def thread_messages_api(request, kind, chat_id):
    if kind == 'direct':
        direct = get_object_or_404(Direct, id=chat_id)
        if request.user not in (direct.user1, direct.user2):
            return JsonResponse({'error': 'Not allowed'}, status=403)
        qs_desc = DirectMessage.objects.filter(direct=direct).select_related('sender').order_by('-created_at')

    elif kind == 'group':
        group = get_object_or_404(GroupChat, id=chat_id)
        if not group.members.filter(pk=request.user.pk).exists():
            return JsonResponse({'error': 'Not allowed'}, status=403)
        qs_desc = GroupMessage.objects.filter(group_chat=group).select_related('sender').order_by('-created_at')

    else:
        return JsonResponse({'error': 'Bad kind'}, status=400)

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